"""
PostgreSQL infrastructure.

SQLAlchemy is used as the database abstraction so the rest of the
application does not depend directly on a particular PostgreSQL driver.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


class PostgreSQLClient:
    """
    Async PostgreSQL database manager.
    """

    def __init__(
        self,
        database_url: str,
        *,
        echo: bool = False,
        pool_size: int = 10,
        max_overflow: int = 20,
    ) -> None:
        self.database_url = database_url

        self.engine: AsyncEngine = create_async_engine(
            database_url,
            echo=echo,
            pool_size=pool_size,
            max_overflow=max_overflow,
        )

        self.session_factory = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    async def healthcheck(self) -> bool:
        """Check PostgreSQL connectivity."""
        try:
            async with self.engine.connect() as connection:
                await connection.execute(text("SELECT 1"))

            return True

        except Exception:
            return False

    @asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        """Provide a transactional database session."""
        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    async def dispose(self) -> None:
        """Dispose the connection pool."""
        await self.engine.dispose()