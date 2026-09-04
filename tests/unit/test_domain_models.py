from datetime import datetime, timezone

from src.nexus.extraction.entities import Entity
from src.nexus.extraction.events import Event
from src.nexus.extraction.relations import Relationship
from src.nexus.intelligence.confidence import ConfidenceScore
from src.nexus.intelligence.pipeline import IntelligenceInput
from src.nexus.reasoning.evidence import Evidence
from src.nexus.reasoning.finding import Finding
from src.nexus.reasoning.hypothesis import Hypothesis
from src.nexus.reasoning.report import IntelligenceReport


def test_entity_generates_identifier() -> None:
    entity = Entity(
        name="Example Organization",
        entity_type="organization",
    )

    assert entity.id.startswith("ent_")
    assert entity.name == "Example Organization"


def test_entity_can_attach_sources() -> None:
    entity = Entity(
        name="Example",
        entity_type="concept",
    )

    entity.add_source("source_001")
    entity.add_source("source_001")
    entity.add_source("source_002")

    assert entity.source_ids == [
        "source_001",
        "source_002",
    ]


def test_relationship_creation() -> None:
    relationship = Relationship(
        source_entity_id="ent_a",
        target_entity_id="ent_b",
        relationship_type="associated_with",
        confidence=0.82,
    )

    assert relationship.id.startswith("rel_")
    assert relationship.confidence == 0.82


def test_event_can_attach_entities() -> None:
    event = Event(
        event_type="announcement",
        title="Example Event",
    )

    event.add_entity("ent_001")
    event.add_entity("ent_001")
    event.add_entity("ent_002")

    assert event.entity_ids == [
        "ent_001",
        "ent_002",
    ]


def test_evidence_supports_target() -> None:
    evidence = Evidence(
        source_id="source_001",
        evidence_type="document",
        content="Example evidence.",
        reliability=0.9,
        relevance=0.8,
    )

    evidence.support("hyp_001")

    assert "hyp_001" in evidence.supports


def test_hypothesis_tracks_supporting_evidence() -> None:
    hypothesis = Hypothesis(
        statement="An example hypothesis.",
    )

    hypothesis.add_evidence(
        "evd_001",
        supports=True,
    )

    assert "evd_001" in hypothesis.evidence_ids
    assert "evd_001" in hypothesis.supporting_evidence_ids


def test_finding_accepts_evidence() -> None:
    finding = Finding(
        title="Example Finding",
        statement="An example finding.",
        category="general",
    )

    finding.add_evidence("evd_001")

    assert finding.evidence_ids == ["evd_001"]


def test_confidence_level() -> None:
    confidence = ConfidenceScore(
        value=0.91,
        evidence_strength=0.9,
        source_reliability=0.95,
        consistency=0.88,
    )

    assert confidence.level == "very_high"


def test_intelligence_input_generates_identifier() -> None:
    intelligence_input = IntelligenceInput(
        query="What patterns are present?",
    )

    assert intelligence_input.id.startswith("intel_")


def test_report_can_be_finalized() -> None:
    report = IntelligenceReport(
        title="Example Intelligence Report",
        executive_summary="Example summary.",
    )

    report.finalize()

    assert report.status == "finalized"
    assert isinstance(report.finalized_at, datetime)
    assert report.finalized_at.tzinfo == timezone.utc