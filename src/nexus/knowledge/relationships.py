"""
Knowledge graph relationship models.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from nexus.utils.ids import generate_id
from nexus.utils.timestamps import utc_now


class KnowledgeRelationship(BaseModel):
    """Directed relationship between two knowledge entities."""

    relationship_id: str = Field(
        default_factory=generate_id
    )

    source_entity_id: str

    target_entity_id: str

    relationship_type: str

    description: str | None = None

    properties: dict[str, Any] = Field(
        default_factory=dict
    )

    source_ids: list[str] = Field(
        default_factory=list
    )

    confidence: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
    )

    created_at: datetime = Field(
        default_factory=utc_now
    )

    updated_at: datetime = Field(
        default_factory=utc_now
    )

    def add_source(self, source_id: str) -> None:
        """Associate relationship with a source."""
        if source_id not in self.source_ids:
            self.source_ids.append(source_id)

        self.updated_at = utc_now()