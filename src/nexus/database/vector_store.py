"""
Vector store abstractions.

The application can use this interface with:

- Chroma
- PostgreSQL/pgvector
- Qdrant
- Weaviate
- Pinecone
- an in-memory implementation for tests
"""

from __future__ import annotations

from dataclasses import dataclass, field
from math import sqrt
from typing import Any, Protocol

import numpy as np


@dataclass(slots=True)
class VectorRecord:
    """A vector stored in the vector index."""

    id: str
    vector: list[float]
    text: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class VectorSearchResult:
    """A vector similarity result."""

    id: str
    score: float
    text: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


class VectorStore(Protocol):
    """Protocol implemented by vector database adapters."""

    async def upsert(self, records: list[VectorRecord]) -> None:
        ...

    async def delete(self, ids: list[str]) -> None:
        ...

    async def search(
        self,
        vector: list[float],
        *,
        top_k: int = 10,
    ) -> list[VectorSearchResult]:
        ...

    async def count(self) -> int:
        ...


def _cosine_similarity(
    left: list[float],
    right: list[float],
) -> float:
    """Calculate cosine similarity between two vectors."""

    if len(left) != len(right):
        raise ValueError("Vectors must have identical dimensions.")

    left_norm = sqrt(sum(value * value for value in left))
    right_norm = sqrt(sum(value * value for value in right))

    if left_norm == 0 or right_norm == 0:
        return 0.0

    return sum(
        left_value * right_value
        for left_value, right_value in zip(left, right)
    ) / (left_norm * right_norm)


class InMemoryVectorStore:
    """
    Deterministic vector store used for development and testing.

    This implementation requires no external infrastructure.
    """

    def __init__(self) -> None:
        self._records: dict[str, VectorRecord] = {}

    async def upsert(self, records: list[VectorRecord]) -> None:
        for record in records:
            self._records[record.id] = record

    async def delete(self, ids: list[str]) -> None:
        for record_id in ids:
            self._records.pop(record_id, None)

    async def search(
        self,
        vector: list[float],
        *,
        top_k: int = 10,
    ) -> list[VectorSearchResult]:

        results: list[VectorSearchResult] = []

        for record in self._records.values():
            score = _cosine_similarity(vector, record.vector)

            results.append(
                VectorSearchResult(
                    id=record.id,
                    score=score,
                    text=record.text,
                    metadata=dict(record.metadata),
                )
            )

        results.sort(
            key=lambda item: item.score,
            reverse=True,
        )

        return results[:top_k]

    async def count(self) -> int:
        return len(self._records)

    async def clear(self) -> None:
        self._records.clear()

    async def get(self, record_id: str) -> VectorRecord | None:
        return self._records.get(record_id)

    def as_numpy(self) -> np.ndarray:
        """Expose vectors for analytical/evaluation workloads."""

        if not self._records:
            return np.empty((0, 0))

        return np.array(
            [record.vector for record in self._records.values()],
            dtype=float,
        )