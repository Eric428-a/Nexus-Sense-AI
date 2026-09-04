"""
System-wide constants for NEXUS-SENSE AI.
"""

# ----------------------------------------------------------------------
# System identity
# ----------------------------------------------------------------------

SYSTEM_NAME = "NEXUS-SENSE AI"
SYSTEM_VERSION = "0.1.0"

# ----------------------------------------------------------------------
# Intelligence lifecycle
# ----------------------------------------------------------------------

INTELLIGENCE_STAGES = (
    "ingest",
    "normalize",
    "extract",
    "enrich",
    "retrieve",
    "reason",
    "verify",
    "score",
    "decide",
    "report",
)

# ----------------------------------------------------------------------
# Agent identifiers
# ----------------------------------------------------------------------

AGENT_RESEARCH = "research_agent"
AGENT_EXTRACTION = "extraction_agent"
AGENT_REASONING = "reasoning_agent"
AGENT_ANOMALY = "anomaly_agent"
AGENT_VERIFICATION = "verification_agent"
AGENT_REPORT = "report_agent"
AGENT_DECISION = "decision_agent"

AGENT_TYPES = (
    AGENT_RESEARCH,
    AGENT_EXTRACTION,
    AGENT_REASONING,
    AGENT_ANOMALY,
    AGENT_VERIFICATION,
    AGENT_REPORT,
    AGENT_DECISION,
)

# ----------------------------------------------------------------------
# Evidence
# ----------------------------------------------------------------------

EVIDENCE_TYPES = (
    "document",
    "web",
    "api",
    "database",
    "event",
    "observation",
    "derived",
)

# ----------------------------------------------------------------------
# Confidence
# ----------------------------------------------------------------------

CONFIDENCE_LOW = 0.25
CONFIDENCE_MEDIUM = 0.50
CONFIDENCE_HIGH = 0.75
CONFIDENCE_VERY_HIGH = 0.90

# ----------------------------------------------------------------------
# Priority
# ----------------------------------------------------------------------

PRIORITY_LOW = "low"
PRIORITY_MEDIUM = "medium"
PRIORITY_HIGH = "high"
PRIORITY_CRITICAL = "critical"

PRIORITIES = (
    PRIORITY_LOW,
    PRIORITY_MEDIUM,
    PRIORITY_HIGH,
    PRIORITY_CRITICAL,
)

# ----------------------------------------------------------------------
# API
# ----------------------------------------------------------------------

API_VERSION = "v1"
API_PREFIX = f"/api/{API_VERSION}"

HEALTH_ENDPOINT = "/health"