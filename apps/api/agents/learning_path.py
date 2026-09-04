"""
Shikshak AI — Learning Path Agent.

Single responsibility: break a broad topic into an ordered curriculum of sub-topics
using a lightweight concept-dependency graph.

Extracts sub-concepts and prerequisite dependency edges in a single structured LLM call,
validates against ConceptGraph, and topologically sorts via Kahn's algorithm
(graph_topology skill) so no prerequisite appears after a concept that depends on it.
Persists dependencies to the concept_dependencies table.
"""
from __future__ import annotations

import logging
from typing import Any
from pydantic import BaseModel, Field

from celery_app import celery_app
from agents.llm import get_content_llm as get_llm
from skills.graph_topology import topological_sort
from skills.json_schema_validation import call_llm_with_retry
from skills.prompt_templating import (
    CONCEPT_DEPENDENCY_GRAPH_TEMPLATE,
    SYSTEM_TEACHER,
)
from skills.supabase_persistence import (
    get_learner_profile,
    insert_concept_dependencies,
    insert_learning_path,
    insert_learning_path_items,
    log_agent_run,
)

logger = logging.getLogger(__name__)


class ConceptGraph(BaseModel):
    concepts: list[str] = Field(default_factory=list)
    edges: list[tuple[str, str]] = Field(default_factory=list)


# Backward compatibility alias
PathPlan = ConceptGraph


def build_path(*, student_id: str, broad_topic: str) -> dict[str, Any]:
    """Generate + persist a dependency-ordered learning path. Returns the path with items."""
    # 1. Read student's level from profile
    profile = {}
    try:
        profile = get_learner_profile(student_id) or {}
    except Exception as e:
        logger.warning("[learning_path] Could not read learner profile for %s: %s", student_id, e)
    level = profile.get("default_level", "beginner")

    # 2. Extract concepts and prerequisite dependencies in one structured LLM call
    prompt = SYSTEM_TEACHER.render() + "\n\n" + CONCEPT_DEPENDENCY_GRAPH_TEMPLATE.render(
        broad_topic=broad_topic, level=level
    )
    llm = get_llm()
    try:
        graph = call_llm_with_retry(llm, prompt, ConceptGraph, model_name="learning_path")
        if not graph.concepts:
            raise ValueError("Empty concepts list from LLM")
    except Exception as e:
        logger.warning("[learning_path] LLM failed (%s); using deterministic fallback DAG", e)
        fallback_concepts = [
            f"Foundations of {broad_topic}",
            f"Core Principles of {broad_topic}",
            f"Mechanisms and Laws of {broad_topic}",
            f"Applications of {broad_topic}",
            f"Advanced Topics in {broad_topic}",
        ]
        fallback_edges = [
            (fallback_concepts[0], fallback_concepts[1]),
            (fallback_concepts[1], fallback_concepts[2]),
            (fallback_concepts[2], fallback_concepts[3]),
            (fallback_concepts[3], fallback_concepts[4]),
        ]
        graph = ConceptGraph(concepts=fallback_concepts, edges=fallback_edges)

    # 3. Topologically sort concepts (Kahn's algorithm, stdlib, handles cycles gracefully)
    sorted_concepts = topological_sort(graph.edges, concepts=graph.concepts)

    # 4. Persist learning path
    path_row = insert_learning_path(student_id=student_id, broad_topic=broad_topic)
    path_id = path_row["id"]

    # 5. Persist learning path items in topological order
    items = []
    for i, sub in enumerate(sorted_concepts, start=1):
        items.append(
            {
                "learning_path_id": path_id,
                "item_order": i,
                "sub_topic": sub,
                # First item unlocked, remaining locked until prerequisite is completed
                "status": "unlocked" if i == 1 else "locked",
            }
        )
    if items:
        insert_learning_path_items(items)

    # 6. Persist concept dependencies adjacency list
    dep_rows = []
    concept_prereqs: dict[str, list[str]] = {c: [] for c in sorted_concepts}
    for u, v in graph.edges:
        if v in concept_prereqs:
            concept_prereqs[v].append(u)

    for c in sorted_concepts:
        prereqs = concept_prereqs.get(c)
        if not prereqs:
            dep_rows.append(
                {
                    "learning_path_id": path_id,
                    "concept": c,
                    "depends_on_concept": None,
                }
            )
        else:
            for p in prereqs:
                dep_rows.append(
                    {
                        "learning_path_id": path_id,
                        "concept": c,
                        "depends_on_concept": p,
                    }
                )

    if dep_rows:
        insert_concept_dependencies(dep_rows)

    # 7. Log agent run
    try:
        log_agent_run(
            session_id=None,
            agent_name="learning_path",
            input_summary={"broad_topic": broad_topic, "student_id": student_id, "level": level},
            output_summary={
                "learning_path_id": path_id,
                "concepts_count": len(sorted_concepts),
                "edges_count": len(graph.edges),
            },
            status="success",
        )
    except Exception as e:
        logger.warning("[learning_path] Could not write agent_run_log: %s", e)

    return {
        "id": path_id,
        "broad_topic": broad_topic,
        "items": [
            {
                "id": None,
                "item_order": r["item_order"],
                "sub_topic": r["sub_topic"],
                "status": r["status"],
                "related_session_id": None,
            }
            for r in items
        ],
        "dependencies": dep_rows,
    }


@celery_app.task(name="agents.learning_path.run")
def run(student_id: str, broad_topic: str) -> dict[str, Any]:
    return build_path(student_id=student_id, broad_topic=broad_topic)
