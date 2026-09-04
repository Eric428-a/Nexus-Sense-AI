"""
Entity domain models.

Entities represent identifiable people, organizations, places,
products, concepts, technologies, or other objects discovered
during intelligence processing.
"""

from datetime import datetime
from typing import Any, Dict, List

from pydantic import BaseModel, ConfigDict, Field

from nexus.utils.ids import generate_id
from nexus.utils.timestamps import utc_now


class EntityMention(BaseModel):
    """
    A textual occurrence of an entity inside a source.
    """

    model_config = ConfigDict(extra="ignore")

    text: str
    source_id: str
    start_offset: int | None = None
    end_offset: int | None = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class Entity(BaseModel):
    """
    Canonical representation of an extracted entity.
    """

    model_config = ConfigDict(extra="ignore")

    id: str = Field(default_factory=lambda: generate_id("ent"))

    name: str
    entity_type: str

    description: str | None = None

    aliases: List[str] = Field(default_factory=list)
    mentions: List[EntityMention] = Field(default_factory=list)

    attributes: Dict[str, Any] = Field(default_factory=dict)

    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
    )

    source_ids: List[str] = Field(default_factory=list)

    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

    def add_alias(self, alias: str) -> None:
        """Add an alias if it is not already registered."""
        if alias and alias not in self.aliases:
            self.aliases.append(alias)
            self.updated_at = utc_now()

    def add_source(self, source_id: str) -> None:
        """Associate the entity with a source."""
        if source_id and source_id not in self.source_ids:
            self.source_ids.append(source_id)
            self.updated_at = utc_now()

    def add_mention(self, mention: EntityMention) -> None:
        """Attach an observed mention to the entity."""
        self.mentions.append(mention)
        self.updated_at = utc_now()