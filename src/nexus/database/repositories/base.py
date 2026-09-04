"""
Generic repository abstractions.
"""

from __future__ import annotations

from typing import Generic, Protocol, TypeVar


EntityT = TypeVar("EntityT")
IDT = TypeVar("IDT")


class Repository(Protocol, Generic[EntityT, IDT]):
    """Generic repository contract."""

    async def get(self, entity_id: IDT) -> EntityT | None:
        ...

    async def save(self, entity: EntityT) -> EntityT:
        ...

    async def delete(self, entity_id: IDT) -> bool:
        ...

    async def exists(self, entity_id: IDT) -> bool:
        ...