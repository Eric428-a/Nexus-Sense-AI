from src.nexus.database.vector_store import (
    InMemoryVectorStore,
    VectorRecord,
)
from src.nexus.database.repositories.documents import DocumentRepository


async def test_vector_store_upsert_and_search() -> None:
    store = InMemoryVectorStore()

    await store.upsert(
        [
            VectorRecord(
                id="a",
                vector=[1.0, 0.0, 0.0],
                text="alpha",
            ),
            VectorRecord(
                id="b",
                vector=[0.0, 1.0, 0.0],
                text="beta",
            ),
        ]
    )

    results = await store.search(
        [1.0, 0.0, 0.0],
        top_k=2,
    )

    assert len(results) == 2
    assert results[0].id == "a"
    assert results[0].score > results[1].score


async def test_vector_store_delete() -> None:
    store = InMemoryVectorStore()

    await store.upsert(
        [
            VectorRecord(
                id="a",
                vector=[1.0, 0.0],
            )
        ]
    )

    await store.delete(["a"])

    assert await store.count() == 0


async def test_document_repository() -> None:
    repository = DocumentRepository()

    assert await repository.count() == 0