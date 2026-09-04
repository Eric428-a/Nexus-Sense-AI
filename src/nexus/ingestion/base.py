"""
Core ingestion contracts.

Every ingestion source is normalized into the same domain
representation so downstream components do not need to know
where the information originated.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any, Dict

from pydantic import BaseModel, ConfigDict, Field

from nexus.utils.ids import generate_id
from nexus.utils.hashing import content_fingerprint
from nexus.utils.timestamps import utc_now


class SourceType(str, Enum):
    """Supported source categories."""

    DOCUMENT = "document"
    WEB = "web"
    API = "api"
    CSV = "csv"
    EVENT_STREAM = "event_stream"
    DATABASE = "database"
    MANUAL = "manual"
    UNKNOWN = "unknown"


class ContentChunk(BaseModel):
    """
    A normalized piece of source content.

    Chunks are intentionally source-agnostic so retrieval,
    embedding, and extraction can operate uniformly.
    """

    model_config = ConfigDict(extra="ignore")

    id: str = Field(default_factory=lambda: generate_id("chunk"))

    source_id: str
    content: str

    index: int = 0

    start_offset: int | None = None
    end_offset: int | None = None

    token_count: int | None = None

    metadata: Dict[str, Any] = Field(default_factory=dict)

    created_at: datetime = Field(default_factory=utc_now)

    @property
    def fingerprint(self) -> str:
        """Return a stable fingerprint for this chunk."""
        return content_fingerprint(self.content)


class SourceDocument(BaseModel):
    """
    Canonical representation of an ingested source.
    """

    model_config = ConfigDict(extra="ignore")

    id: str = Field(default_factory=lambda: generate_id("src"))

    source_type: SourceType

    title: str | None = None

    content: str

    uri: str | None = None

    mime_type: str | None = None

    encoding: str = "utf-8"

    author: str | None = None
    publisher: str | None = None
    language: str | None = None

    published_at: datetime | None = None

    collected_at: datetime = Field(default_factory=utc_now)

    checksum: str | None = None

    tags: list[str] = Field(default_factory=list)

    metadata: Dict[str, Any] = Field(default_factory=dict)

    chunks: list[ContentChunk] = Field(default_factory=list)

    def model_post_init(self, __context: Any) -> None:
        """
        Generate a content checksum after model initialization.
        """
        if not self.checksum:
            self.checksum = content_fingerprint(self.content)

    def add_chunk(self, chunk: ContentChunk) -> None:
        """Attach a normalized content chunk."""
        self.chunks.append(chunk)

    def add_tag(self, tag: str) -> None:
        """Attach a tag if it does not already exist."""
        if tag and tag not in self.tags:
            self.tags.append(tag)


class IngestionRequest(BaseModel):
    """
    Generic ingestion request.
    """

    model_config = ConfigDict(extra="ignore")

    id: str = Field(default_factory=lambda: generate_id("ing"))

    source_type: SourceType

    uri: str | None = None

    content: str | None = None

    title: str | None = None

    options: Dict[str, Any] = Field(default_factory=dict)

    metadata: Dict[str, Any] = Field(default_factory=dict)

    created_at: datetime = Field(default_factory=utc_now)


class IngestionResult(BaseModel):
    """
    Result returned by an ingestion operation.
    """

    model_config = ConfigDict(extra="ignore")

    request_id: str

    success: bool

    documents: list[SourceDocument] = Field(default_factory=list)

    chunks: list[ContentChunk] = Field(default_factory=list)

    errors: list[str] = Field(default_factory=list)

    warnings: list[str] = Field(default_factory=list)

    processing_time_ms: float | None = None

    metadata: Dict[str, Any] = Field(default_factory=dict)

    created_at: datetime = Field(default_factory=utc_now)


class BaseLoader(ABC):
    """
    Abstract base class for all ingestion loaders.

    Implementations convert external source formats into
    SourceDocument objects.
    """

    source_type: SourceType

    @abstractmethod
    async def load(
        self,
        request: IngestionRequest,
    ) -> IngestionResult:
        """
        Load and normalize a source.

        Implementations should never expose source-specific
        representations to downstream components.
        """
        raise NotImplementedError

    def create_document(
        self,
        *,
        content: str,
        title: str | None = None,
        uri: str | None = None,
        mime_type: str | None = None,
        metadata: Dict[str, Any] | None = None,
    ) -> SourceDocument:
        """Create a normalized source document."""
        return SourceDocument(
            source_type=self.source_type,
            content=content,
            title=title,
            uri=uri,
            mime_type=mime_type,
            metadata=metadata or {},
        )