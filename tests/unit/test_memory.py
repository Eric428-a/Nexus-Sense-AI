from src.nexus.database.vector_store import InMemoryVectorStore
from src.nexus.memory.episodic import EpisodicMemory
from src.nexus.memory.long_term import LongTermMemory
from src.nexus.memory.manager import MemoryManager
from src.nexus.memory.semantic import SemanticMemory
from src.nexus.memory.short_term import ShortTermMemory


def test_short_term_memory() -> None:
    memory = ShortTermMemory(max_items=2)

    memory.put("name", "NEXUS")
    memory.put("version", "0.1.0")

    assert memory.get("name") is not None
    assert memory.get("name").value == "NEXUS"


async def test_long_term_memory() -> None:
    memory = LongTermMemory()

    item = await memory.store(
        "project",
        "NEXUS-SENSE",
        importance=0.9,
    )

    assert item.key == "project"

    matches = await memory.find("project")

    assert len(matches) == 1


async def test_episodic_memory() -> None:
    memory = EpisodicMemory()

    episode = await memory.record(
        episode_type="investigation",
        title="Initial Investigation",
        summary="System analyzed an intelligence question.",
    )

    completed = await memory.complete(
        episode.id,
        outcome="completed",
    )

    assert completed is not None
    assert completed.outcome == "completed"
    assert completed.completed_at is not None


async def test_semantic_memory() -> None:
    vector_store = InMemoryVectorStore()
    memory = SemanticMemory(vector_store)

    item = await memory.store(
        "Artificial intelligence system",
        [1.0, 0.0, 0.0],
    )

    assert item.content == "Artificial intelligence system"
    assert await memory.count() == 1

    results = await memory.search(
        [1.0, 0.0, 0.0],
    )

    assert results[0].id == item.id


async def test_memory_manager() -> None:
    manager = MemoryManager(
        short_term=ShortTermMemory(),
        long_term=LongTermMemory(),
        episodic=EpisodicMemory(),
    )

    await manager.remember(
        "system_name",
        "NEXUS-SENSE",
    )

    value = await manager.recall("system_name")

    assert value == "NEXUS-SENSE"

    snapshot = await manager.snapshot()

    assert snapshot["short_term"] == 1
    assert snapshot["long_term"] == 1