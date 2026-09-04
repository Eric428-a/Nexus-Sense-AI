"""
Unified memory manager.

Agents can interact with one memory facade without knowing which
memory subsystem is being used.
"""

from __future__ import annotations

from typing import Any

from nexus.memory.episodic import EpisodicMemory
from nexus.memory.long_term import LongTermMemory
from nexus.memory.semantic import SemanticMemory
from nexus.memory.short_term import ShortTermMemory


class MemoryManager:
    """
    Unified interface over all NEXUS-SENSE memory systems.
    """

    def __init__(
        self,
        *,
        short_term: ShortTermMemory | None = None,
        long_term: LongTermMemory | None = None,
        episodic: EpisodicMemory | None = None,
        semantic: SemanticMemory | None = None,
    ) -> None:

        self.short_term = short_term or ShortTermMemory()
        self.long_term = long_term or LongTermMemory()
        self.episodic = episodic or EpisodicMemory()
        self.semantic = semantic

    async def remember(
        self,
        key: str,
        value: Any,
        *,
        importance: float = 0.5,
    ) -> None:

        self.short_term.put(
            key,
            value,
        )

        await self.long_term.store(
            key,
            value,
            importance=importance,
        )

    async def recall(
        self,
        key: str,
    ) -> Any | None:

        item = self.short_term.get(key)

        if item is not None:
            return item.value

        matches = await self.long_term.find(key)

        if matches:
            matches.sort(
                key=lambda memory: memory.importance,
                reverse=True,
            )

            return matches[0].value

        return None

    async def snapshot(self) -> dict[str, int]:
        """Return memory subsystem statistics."""

        return {
            "short_term": len(self.short_term),
            "long_term": await self.long_term.count(),
            "episodic": await self.episodic.count(),
            "semantic": (
                await self.semantic.count()
                if self.semantic is not None
                else 0
            ),
        }