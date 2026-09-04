"""
Document persistence abstraction.
"""

from __future__ import annotations

from typing import Any

from nexus.ingestion.base import SourceDocument


class DocumentRepository:
    """
    Repository for source documents.

    The initial implementation is in-memory so the architecture can
    be tested independently of MongoDB.
    """

    def __init__(self) -> None:
        self._documents: dict[str, SourceDocument] = {}

    async def get(self, document_id: str) -> SourceDocument | None:
        return self._documents.get(document_id)

    async def save(self, document: SourceDocument) -> SourceDocument:
        self._documents[document.id] = document
        return document

    async def delete(self, document_id: str) -> bool:
        return self._documents.pop(document_id, None) is not None

    async def exists(self, document_id: str) -> bool:
        return document_id in self._documents

    async def list(
        self,
        *,
        tags: list[str] | None = None,
        limit: int = 100,
    ) -> list[SourceDocument]:

        documents = list(self._documents.values())

        if tags:
            required_tags = set(tags)

            documents = [
                document
                for document in documents
                if required_tags.intersection(document.tags)
            ]

        return documents[:limit]

    async def count(self) -> int:
        return len(self._documents)

    async def metadata(self, document_id: str) -> dict[str, Any]:
        document = await self.get(document_id)

        if document is None:
            return {}

        return {
            "id": document.id,
            "title": document.title,
            "source_type": document.source_type.value,
            "uri": document.uri,
            "mime_type": document.mime_type,
            "language": document.language,
            "tags": document.tags,
        }