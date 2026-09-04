"""
Evidence domain models.

Evidence is the fundamental support layer for NEXUS-SENSE
reasoning and decision-making.
"""

from datetime import datetime
from typing import Any, Dict

from pydantic import BaseModel, ConfigDict, Field

from nexus.utils.ids import generate_id
from nexus.utils.timestamps import utc_now


class Evidence(BaseModel):
    """
    A discrete piece of information supporting or contradicting
    an intelligence claim.
    """

    model_config = ConfigDict(extra="ignore")

    id: str = Field(default_factory=lambda: generate_id("evd"))

    source_id: str

    evidence_type: str

    title: str | None = None

    content: str

    excerpt: str | None = None

    source_uri: str | None = None

    supports: list[str] = Field(default_factory=list)
    contradicts: list[str] = Field(default_factory=list)

    reliability: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
    )

    relevance: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
    )

    attributes: Dict[str, Any] = Field(default_factory=dict)

    observed_at: datetime | None = None

    created_at: datetime = Field(default_factory=utc_now)

    def support(self, target_id: str) -> None:
        """Mark a target as supported by this evidence."""
        if target_id and target_id not in self.supports:
            self.supports.append(target_id)

    def contradict(self, target_id: str) -> None:
        """Mark a target as contradicted by this evidence."""
        if target_id and target_id not in self.contradicts:
            self.contradicts.append(target_id)