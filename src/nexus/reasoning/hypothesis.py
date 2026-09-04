"""
Hypothesis domain models.
"""

from datetime import datetime
from typing import Any, Dict

from pydantic import BaseModel, ConfigDict, Field

from nexus.utils.ids import generate_id
from nexus.utils.timestamps import utc_now


class Hypothesis(BaseModel):
    """
    A candidate explanation generated during reasoning.
    """

    model_config = ConfigDict(extra="ignore")

    id: str = Field(default_factory=lambda: generate_id("hyp"))

    statement: str

    rationale: str | None = None

    evidence_ids: list[str] = Field(default_factory=list)

    supporting_evidence_ids: list[str] = Field(default_factory=list)
    contradicting_evidence_ids: list[str] = Field(default_factory=list)

    probability: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
    )

    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
    )

    status: str = "candidate"

    attributes: Dict[str, Any] = Field(default_factory=dict)

    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

    def add_evidence(
        self,
        evidence_id: str,
        *,
        supports: bool,
    ) -> None:
        """Associate evidence with this hypothesis."""
        if evidence_id not in self.evidence_ids:
            self.evidence_ids.append(evidence_id)

        target = (
            self.supporting_evidence_ids
            if supports
            else self.contradicting_evidence_ids
        )

        if evidence_id not in target:
            target.append(evidence_id)

        self.updated_at = utc_now()