"""
Unit tests for Work Stream 4: Lightweight Concept-Dependency Graph & Topological Sort.
"""
from unittest.mock import MagicMock, patch

from agents.learning_path import ConceptGraph, build_path
from skills.graph_topology import topological_sort


def test_topological_sort_known_small_dag():
    """Verify topological sort on a known DAG:
    Dependencies:
    - Math Basics -> Algebra
    - Algebra -> Calculus
    - Algebra -> Linear Algebra
    - Calculus -> Machine Learning
    - Linear Algebra -> Machine Learning
    """
    edges = [
        ("Math Basics", "Algebra"),
        ("Algebra", "Calculus"),
        ("Algebra", "Linear Algebra"),
        ("Calculus", "Machine Learning"),
        ("Linear Algebra", "Machine Learning"),
    ]
    concepts = ["Machine Learning", "Linear Algebra", "Calculus", "Algebra", "Math Basics"]

    ordered = topological_sort(edges, concepts=concepts)

    # Every concept must appear
    assert set(ordered) == set(concepts)

    # Verify prerequisite invariants
    pos = {c: i for i, c in enumerate(ordered)}
    assert pos["Math Basics"] < pos["Algebra"]
    assert pos["Algebra"] < pos["Calculus"]
    assert pos["Algebra"] < pos["Linear Algebra"]
    assert pos["Calculus"] < pos["Machine Learning"]
    assert pos["Linear Algebra"] < pos["Machine Learning"]


def test_topological_sort_cycle_graceful_degradation():
    """Verify that a cyclic dependency list degrades gracefully to input order without throwing."""
    # Cyclic edges: A -> B -> C -> A
    cyclic_edges = [
        ("Concept A", "Concept B"),
        ("Concept B", "Concept C"),
        ("Concept C", "Concept A"),
    ]
    input_concepts = ["Concept A", "Concept B", "Concept C"]

    # Must NOT raise any exception, and must return the input ordering safely
    result = topological_sort(cyclic_edges, concepts=input_concepts)
    assert result == input_concepts


def test_topological_sort_independent_nodes():
    """Verify topological sort with disconnected or independent concept nodes."""
    edges = [("A", "B")]
    concepts = ["C", "B", "A", "D"]

    ordered = topological_sort(edges, concepts=concepts)
    assert set(ordered) == set(concepts)
    pos = {c: i for i, c in enumerate(ordered)}
    assert pos["A"] < pos["B"]


def test_learning_path_agent_build_path_with_graph():
    """Test Learning Path Agent build_path uses topological sorting to order items."""
    broad_topic = "Classical Mechanics"
    student_id = "test-student-999"

    mock_graph = ConceptGraph(
        concepts=[
            "Newton's Third Law",
            "Kinematics & Velocity",
            "Force & Newton's First Law",
            "Momentum & Collisions",
        ],
        edges=[
            ("Kinematics & Velocity", "Force & Newton's First Law"),
            ("Force & Newton's First Law", "Newton's Third Law"),
            ("Newton's Third Law", "Momentum & Collisions"),
        ],
    )

    with patch("agents.learning_path.get_learner_profile", return_value={"default_level": "intermediate"}), \
         patch("agents.learning_path.call_llm_with_retry", return_value=mock_graph), \
         patch("agents.learning_path.insert_learning_path", return_value={"id": "path-123"}), \
         patch("agents.learning_path.insert_learning_path_items") as mock_insert_items, \
         patch("agents.learning_path.insert_concept_dependencies") as mock_insert_deps, \
         patch("agents.learning_path.log_agent_run"):

        res = build_path(student_id=student_id, broad_topic=broad_topic)

        assert res["id"] == "path-123"
        assert len(res["items"]) == 4

        # Ordered items should start with Kinematics & Velocity, then Force, etc.
        item_names = [it["sub_topic"] for it in res["items"]]
        assert item_names[0] == "Kinematics & Velocity"
        assert item_names[1] == "Force & Newton's First Law"
        assert item_names[2] == "Newton's Third Law"
        assert item_names[3] == "Momentum & Collisions"

        # Check unlocked status for first item, locked for subsequent
        assert res["items"][0]["status"] == "unlocked"
        assert res["items"][1]["status"] == "locked"
        assert res["items"][2]["status"] == "locked"
        assert res["items"][3]["status"] == "locked"

        # Dependencies persisted
        mock_insert_deps.assert_called_once()
        deps_persisted = mock_insert_deps.call_args[0][0]
        assert len(deps_persisted) == 4
