"""
Persistence infrastructure for NEXUS-SENSE AI.

The database package provides backend-agnostic interfaces for:

- MongoDB
- PostgreSQL
- Vector databases
- Repository abstractions
"""

from nexus.database.mongodb import MongoDBClient
from nexus.database.postgres import PostgreSQLClient
from nexus.database.vector_store import (
    InMemoryVectorStore,
    VectorRecord,
    VectorSearchResult,
    VectorStore,
)

__all__ = [
    "MongoDBClient",
    "PostgreSQLClient",
    "InMemoryVectorStore",
    "VectorRecord",
    "VectorSearchResult",
    "VectorStore",
]