"""
Relationship domain models.

Relationships describe connections between entities.
"""

from datetime import datetime
from typing import Any, Dict

from pydantic import BaseModel, ConfigDict, Field

from nexus.utils.ids import generate_id
from nexus.utils.timestamps import utc_now


class Relationship(BaseModel):
    """
    Directed relationship between two entities.
    """

    model_config = ConfigDict(extra="ignore")

    id: str = Field(default_factory=lambda: generate_id("rel"))

    source_entity_id: str
    target_entity_id: str

    relationship_type: str

    description: str | None = None

    attributes: Dict[str, Any] = Field(default_factory=dict)

    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
    )

    source_ids: list[str] = Field(default_factory=list)

    valid_from: datetime | None = None
    valid_until: datetime | None = None

    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

    def add_source(self, source_id: str) -> None:
        """Associate supporting evidence with the relationship."""
        if source_id and source_id not in self.source_ids:
            self.source_ids.append(source_id)
            self.updated_at = utc_now()