"""
Finding domain models.

A finding represents a reasoned conclusion derived from evidence.
"""

from datetime import datetime
from typing import Any, Dict

from pydantic import BaseModel, ConfigDict, Field

from nexus.utils.ids import generate_id
from nexus.utils.timestamps import utc_now


class Finding(BaseModel):
    """
    Structured intelligence finding.
    """

    model_config = ConfigDict(extra="ignore")

    id: str = Field(default_factory=lambda: generate_id("fnd"))

    title: str

    statement: str

    category: str

    severity: str = "medium"

    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
    )

    evidence_ids: list[str] = Field(default_factory=list)

    entity_ids: list[str] = Field(default_factory=list)

    hypothesis_ids: list[str] = Field(default_factory=list)

    implications: list[str] = Field(default_factory=list)

    recommendations: list[str] = Field(default_factory=list)

    attributes: Dict[str, Any] = Field(default_factory=dict)

    created_at: datetime = Field(default_factory=utc_now)

    def add_evidence(self, evidence_id: str) -> None:
        """Attach evidence to the finding."""
        if evidence_id and evidence_id not in self.evidence_ids:
            self.evidence_ids.append(evidence_id)

    def add_entity(self, entity_id: str) -> None:
        """Attach an entity to the finding."""
        if entity_id and entity_id not in self.entity_ids:
            self.entity_ids.append(entity_id)

    def add_hypothesis(self, hypothesis_id: str) -> None:
        """Attach a hypothesis to the finding."""
        if hypothesis_id and hypothesis_id not in self.hypothesis_ids:
            self.hypothesis_ids.append(hypothesis_id)