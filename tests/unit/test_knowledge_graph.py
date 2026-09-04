"""
Tests for the NEXUS-SENSE knowledge graph.
"""

from src.nexus.knowledge.entities import KnowledgeEntity
from src.nexus.knowledge.graph import KnowledgeGraph
from src.nexus.knowledge.graph_queries import (
    GraphQueryEngine,
)
from src.nexus.knowledge.relationships import (
    KnowledgeRelationship,
)


def build_graph():
    graph = KnowledgeGraph()

    alpha = KnowledgeEntity(
        entity_id="alpha",
        canonical_name="Alpha Corporation",
        entity_type="organization",
    )

    beta = KnowledgeEntity(
        entity_id="beta",
        canonical_name="Beta Corporation",
        entity_type="organization",
    )

    project = KnowledgeEntity(
        entity_id="project",
        canonical_name="Project Atlas",
        entity_type="project",
    )

    graph.add_entity(alpha)
    graph.add_entity(beta)
    graph.add_entity(project)

    graph.add_relationship(
        KnowledgeRelationship(
            relationship_id="r1",
            source_entity_id="alpha",
            target_entity_id="project",
            relationship_type="operates",
        )
    )

    graph.add_relationship(
        KnowledgeRelationship(
            relationship_id="r2",
            source_entity_id="beta",
            target_entity_id="project",
            relationship_type="supports",
        )
    )

    return graph


def test_graph_stats():
    graph = build_graph()

    assert graph.stats() == {
        "entities": 3,
        "relationships": 2,
    }


def test_find_entity_by_name():
    graph = build_graph()
    engine = GraphQueryEngine(graph)

    results = engine.find_by_name(
        "Alpha Corporation"
    )

    assert len(results) == 1
    assert results[0].entity_id == "alpha"


def test_find_entity_by_type():
    graph = build_graph()
    engine = GraphQueryEngine(graph)

    results = engine.find_by_type(
        "organization"
    )

    assert len(results) == 2


def test_neighbors():
    graph = build_graph()

    neighbors = graph.neighbors(
        "alpha"
    )

    assert len(neighbors) == 1
    assert neighbors[0].entity_id == "project"


def test_neighborhood():
    graph = build_graph()
    engine = GraphQueryEngine(graph)

    result = engine.neighborhood(
        "alpha",
        depth=1,
    )

    entity_ids = {
        entity.entity_id
        for entity in result["entities"]
    }

    assert "alpha" in entity_ids
    assert "project" in entity_ids


def test_shortest_path():
    graph = build_graph()
    engine = GraphQueryEngine(graph)

    path = engine.shortest_path(
        "alpha",
        "project",
    )

    assert path is not None
    assert path.entity_ids == [
        "alpha",
        "project",
    ]
    assert path.relationship_ids == ["r1"]