"""
Schemas representing extraction requests and results.
"""

from datetime import datetime
from typing import Any, Dict

from pydantic import BaseModel, ConfigDict, Field

from .entities import Entity
from .events import Event
from .metadata import ExtractionMetadata, SourceMetadata
from .relations import Relationship


class ExtractionRequest(BaseModel):
    """
    Input supplied to an extraction component.
    """

    model_config = ConfigDict(extra="ignore")

    source_id: str

    content: str

    metadata: SourceMetadata | None = None

    extraction_types: list[str] = Field(
        default_factory=lambda: [
            "entities",
            "relationships",
            "events",
        ]
    )

    options: Dict[str, Any] = Field(default_factory=dict)


class ExtractionResult(BaseModel):
    """
    Complete structured result produced by extraction.
    """

    model_config = ConfigDict(extra="ignore")

    request_id: str

    source_id: str

    entities: list[Entity] = Field(default_factory=list)

    relationships: list[Relationship] = Field(default_factory=list)

    events: list[Event] = Field(default_factory=list)

    metadata: ExtractionMetadata | None = None

    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
    )

    warnings: list[str] = Field(default_factory=list)

    created_at: datetime