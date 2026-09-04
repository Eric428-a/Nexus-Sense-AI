"""
Persistent long-term memory abstraction.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from nexus.utils.ids import generate_id
from nexus.utils.timestamps import utc_now


@dataclass(slots=True)
class LongTermMemoryItem:
    """Durable memory record."""

    id: str = field(default_factory=generate_id)
    namespace: str = "default"
    key: str = ""
    value: Any = None
    importance: float = 0.5
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)
    metadata: dict[str, Any] = field(default_factory=dict)


class LongTermMemory:
    """
    Durable application memory.

    The current implementation is in-memory, while the interface is
    intentionally suitable for MongoDB/PostgreSQL persistence.
    """

    def __init__(self) -> None:
        self._items: dict[str, LongTermMemoryItem] = {}

    async def store(
        self,
        key: str,
        value: Any,
        *,
        namespace: str = "default",
        importance: float = 0.5,
        metadata: dict[str, Any] | None = None,
    ) -> LongTermMemoryItem:

        if not 0.0 <= importance <= 1.0:
            raise ValueError("importance must be between 0 and 1.")

        item = LongTermMemoryItem(
            namespace=namespace,
            key=key,
            value=value,
            importance=importance,
            metadata=metadata or {},
        )

        self._items[item.id] = item
        return item

    async def get(self, memory_id: str) -> LongTermMemoryItem | None:
        return self._items.get(memory_id)

    async def find(
        self,
        key: str,
        *,
        namespace: str = "default",
    ) -> list[LongTermMemoryItem]:

        return [
            item
            for item in self._items.values()
            if item.key == key
            and item.namespace == namespace
        ]

    async def delete(self, memory_id: str) -> bool:
        return self._items.pop(memory_id, None) is not None

    async def count(self) -> int:
        return len(self._items)