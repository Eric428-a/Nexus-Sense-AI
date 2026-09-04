"""
Contracts for the NEXUS-SENSE intelligence pipeline.

The pipeline coordinates transformations between ingestion,
extraction, reasoning, verification, decision, and reporting.
"""

from datetime import datetime
from typing import Any, Dict

from pydantic import BaseModel, ConfigDict, Field

from nexus.extraction.entities import Entity
from nexus.extraction.events import Event
from nexus.extraction.relations import Relationship
from nexus.reasoning.evidence import Evidence
from nexus.reasoning.finding import Finding
from nexus.reasoning.hypothesis import Hypothesis
from nexus.utils.ids import generate_id
from nexus.utils.timestamps import utc_now


class IntelligenceInput(BaseModel):
    """
    Input entering the intelligence pipeline.
    """

    model_config = ConfigDict(extra="ignore")

    id: str = Field(default_factory=lambda: generate_id("intel"))

    query: str | None = None

    source_ids: list[str] = Field(default_factory=list)

    content: list[str] = Field(default_factory=list)

    context: Dict[str, Any] = Field(default_factory=dict)

    created_at: datetime = Field(default_factory=utc_now)


class IntelligencePipelineResult(BaseModel):
    """
    Aggregate output of the intelligence pipeline.
    """

    model_config = ConfigDict(extra="ignore")

    id: str = Field(default_factory=lambda: generate_id("result"))

    input_id: str

    entities: list[Entity] = Field(default_factory=list)

    relationships: list[Relationship] = Field(default_factory=list)

    events: list[Event] = Field(default_factory=list)

    evidence: list[Evidence] = Field(default_factory=list)

    hypotheses: list[Hypothesis] = Field(default_factory=list)

    findings: list[Finding] = Field(default_factory=list)

    overall_confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
    )

    status: str = "initialized"

    stages_completed: list[str] = Field(default_factory=list)

    warnings: list[str] = Field(default_factory=list)

    metadata: Dict[str, Any] = Field(default_factory=dict)

    created_at: datetime = Field(default_factory=utc_now)

    completed_at: datetime | None = None

    def mark_stage_complete(self, stage: str) -> None:
        """Record completion of an intelligence stage."""
        if stage not in self.stages_completed:
            self.stages_completed.append(stage)

    def complete(self) -> None:
        """Mark the pipeline execution as completed."""
        self.status = "completed"
        self.completed_at = utc_now()