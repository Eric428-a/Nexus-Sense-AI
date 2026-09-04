"""
Short-term agent working memory.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from nexus.utils.timestamps import utc_now


@dataclass(slots=True)
class MemoryItem:
    """A temporary item held in an agent's working context."""

    key: str
    value: Any
    created_at: datetime = field(default_factory=utc_now)
    metadata: dict[str, Any] = field(default_factory=dict)


class ShortTermMemory:
    """
    Bounded working memory.

    This memory is intended for the current task, investigation,
    conversation, or agent execution.
    """

    def __init__(self, max_items: int = 100) -> None:
        if max_items <= 0:
            raise ValueError("max_items must be greater than zero.")

        self.max_items = max_items
        self._items: deque[MemoryItem] = deque(maxlen=max_items)

    def put(
        self,
        key: str,
        value: Any,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> MemoryItem:

        item = MemoryItem(
            key=key,
            value=value,
            metadata=metadata or {},
        )

        self._items.append(item)
        return item

    def get(self, key: str) -> MemoryItem | None:
        for item in reversed(self._items):
            if item.key == key:
                return item

        return None

    def latest(self, limit: int = 10) -> list[MemoryItem]:
        return list(self._items)[-limit:]

    def all(self) -> list[MemoryItem]:
        return list(self._items)

    def clear(self) -> None:
        self._items.clear()

    def __len__(self) -> int:
        return len(self._items)