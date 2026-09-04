"""
Keyword-based retrieval.

Provides deterministic lexical search over indexed text.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Iterable


@dataclass(slots=True)
class KeywordDocument:
    """Document indexed by the lexical search engine."""

    document_id: str
    chunk_id: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class KeywordSearchResult:
    """Lexical search result."""

    document_id: str
    chunk_id: str
    content: str
    score: float
    matched_terms: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class KeywordSearch:
    """Simple in-memory lexical retrieval engine."""

    def __init__(
        self,
        documents: Iterable[KeywordDocument] | None = None,
    ) -> None:
        self._documents: dict[str, KeywordDocument] = {}

        if documents:
            for document in documents:
                self.add(document)

    def add(self, document: KeywordDocument) -> None:
        """Add or replace a document."""
        self._documents[document.chunk_id] = document

    def remove(self, chunk_id: str) -> None:
        """Remove an indexed chunk."""
        self._documents.pop(chunk_id, None)

    def clear(self) -> None:
        """Clear the lexical index."""
        self._documents.clear()

    async def search(
        self,
        query: str,
        *,
        limit: int = 10,
    ) -> list[KeywordSearchResult]:
        if not query.strip() or limit <= 0:
            return []

        query_terms = self._tokenize(query)

        if not query_terms:
            return []

        results: list[KeywordSearchResult] = []

        for document in self._documents.values():
            tokens = self._tokenize(document.content)

            if not tokens:
                continue

            token_set = set(tokens)

            matched = [
                term
                for term in query_terms
                if term in token_set
            ]

            if not matched:
                continue

            score = len(matched) / len(set(query_terms))

            results.append(
                KeywordSearchResult(
                    document_id=document.document_id,
                    chunk_id=document.chunk_id,
                    content=document.content,
                    score=min(score, 1.0),
                    matched_terms=matched,
                    metadata=document.metadata.copy(),
                )
            )

        results.sort(
            key=lambda item: item.score,
            reverse=True,
        )

        return results[:limit]

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        return re.findall(
            r"\b[a-zA-Z0-9][a-zA-Z0-9_-]*\b",
            text.lower(),
        )