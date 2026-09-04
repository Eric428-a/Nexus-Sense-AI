"""
Context construction for downstream reasoning agents.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Sequence

from nexus.retrieval.reranker import RerankedResult


@dataclass(slots=True)
class RetrievalContext:
    """Structured context assembled from retrieved evidence."""

    query: str

    passages: list[str] = field(default_factory=list)

    source_ids: list[str] = field(default_factory=list)

    chunk_ids: list[str] = field(default_factory=list)

    citations: list[dict[str, Any]] = field(
        default_factory=list
    )

    token_estimate: int = 0

    metadata: dict[str, Any] = field(default_factory=dict)


class ContextBuilder:
    """Build bounded reasoning context."""

    def __init__(
        self,
        *,
        max_characters: int = 12000,
    ) -> None:
        if max_characters <= 0:
            raise ValueError(
                "max_characters must be positive."
            )

        self.max_characters = max_characters

    def build(
        self,
        query: str,
        results: Sequence[RerankedResult],
    ) -> RetrievalContext:

        passages: list[str] = []
        source_ids: list[str] = []
        chunk_ids: list[str] = []
        citations: list[dict[str, Any]] = []

        current_length = 0

        for result in results:
            content = result.content.strip()

            if not content:
                continue

            remaining = (
                self.max_characters
                - current_length
            )

            if remaining <= 0:
                break

            content = content[:remaining]

            passages.append(content)

            source_ids.append(
                result.document_id
            )

            chunk_ids.append(
                result.chunk_id
            )

            citations.append(
                {
                    "document_id": result.document_id,
                    "chunk_id": result.chunk_id,
                    "rank": result.rank,
                    "score": result.rerank_score,
                }
            )

            current_length += len(content)

        combined = "\n\n".join(passages)

        return RetrievalContext(
            query=query,
            passages=passages,
            source_ids=source_ids,
            chunk_ids=chunk_ids,
            citations=citations,
            token_estimate=max(
                0,
                len(combined) // 4,
            ),
            metadata={
                "passage_count": len(passages),
                "character_count": len(combined),
                "max_characters": self.max_characters,
            },
        )