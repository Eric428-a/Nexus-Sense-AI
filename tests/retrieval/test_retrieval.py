"""
Tests for NEXUS-SENSE retrieval.
"""

from __future__ import annotations

import pytest

from src.nexus.retrieval.context_builder import ContextBuilder
from src.nexus.retrieval.hybrid_search import HybridSearch
from src.nexus.retrieval.keyword_search import (
    KeywordDocument,
    KeywordSearch,
)
from src.nexus.retrieval.reranker import Reranker
from src.nexus.retrieval.semantic_search import (
    SemanticSearch,
    SemanticSearchResult,
)


class MockVectorStore:
    async def search(
        self,
        query: str,
        *,
        limit: int = 10,
    ):
        return [
            SemanticSearchResult(
                document_id="doc-1",
                chunk_id="chunk-1",
                content=(
                    "Artificial intelligence supports "
                    "decision intelligence."
                ),
                score=0.92,
            ),
            SemanticSearchResult(
                document_id="doc-2",
                chunk_id="chunk-2",
                content="Unrelated content.",
                score=0.30,
            ),
        ][:limit]


@pytest.mark.asyncio
async def test_semantic_search():
    search = SemanticSearch(
        vector_store=MockVectorStore()
    )

    results = await search.search(
        "artificial intelligence"
    )

    assert len(results) == 2
    assert results[0].score == 0.92


@pytest.mark.asyncio
async def test_keyword_search():
    search = KeywordSearch(
        [
            KeywordDocument(
                document_id="doc-1",
                chunk_id="chunk-1",
                content=(
                    "Artificial intelligence "
                    "supports decision systems."
                ),
            ),
            KeywordDocument(
                document_id="doc-2",
                chunk_id="chunk-2",
                content="Ocean engineering.",
            ),
        ]
    )

    results = await search.search(
        "artificial intelligence"
    )

    assert results
    assert results[0].chunk_id == "chunk-1"
    assert results[0].score > 0


@pytest.mark.asyncio
async def test_hybrid_search():
    semantic = SemanticSearch(
        vector_store=MockVectorStore()
    )

    keyword = KeywordSearch(
        [
            KeywordDocument(
                document_id="doc-1",
                chunk_id="chunk-1",
                content=(
                    "Artificial intelligence "
                    "supports decision intelligence."
                ),
            )
        ]
    )

    hybrid = HybridSearch(
        semantic,
        keyword,
    )

    results = await hybrid.search(
        "artificial intelligence"
    )

    assert results
    assert results[0].chunk_id == "chunk-1"
    assert 0 <= results[0].score <= 1


@pytest.mark.asyncio
async def test_reranker():
    semantic = SemanticSearch(
        vector_store=MockVectorStore()
    )

    candidates = await semantic.search(
        "artificial intelligence"
    )

    reranker = Reranker()

    results = await reranker.rerank(
        "artificial intelligence",
        candidates,
    )

    assert results
    assert results[0].rank == 1
    assert (
        results[0].rerank_score
        >= results[-1].rerank_score
    )


@pytest.mark.asyncio
async def test_context_builder():
    semantic = SemanticSearch(
        vector_store=MockVectorStore()
    )

    candidates = await semantic.search(
        "artificial intelligence"
    )

    reranker = Reranker()

    results = await reranker.rerank(
        "artificial intelligence",
        candidates,
    )

    builder = ContextBuilder(
        max_characters=500
    )

    context = builder.build(
        "artificial intelligence",
        results,
    )

    assert context.query == (
        "artificial intelligence"
    )

    assert context.passages
    assert context.citations
    assert context.token_estimate > 0