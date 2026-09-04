"""
Semantic retrieval primitives.

The implementation is intentionally backend-agnostic.

A real vector database can later implement the `VectorStoreProtocol`
without requiring changes to the retrieval API.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol, Sequence


@dataclass(slots=True)
class SemanticSearchResult:
    """One semantic retrieval candidate."""

    document_id: str
    chunk_id: str
    content: str
    score: float

    metadata: dict[str, Any] = field(default_factory=dict)


class VectorStoreProtocol(Protocol):
    """Protocol expected from a vector-search backend."""

    async def search(
        self,
        query: str,
        *,
        limit: int = 10,
    ) -> Sequence[SemanticSearchResult]:
        ...


class SemanticSearch:
    """Semantic retrieval facade."""

    def __init__(
        self,
        vector_store: VectorStoreProtocol | None = None,
    ) -> None:
        self.vector_store = vector_store

    async def search(
        self,
        query: str,
        *,
        limit: int = 10,
    ) -> list[SemanticSearchResult]:
        if not query.strip():
            return []

        if limit <= 0:
            return []

        if self.vector_store is None:
            return []

        results = await self.vector_store.search(
            query,
            limit=limit,
        )

        return [
            result
            for result in results
            if 0.0 <= result.score <= 1.0
        ]