"""
Document ingestion.

Handles textual documents and common document formats.
"""

from pathlib import Path
from time import perf_counter

from nexus.utils.ids import generate_id

from .base import (
    BaseLoader,
    ContentChunk,
    IngestionRequest,
    IngestionResult,
    SourceType,
)


class DocumentLoader(BaseLoader):
    """
    Loader for local textual documents.

    PDF and DOCX support can be extended through dedicated
    adapters while preserving the same normalized output.
    """

    source_type = SourceType.DOCUMENT

    SUPPORTED_TEXT_EXTENSIONS = {
        ".txt",
        ".md",
        ".markdown",
        ".json",
        ".xml",
        ".html",
        ".htm",
        ".yaml",
        ".yml",
        ".log",
    }

    def __init__(
        self,
        *,
        chunk_size: int = 1500,
        chunk_overlap: int = 150,
    ) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than zero.")

        if chunk_overlap < 0:
            raise ValueError("chunk_overlap cannot be negative.")

        if chunk_overlap >= chunk_size:
            raise ValueError(
                "chunk_overlap must be smaller than chunk_size."
            )

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    async def load(
        self,
        request: IngestionRequest,
    ) -> IngestionResult:
        """Load a document from content or a local URI."""
        started = perf_counter()

        try:
            content = await self._read_content(request)

            document = self.create_document(
                content=content,
                title=request.title,
                uri=request.uri,
                metadata=request.metadata,
            )

            chunks = self._chunk_document(document.content, document.id)

            for chunk in chunks:
                document.add_chunk(chunk)

            elapsed_ms = (perf_counter() - started) * 1000

            return IngestionResult(
                request_id=request.id,
                success=True,
                documents=[document],
                chunks=chunks,
                processing_time_ms=elapsed_ms,
            )

        except Exception as exc:
            elapsed_ms = (perf_counter() - started) * 1000

            return IngestionResult(
                request_id=request.id,
                success=False,
                errors=[str(exc)],
                processing_time_ms=elapsed_ms,
            )

    async def _read_content(
        self,
        request: IngestionRequest,
    ) -> str:
        """Read source content."""
        if request.content is not None:
            return request.content

        if not request.uri:
            raise ValueError(
                "Document ingestion requires either content or uri."
            )

        path = Path(request.uri)

        if not path.exists():
            raise FileNotFoundError(
                f"Document does not exist: {request.uri}"
            )

        if not path.is_file():
            raise ValueError(
                f"Document URI is not a file: {request.uri}"
            )

        if path.suffix.lower() not in self.SUPPORTED_TEXT_EXTENSIONS:
            raise ValueError(
                f"Unsupported document extension: {path.suffix}"
            )

        return path.read_text(
            encoding="utf-8",
            errors="replace",
        )

    def _chunk_document(
        self,
        content: str,
        source_id: str,
    ) -> list[ContentChunk]:
        """Split content into overlapping chunks."""
        if not content.strip():
            return []

        chunks: list[ContentChunk] = []

        start = 0
        index = 0

        while start < len(content):
            end = min(
                start + self.chunk_size,
                len(content),
            )

            chunk_text = content[start:end].strip()

            if chunk_text:
                chunks.append(
                    ContentChunk(
                        id=generate_id("chunk"),
                        source_id=source_id,
                        content=chunk_text,
                        index=index,
                        start_offset=start,
                        end_offset=end,
                        metadata={
                            "chunking_strategy": "character_window",
                        },
                    )
                )

                index += 1

            if end >= len(content):
                break

            start = end - self.chunk_overlap

        return chunks