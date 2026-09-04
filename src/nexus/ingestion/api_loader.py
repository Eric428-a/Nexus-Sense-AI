"""
API ingestion loader.

Provides generic HTTP API ingestion with JSON normalization.
"""

import json
from time import perf_counter
from typing import Any

import httpx

from .base import (
    BaseLoader,
    ContentChunk,
    IngestionRequest,
    IngestionResult,
    SourceType,
)


class APIDataLoader(BaseLoader):
    """Loader for HTTP API responses."""

    source_type = SourceType.API

    def __init__(
        self,
        *,
        timeout: float = 20.0,
    ) -> None:
        self.timeout = timeout

    async def load(
        self,
        request: IngestionRequest,
    ) -> IngestionResult:
        """Fetch and normalize an API response."""
        started = perf_counter()

        if not request.uri:
            return IngestionResult(
                request_id=request.id,
                success=False,
                errors=["API ingestion requires a URI."],
            )

        try:
            headers = request.options.get(
                "headers",
                {},
            )

            params = request.options.get(
                "params",
                {},
            )

            method = str(
                request.options.get(
                    "method",
                    "GET",
                )
            ).upper()

            async with httpx.AsyncClient(
                timeout=self.timeout,
            ) as client:
                response = await client.request(
                    method,
                    request.uri,
                    headers=headers,
                    params=params,
                    json=request.options.get("json"),
                )

                response.raise_for_status()

            payload = response.json()

            content = self._serialize_payload(payload)

            document = self.create_document(
                content=content,
                title=request.title or "API Response",
                uri=request.uri,
                mime_type="application/json",
                metadata={
                    **request.metadata,
                    "http_status": response.status_code,
                    "method": method,
                },
            )

            chunk = ContentChunk(
                source_id=document.id,
                content=content,
                index=0,
                token_count=None,
                metadata={
                    "source": "api",
                    "response_type": type(payload).__name__,
                },
            )

            document.add_chunk(chunk)

            elapsed_ms = (perf_counter() - started) * 1000

            return IngestionResult(
                request_id=request.id,
                success=True,
                documents=[document],
                chunks=[chunk],
                processing_time_ms=elapsed_ms,
            )

        except (httpx.HTTPError, ValueError, TypeError) as exc:
            return IngestionResult(
                request_id=request.id,
                success=False,
                errors=[f"API ingestion failed: {exc}"],
            )

    @staticmethod
    def _serialize_payload(payload: Any) -> str:
        """Convert an API payload into normalized text."""
        return json.dumps(
            payload,
            ensure_ascii=False,
            indent=2,
            default=str,
        )