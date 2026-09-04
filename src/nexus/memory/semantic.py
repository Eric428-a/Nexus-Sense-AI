"""
Semantic memory.

Semantic memory connects durable knowledge with vector retrieval.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from nexus.database.vector_store import (
    VectorRecord,
    VectorSearchResult,
    VectorStore,
)
from nexus.utils.ids import generate_id


@dataclass(slots=True)
class SemanticMemoryItem:
    """A semantic knowledge item."""

    id: str = field(default_factory=generate_id)
    content: str = ""
    namespace: str = "default"
    source_ids: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class SemanticMemory:
    """
    Semantic memory backed by a vector store.
    """

    def __init__(self, vector_store: VectorStore) -> None:
        self.vector_store = vector_store

    async def store(
        self,
        content: str,
        vector: list[float],
        *,
        namespace: str = "default",
        source_ids: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> SemanticMemoryItem:

        item = SemanticMemoryItem(
            content=content,
            namespace=namespace,
            source_ids=source_ids or [],
            metadata=metadata or {},
        )

        record = VectorRecord(
            id=item.id,
            vector=vector,
            text=content,
            metadata={
                **item.metadata,
                "namespace": namespace,
                "source_ids": item.source_ids,
            },
        )

        await self.vector_store.upsert([record])

        return item

    async def search(
        self,
        vector: list[float],
        *,
        top_k: int = 10,
    ) -> list[VectorSearchResult]:

        return await self.vector_store.search(
            vector,
            top_k=top_k,
        )

    async def delete(self, memory_id: str) -> None:
        await self.vector_store.delete([memory_id])

    async def count(self) -> int:
        return await self.vector_store.count()