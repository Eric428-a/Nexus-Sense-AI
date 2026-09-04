"""
MongoDB infrastructure.

This module intentionally separates connection management from
repository implementations.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase


class MongoDBClient:
    """
    Async MongoDB connection manager.

    The client is deliberately lightweight so repositories can depend
    on the database abstraction instead of constructing connections.
    """

    def __init__(
        self,
        uri: str,
        database_name: str,
        *,
        max_pool_size: int = 50,
        min_pool_size: int = 5,
    ) -> None:
        self.uri = uri
        self.database_name = database_name
        self.max_pool_size = max_pool_size
        self.min_pool_size = min_pool_size

        self._client: AsyncIOMotorClient | None = None
        self._database: AsyncIOMotorDatabase | None = None

    @property
    def client(self) -> AsyncIOMotorClient:
        if self._client is None:
            raise RuntimeError("MongoDB client has not been connected.")
        return self._client

    @property
    def database(self) -> AsyncIOMotorDatabase:
        if self._database is None:
            raise RuntimeError("MongoDB database has not been initialized.")
        return self._database

    @property
    def connected(self) -> bool:
        return self._client is not None

    async def connect(self) -> None:
        """Create the MongoDB client."""
        if self._client is not None:
            return

        self._client = AsyncIOMotorClient(
            self.uri,
            maxPoolSize=self.max_pool_size,
            minPoolSize=self.min_pool_size,
        )

        self._database = self._client[self.database_name]

    async def disconnect(self) -> None:
        """Close the MongoDB client."""
        if self._client is not None:
            self._client.close()

        self._client = None
        self._database = None

    async def ping(self) -> bool:
        """Check whether MongoDB responds to a ping."""
        if self._client is None:
            return False

        try:
            await self._client.admin.command("ping")
            return True
        except Exception:
            return False

    def collection(self, name: str) -> Any:
        """Return a MongoDB collection."""
        return self.database[name]

    @asynccontextmanager
    async def lifespan(self) -> AsyncIterator["MongoDBClient"]:
        """Convenience lifecycle context."""
        await self.connect()

        try:
            yield self
        finally:
            await self.disconnect()