"""
Retrieval reranking.

The reranker provides a second-stage scoring mechanism after
initial candidate retrieval.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Sequence


@dataclass(slots=True)
class RerankedResult:
    """Reranked retrieval candidate."""

    document_id: str
    chunk_id: str
    content: str

    original_score: float
    rerank_score: float

    rank: int

    metadata: dict[str, Any] = field(default_factory=dict)


class Reranker:
    """
    Lightweight deterministic reranker.

    The scoring model can later be replaced with a cross-encoder
    or LLM-based relevance model.
    """

    def __init__(
        self,
        *,
        exact_match_bonus: float = 0.2,
    ) -> None:
        self.exact_match_bonus = exact_match_bonus

    async def rerank(
        self,
        query: str,
        candidates: Sequence[Any],
        *,
        limit: int = 10,
    ) -> list[RerankedResult]:

        if not query.strip() or limit <= 0:
            return []

        query_terms = set(
            self._tokenize(query)
        )

        scored: list[tuple[float, Any]] = []

        for candidate in candidates:
            content = str(
                getattr(candidate, "content", "")
            )

            content_terms = set(
                self._tokenize(content)
            )

            overlap = (
                len(query_terms & content_terms)
                / max(len(query_terms), 1)
            )

            original_score = float(
                getattr(candidate, "score", 0.0)
            )

            score = (
                original_score * 0.7
                + overlap * 0.3
            )

            if query.lower() in content.lower():
                score += self.exact_match_bonus

            scored.append(
                (min(score, 1.0), candidate)
            )

        scored.sort(
            key=lambda item: item[0],
            reverse=True,
        )

        results: list[RerankedResult] = []

        for index, (score, candidate) in enumerate(
            scored[:limit],
            start=1,
        ):
            results.append(
                RerankedResult(
                    document_id=candidate.document_id,
                    chunk_id=candidate.chunk_id,
                    content=candidate.content,
                    original_score=float(
                        getattr(candidate, "score", 0.0)
                    ),
                    rerank_score=score,
                    rank=index,
                    metadata=dict(
                        getattr(candidate, "metadata", {})
                    ),
                )
            )

        return results

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        return re.findall(
            r"\b[a-zA-Z0-9][a-zA-Z0-9_-]*\b",
            text.lower(),
        )