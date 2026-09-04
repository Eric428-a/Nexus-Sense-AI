"""
Knowledge entity persistence.
"""

from __future__ import annotations

from nexus.knowledge.entities import KnowledgeEntity


class EntityRepository:
    """Repository for knowledge graph entities."""

    def __init__(self) -> None:
        self._entities: dict[str, KnowledgeEntity] = {}

    async def get(self, entity_id: str) -> KnowledgeEntity | None:
        return self._entities.get(entity_id)

    async def save(self, entity: KnowledgeEntity) -> KnowledgeEntity:
        self._entities[entity.id] = entity
        return entity

    async def delete(self, entity_id: str) -> bool:
        return self._entities.pop(entity_id, None) is not None

    async def exists(self, entity_id: str) -> bool:
        return entity_id in self._entities

    async def find_by_name(
        self,
        name: str,
    ) -> list[KnowledgeEntity]:

        normalized = name.strip().lower()

        return [
            entity
            for entity in self._entities.values()
            if entity.canonical_name.lower() == normalized
            or normalized in {
                alias.lower()
                for alias in entity.aliases
            }
        ]

    async def find_by_type(
        self,
        entity_type: str,
    ) -> list[KnowledgeEntity]:

        return [
            entity
            for entity in self._entities.values()
            if entity.entity_type.lower() == entity_type.lower()
        ]

    async def count(self) -> int:
        return len(self._entities)