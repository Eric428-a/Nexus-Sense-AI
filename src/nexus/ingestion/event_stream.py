"""
Event-stream ingestion.

Provides a lightweight abstraction for normalizing incoming
events before they enter the intelligence pipeline.
"""

import json
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from nexus.utils.ids import generate_id
from nexus.utils.timestamps import utc_now

from .base import (
    BaseLoader,
    ContentChunk,
    IngestionRequest,
    IngestionResult,
    SourceType,
)


class StreamEvent(BaseModel):
    """Normalized event-stream message."""

    model_config = ConfigDict(extra="ignore")

    id: str = Field(default_factory=lambda: generate_id("stream"))

    event_type: str

    payload: dict[str, Any] = Field(default_factory=dict)

    timestamp: datetime = Field(default_factory=utc_now)

    source: str | None = None

    metadata: dict[str, Any] = Field(default_factory=dict)


class EventStreamLoader(BaseLoader):
    """
    Loader for discrete event payloads.

    Transport-specific implementations can later connect Kafka,
    Redis Streams, WebSockets, queues, or other event systems.
    """

    source_type = SourceType.EVENT_STREAM

    async def load(
        self,
        request: IngestionRequest,
    ) -> IngestionResult:
        """Normalize an incoming stream event."""
        if request.content is None:
            return IngestionResult(
                request_id=request.id,
                success=False,
                errors=[
                    "Event stream ingestion requires event content."
                ],
            )

        try:
            payload = json.loads(request.content)

            if not isinstance(payload, dict):
                raise ValueError(
                    "Event payload must be a JSON object."
                )

            event = StreamEvent(
                event_type=str(
                    payload.get(
                        "event_type",
                        "unknown",
                    )
                ),
                payload=payload.get(
                    "payload",
                    payload,
                ),
                source=payload.get("source"),
                metadata={
                    **request.metadata,
                    **payload.get("metadata", {}),
                },
            )

            content = json.dumps(
                event.model_dump(mode="json"),
                ensure_ascii=False,
                indent=2,
            )

            document = self.create_document(
                content=content,
                title=request.title or event.event_type,
                uri=request.uri,
                mime_type="application/json",
                metadata={
                    "stream_event_id": event.id,
                    "event_type": event.event_type,
                },
            )

            chunk = ContentChunk(
                source_id=document.id,
                content=content,
                index=0,
                metadata={
                    "event_id": event.id,
                    "event_type": event.event_type,
                },
            )

            document.add_chunk(chunk)

            return IngestionResult(
                request_id=request.id,
                success=True,
                documents=[document],
                chunks=[chunk],
                metadata={
                    "event_id": event.id,
                    "event_type": event.event_type,
                },
            )

        except (json.JSONDecodeError, ValueError, TypeError) as exc:
            return IngestionResult(
                request_id=request.id,
                success=False,
                errors=[
                    f"Event ingestion failed: {exc}"
                ],
            )