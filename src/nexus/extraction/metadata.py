"""
Metadata models used throughout the extraction pipeline.
"""

from datetime import datetime
from typing import Any, Dict

from pydantic import BaseModel, ConfigDict, Field

from nexus.utils.timestamps import utc_now


class SourceMetadata(BaseModel):
    """
    Metadata describing the origin and processing state of a source.
    """

    model_config = ConfigDict(extra="ignore")

    source_id: str

    source_type: str

    title: str | None = None
    uri: str | None = None

    author: str | None = None
    publisher: str | None = None

    language: str | None = None

    published_at: datetime | None = None
    collected_at: datetime = Field(default_factory=utc_now)

    checksum: str | None = None

    tags: list[str] = Field(default_factory=list)

    attributes: Dict[str, Any] = Field(default_factory=dict)


class ExtractionMetadata(BaseModel):
    """
    Metadata describing an extraction operation.
    """

    extractor: str
    extractor_version: str = "0.1.0"

    started_at: datetime
    completed_at: datetime | None = None

    processing_time_ms: float | None = None

    model_name: str | None = None

    token_count: int | None = None

    warnings: list[str] = Field(default_factory=list)

    attributes: Dict[str, Any] = Field(default_factory=dict)