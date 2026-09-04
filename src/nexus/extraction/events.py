"""
Event domain models.

Events represent occurrences identified in source material.
"""

from datetime import datetime
from typing import Any, Dict

from pydantic import BaseModel, ConfigDict, Field

from nexus.utils.ids import generate_id
from nexus.utils.timestamps import utc_now


class Event(BaseModel):
    """
    Structured representation of an observed event.
    """

    model_config = ConfigDict(extra="ignore")

    id: str = Field(default_factory=lambda: generate_id("evt"))

    event_type: str
    title: str

    description: str | None = None

    timestamp: datetime | None = None
    end_timestamp: datetime | None = None

    location: str | None = None

    entity_ids: list[str] = Field(default_factory=list)

    attributes: Dict[str, Any] = Field(default_factory=dict)

    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
    )

    source_ids: list[str] = Field(default_factory=list)

    created_at: datetime = Field(default_factory=utc_now)

    def add_entity(self, entity_id: str) -> None:
        """Attach an entity participating in the event."""
        if entity_id and entity_id not in self.entity_ids:
            self.entity_ids.append(entity_id)

    def add_source(self, source_id: str) -> None:
        """Attach a supporting source."""
        if source_id and source_id not in self.source_ids:
            self.source_ids.append(source_id)