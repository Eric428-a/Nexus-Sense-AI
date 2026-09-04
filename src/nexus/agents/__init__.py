"""
NEXUS-SENSE AI agent framework.

The agent layer provides:
- A common lifecycle contract for all agents.
- Shared execution context and state.
- Agent registration and discovery.
- Dependency-aware orchestration.
- Structured execution results.
"""

from nexus.agents.base import (
    AgentCapability,
    AgentContext,
    AgentExecution,
    AgentExecutionStatus,
    AgentResult,
    AgentStatus,
    BaseAgent,
)
from nexus.agents.orchestrator import (
    AgentOrchestrator,
    AgentRegistry,
    OrchestrationResult,
)

__all__ = [
    "AgentCapability",
    "AgentContext",
    "AgentExecution",
    "AgentExecutionStatus",
    "AgentResult",
    "AgentOrchestrator",
    "AgentRegistry",
    "AgentStatus",
    "BaseAgent",
    "OrchestrationResult",
]