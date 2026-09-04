"""
Confidence scoring models.

Confidence is represented explicitly rather than hidden inside
individual agents or pipelines.
"""

from pydantic import BaseModel, ConfigDict, Field


class ConfidenceScore(BaseModel):
    """
    Structured confidence assessment.
    """

    model_config = ConfigDict(extra="ignore")

    value: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
    )

    evidence_strength: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
    )

    source_reliability: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
    )

    consistency: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
    )

    explanation: str | None = None

    @property
    def level(self) -> str:
        """Return a human-readable confidence level."""
        if self.value >= 0.90:
            return "very_high"

        if self.value >= 0.75:
            return "high"

        if self.value >= 0.50:
            return "medium"

        return "low"