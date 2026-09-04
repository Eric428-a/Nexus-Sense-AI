"""
Intelligence report models.
"""

from datetime import datetime
from typing import Any, Dict

from pydantic import BaseModel, ConfigDict, Field

from nexus.reasoning.finding import Finding
from nexus.utils.ids import generate_id
from nexus.utils.timestamps import utc_now


class IntelligenceReport(BaseModel):
    """
    Final structured intelligence report.
    """

    model_config = ConfigDict(extra="ignore")

    id: str = Field(default_factory=lambda: generate_id("rpt"))

    title: str

    executive_summary: str

    findings: list[Finding] = Field(default_factory=list)

    key_entities: list[str] = Field(default_factory=list)

    key_events: list[str] = Field(default_factory=list)

    recommendations: list[str] = Field(default_factory=list)

    limitations: list[str] = Field(default_factory=list)

    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
    )

    status: str = "draft"

    metadata: Dict[str, Any] = Field(default_factory=dict)

    generated_at: datetime = Field(default_factory=utc_now)

    finalized_at: datetime | None = None

    def add_finding(self, finding: Finding) -> None:
        """Add a finding to the report."""
        self.findings.append(finding)

    def finalize(self) -> None:
        """Finalize the report."""
        self.status = "finalized"
        self.finalized_at = utc_now()