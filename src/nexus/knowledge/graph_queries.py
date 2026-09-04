"""
Knowledge graph query services.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from nexus.knowledge.graph import KnowledgeGraph


@dataclass(slots=True)
class GraphPath:
    """Represents a graph traversal path."""

    entity_ids: list[str]
    relationship_ids: list[str]


class GraphQueryEngine:
    """High-level query interface over KnowledgeGraph."""

    def __init__(
        self,
        graph: KnowledgeGraph,
    ) -> None:
        self.graph = graph

    def find_by_name(
        self,
        name: str,
    ) -> list[Any]:

        normalized = name.strip().lower()

        if not normalized:
            return []

        matches = []

        for entity in self.graph.entities():
            names = [
                entity.canonical_name,
                *entity.aliases,
            ]

            if any(
                normalized == value.lower()
                for value in names
            ):
                matches.append(entity)

        return matches

    def find_by_type(
        self,
        entity_type: str,
    ) -> list[Any]:

        normalized = entity_type.strip().lower()

        return [
            entity
            for entity in self.graph.entities()
            if entity.entity_type.lower()
            == normalized
        ]

    def neighborhood(
        self,
        entity_id: str,
        *,
        depth: int = 1,
    ) -> dict[str, Any]:

        if depth < 1:
            raise ValueError(
                "depth must be at least 1."
            )

        if self.graph.get_entity(entity_id) is None:
            return {
                "entities": [],
                "relationships": [],
            }

        visited = {entity_id}
        frontier = {entity_id}

        relationships = set()

        for _ in range(depth):
            next_frontier: set[str] = set()

            for current in frontier:
                for relationship in (
                    self.graph.outgoing_relationships(
                        current
                    )
                ):
                    relationships.add(
                        relationship.relationship_id
                    )

                    target = (
                        relationship.target_entity_id
                    )

                    if target not in visited:
                        visited.add(target)
                        next_frontier.add(target)

                for relationship in (
                    self.graph.incoming_relationships(
                        current
                    )
                ):
                    relationships.add(
                        relationship.relationship_id
                    )

                    source = (
                        relationship.source_entity_id
                    )

                    if source not in visited:
                        visited.add(source)
                        next_frontier.add(source)

            frontier = next_frontier

            if not frontier:
                break

        entities = [
            self.graph.get_entity(entity)
            for entity in visited
        ]

        relationship_objects = [
            self.graph.get_relationship(
                relationship_id
            )
            for relationship_id in relationships
        ]

        return {
            "entities": [
                entity
                for entity in entities
                if entity is not None
            ],
            "relationships": [
                relationship
                for relationship in relationship_objects
                if relationship is not None
            ],
        }

    def shortest_path(
        self,
        source_entity_id: str,
        target_entity_id: str,
    ) -> GraphPath | None:

        if (
            self.graph.get_entity(source_entity_id)
            is None
            or self.graph.get_entity(target_entity_id)
            is None
        ):
            return None

        if source_entity_id == target_entity_id:
            return GraphPath(
                entity_ids=[source_entity_id],
                relationship_ids=[],
            )

        queue: list[tuple[str, list[str], list[str]]] = [
            (
                source_entity_id,
                [source_entity_id],
                [],
            )
        ]

        visited = {source_entity_id}

        while queue:
            current, entity_path, relationship_path = (
                queue.pop(0)
            )

            for relationship in (
                self.graph.outgoing_relationships(
                    current
                )
            ):
                next_entity = (
                    relationship.target_entity_id
                )

                if next_entity in visited:
                    continue

                next_entity_path = [
                    *entity_path,
                    next_entity,
                ]

                next_relationship_path = [
                    *relationship_path,
                    relationship.relationship_id,
                ]

                if next_entity == target_entity_id:
                    return GraphPath(
                        entity_ids=next_entity_path,
                        relationship_ids=next_relationship_path,
                    )

                visited.add(next_entity)

                queue.append(
                    (
                        next_entity,
                        next_entity_path,
                        next_relationship_path,
                    )
                )

        return None