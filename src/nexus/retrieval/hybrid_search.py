"""
Hybrid retrieval.

Combines:
    semantic similarity
+
    lexical relevance

into one normalized ranking.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from nexus.retrieval.keyword_search import (
    KeywordSearch,
    KeywordSearchResult,
)
from nexus.retrieval.semantic_search import (
    SemanticSearch,
    SemanticSearchResult,
)


@dataclass(slots=True)
class HybridSearchResult:
    """Combined retrieval result."""

    document_id: str
    chunk_id: str
    content: str

    score: float

    semantic_score: float
    keyword_score: float

    metadata: dict[str, Any] = field(default_factory=dict)


class HybridSearch:
    """Weighted semantic + lexical retrieval."""

    def __init__(
        self,
        semantic_search: SemanticSearch,
        keyword_search: KeywordSearch,
        *,
        semantic_weight: float = 0.65,
        keyword_weight: float = 0.35,
    ) -> None:
        if semantic_weight < 0 or keyword_weight < 0:
            raise ValueError(
                "Search weights cannot be negative."
            )

        total = semantic_weight + keyword_weight

        if total <= 0:
            raise ValueError(
                "At least one search weight must be positive."
            )

        self.semantic_search = semantic_search
        self.keyword_search = keyword_search

        self.semantic_weight = semantic_weight / total
        self.keyword_weight = keyword_weight / total

    async def search(
        self,
        query: str,
        *,
        limit: int = 10,
        candidate_limit: int | None = None,
    ) -> list[HybridSearchResult]:

        if not query.strip() or limit <= 0:
            return []

        candidate_limit = candidate_limit or max(
            limit * 3,
            10,
        )

        semantic_results = await self.semantic_search.search(
            query,
            limit=candidate_limit,
        )

        keyword_results = await self.keyword_search.search(
            query,
            limit=candidate_limit,
        )

        semantic_map = {
            result.chunk_id: result
            for result in semantic_results
        }

        keyword_map = {
            result.chunk_id: result
            for result in keyword_results
        }

        chunk_ids = (
            set(semantic_map)
            | set(keyword_map)
        )

        combined: list[HybridSearchResult] = []

        for chunk_id in chunk_ids:
            semantic = semantic_map.get(chunk_id)
            keyword = keyword_map.get(chunk_id)

            semantic_score = (
                semantic.score
                if semantic
                else 0.0
            )

            keyword_score = (
                keyword.score
                if keyword
                else 0.0
            )

            score = (
                semantic_score * self.semantic_weight
                + keyword_score * self.keyword_weight
            )

            source = semantic or keyword

            if source is None:
                continue

            combined.append(
                HybridSearchResult(
                    document_id=source.document_id,
                    chunk_id=source.chunk_id,
                    content=source.content,
                    score=score,
                    semantic_score=semantic_score,
                    keyword_score=keyword_score,
                    metadata=source.metadata.copy(),
                )
            )

        combined.sort(
            key=lambda result: result.score,
            reverse=True,
        )

        return combined[:limit]