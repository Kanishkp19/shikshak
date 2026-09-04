"""
Shikshak AI — Graph Topology Skill.

Single responsibility: pure topological sorting of concept dependencies using
Kahn's algorithm. Provides safe degradation to original ordering when cycles
or malformed dependencies are detected, ensuring zero crash risk.
"""
from __future__ import annotations

import logging
from typing import Optional

logger = logging.getLogger(__name__)


def topological_sort(
    edges: list[tuple[str, str]],
    concepts: Optional[list[str]] = None,
) -> list[str]:
    """Sort concepts topologically so prerequisites appear before dependent concepts.

    Parameters:
    - edges: list of (prerequisite, dependent_concept) pairs.
             Each edge (u, v) denotes that concept u must precede concept v.
    - concepts: optional list of all concepts in original/fallback order.
                If omitted, inferred from unique nodes appearing in edges.

    Returns:
    - Topologically ordered list of concept names.
    - If a cycle or unresolvable dependency is detected, falls back to the original
      input order and logs a warning without throwing an exception.
    """
    # 1. Determine universal node list
    if concepts is None:
        seen = set()
        inferred = []
        for u, v in edges:
            if u not in seen:
                seen.add(u)
                inferred.append(u)
            if v not in seen:
                seen.add(v)
                inferred.append(v)
        concepts = inferred

    # Deduplicate while preserving order
    ordered_concepts = []
    seen_concepts = set()
    for c in concepts:
        if c not in seen_concepts:
            seen_concepts.add(c)
            ordered_concepts.append(c)

    if not ordered_concepts:
        return []

    # 2. Build in-degree and adjacency graph
    in_degree = {c: 0 for c in ordered_concepts}
    adj: dict[str, list[str]] = {c: [] for c in ordered_concepts}

    for u, v in edges:
        # Ignore self-loops or nodes not in the concept set
        if u == v or u not in in_degree or v not in in_degree:
            continue
        adj[u].append(v)
        in_degree[v] += 1

    # 3. Kahn's Algorithm
    # Start with nodes that have zero prerequisites (in-degree == 0)
    queue = [c for c in ordered_concepts if in_degree[c] == 0]
    sorted_order: list[str] = []

    while queue:
        curr = queue.pop(0)
        sorted_order.append(curr)

        for neighbor in adj[curr]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    # 4. Cycle check: if not all concepts processed, a cycle exists
    if len(sorted_order) < len(ordered_concepts):
        logger.warning(
            "[topological_sort] Cycle detected in concept dependencies (%d of %d resolved). "
            "Falling back to original input ordering.",
            len(sorted_order),
            len(ordered_concepts),
        )
        return ordered_concepts

    return sorted_order
