"""
In-memory knowledge graph.

This provides the canonical graph contract before a persistent graph
backend is introduced.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Iterable

from nexus.knowledge.entities import KnowledgeEntity
from nexus.knowledge.relationships import KnowledgeRelationship


class KnowledgeGraph:
    """Directed entity relationship graph."""

    def __init__(self) -> None:
        self._entities: dict[str, KnowledgeEntity] = {}

        self._relationships: dict[
            str,
            KnowledgeRelationship,
        ] = {}

        self._outgoing: dict[
            str,
            set[str],
        ] = defaultdict(set)

        self._incoming: dict[
            str,
            set[str],
        ] = defaultdict(set)

    def add_entity(
        self,
        entity: KnowledgeEntity,
    ) -> KnowledgeEntity:
        """Insert or replace an entity."""
        self._entities[entity.entity_id] = entity
        return entity

    def add_relationship(
        self,
        relationship: KnowledgeRelationship,
    ) -> KnowledgeRelationship:

        if relationship.source_entity_id not in self._entities:
            raise ValueError(
                "Source entity does not exist: "
                f"{relationship.source_entity_id}"
            )

        if relationship.target_entity_id not in self._entities:
            raise ValueError(
                "Target entity does not exist: "
                f"{relationship.target_entity_id}"
            )

        self._relationships[
            relationship.relationship_id
        ] = relationship

        self._outgoing[
            relationship.source_entity_id
        ].add(relationship.relationship_id)

        self._incoming[
            relationship.target_entity_id
        ].add(relationship.relationship_id)

        return relationship

    def get_entity(
        self,
        entity_id: str,
    ) -> KnowledgeEntity | None:
        return self._entities.get(entity_id)

    def get_relationship(
        self,
        relationship_id: str,
    ) -> KnowledgeRelationship | None:
        return self._relationships.get(
            relationship_id
        )

    def entities(self) -> list[KnowledgeEntity]:
        return list(self._entities.values())

    def relationships(
        self,
    ) -> list[KnowledgeRelationship]:
        return list(
            self._relationships.values()
        )

    def outgoing_relationships(
        self,
        entity_id: str,
    ) -> list[KnowledgeRelationship]:

        relationship_ids = self._outgoing.get(
            entity_id,
            set(),
        )

        return [
            self._relationships[relationship_id]
            for relationship_id in relationship_ids
        ]

    def incoming_relationships(
        self,
        entity_id: str,
    ) -> list[KnowledgeRelationship]:

        relationship_ids = self._incoming.get(
            entity_id,
            set(),
        )

        return [
            self._relationships[relationship_id]
            for relationship_id in relationship_ids
        ]

    def neighbors(
        self,
        entity_id: str,
    ) -> list[KnowledgeEntity]:

        relationship_ids = (
            self._outgoing.get(entity_id, set())
            | self._incoming.get(entity_id, set())
        )

        neighbor_ids: set[str] = set()

        for relationship_id in relationship_ids:
            relationship = self._relationships[
                relationship_id
            ]

            if relationship.source_entity_id == entity_id:
                neighbor_ids.add(
                    relationship.target_entity_id
                )
            else:
                neighbor_ids.add(
                    relationship.source_entity_id
                )

        return [
            self._entities[neighbor_id]
            for neighbor_id in neighbor_ids
            if neighbor_id in self._entities
        ]

    def bulk_add_entities(
        self,
        entities: Iterable[KnowledgeEntity],
    ) -> None:
        for entity in entities:
            self.add_entity(entity)

    def bulk_add_relationships(
        self,
        relationships: Iterable[KnowledgeRelationship],
    ) -> None:
        for relationship in relationships:
            self.add_relationship(relationship)

    def stats(self) -> dict[str, int]:
        """Return graph statistics."""
        return {
            "entities": len(self._entities),
            "relationships": len(
                self._relationships
            ),
        }