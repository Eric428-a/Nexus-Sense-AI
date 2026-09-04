"""
Web ingestion loader.

Fetches textual web resources and converts them into normalized
source documents.
"""

from time import perf_counter

import httpx

from .base import (
    BaseLoader,
    ContentChunk,
    IngestionRequest,
    IngestionResult,
    SourceType,
)


class WebLoader(BaseLoader):
    """Loader for HTTP/HTTPS resources."""

    source_type = SourceType.WEB

    def __init__(
        self,
        *,
        timeout: float = 20.0,
        chunk_size: int = 1500,
        chunk_overlap: int = 150,
    ) -> None:
        self.timeout = timeout
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    async def load(
        self,
        request: IngestionRequest,
    ) -> IngestionResult:
        """Fetch and normalize a web resource."""
        started = perf_counter()

        if not request.uri:
            return IngestionResult(
                request_id=request.id,
                success=False,
                errors=["Web ingestion requires a URI."],
            )

        try:
            async with httpx.AsyncClient(
                timeout=self.timeout,
                follow_redirects=True,
            ) as client:
                response = await client.get(request.uri)
                response.raise_for_status()

            content_type = response.headers.get(
                "content-type",
                "",
            )

            content = response.text

            document = self.create_document(
                content=content,
                title=request.title or request.uri,
                uri=str(response.url),
                mime_type=content_type,
                metadata={
                    **request.metadata,
                    "http_status": response.status_code,
                    "content_type": content_type,
                },
            )

            chunks = self._chunk(
                content,
                document.id,
            )

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

        except httpx.HTTPError as exc:
            return IngestionResult(
                request_id=request.id,
                success=False,
                errors=[f"HTTP ingestion failed: {exc}"],
            )

    def _chunk(
        self,
        content: str,
        source_id: str,
    ) -> list[ContentChunk]:
        """Chunk fetched web content."""
        chunks: list[ContentChunk] = []

        start = 0
        index = 0

        while start < len(content):
            end = min(
                start + self.chunk_size,
                len(content),
            )

            text = content[start:end].strip()

            if text:
                chunks.append(
                    ContentChunk(
                        source_id=source_id,
                        content=text,
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