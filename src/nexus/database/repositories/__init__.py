"""
Repository layer.

Repositories isolate persistence from business logic.
"""

from nexus.database.repositories.base import Repository
from nexus.database.repositories.documents import DocumentRepository
from nexus.database.repositories.entities import EntityRepository
from nexus.database.repositories.reports import ReportRepository

__all__ = [
    "Repository",
    "DocumentRepository",
    "EntityRepository",
    "ReportRepository",
]