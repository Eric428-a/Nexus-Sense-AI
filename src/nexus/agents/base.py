"""
Core agent abstractions for NEXUS-SENSE AI.

Every specialized agent follows the same lifecycle:

    CREATED
       ↓
    VALIDATING
       ↓
    RUNNING
       ↓
    COMPLETED / FAILED
       ↓
    FINALIZED

The framework deliberately separates orchestration state from
agent-specific intelligence logic.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from time import perf_counter
from typing import Any

from pydantic import BaseModel, Field

from nexus.utils.ids import generate_id
from nexus.utils.timestamps import utc_now


class AgentStatus(str, Enum):
    """Availability state of an agent."""

    ACTIVE = "active"
    DISABLED = "disabled"
    MAINTENANCE = "maintenance"


class AgentExecutionStatus(str, Enum):
    """Runtime state of an individual agent execution."""

    CREATED = "created"
    VALIDATING = "validating"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class AgentCapability(BaseModel):
    """Describes a capability exposed by an agent."""

    name: str
    description: str
    input_types: list[str] = Field(default_factory=list)
    output_types: list[str] = Field(default_factory=list)
    requires_llm: bool = False
    requires_external_data: bool = False
    tags: list[str] = Field(default_factory=list)


class AgentExecution(BaseModel):
    """Persistent-style execution record for one agent invocation."""

    execution_id: str = Field(default_factory=generate_id)
    agent_id: str
    status: AgentExecutionStatus = AgentExecutionStatus.CREATED

    started_at: datetime | None = None
    completed_at: datetime | None = None

    duration_ms: float | None = None

    attempt: int = 1
    parent_execution_id: str | None = None

    error: str | None = None
    warnings: list[str] = Field(default_factory=list)

    metadata: dict[str, Any] = Field(default_factory=dict)

    def start(self) -> None:
        """Mark execution as running."""
        self.status = AgentExecutionStatus.RUNNING
        self.started_at = utc_now()

    def complete(self) -> None:
        """Mark execution as completed."""
        self.status = AgentExecutionStatus.COMPLETED
        self.completed_at = utc_now()
        self._calculate_duration()

    def fail(self, error: str) -> None:
        """Mark execution as failed."""
        self.status = AgentExecutionStatus.FAILED
        self.error = error
        self.completed_at = utc_now()
        self._calculate_duration()

    def _calculate_duration(self) -> None:
        if self.started_at and self.completed_at:
            self.duration_ms = (
                self.completed_at - self.started_at
            ).total_seconds() * 1000


class AgentResult(BaseModel):
    """Standardized result returned by every agent."""

    result_id: str = Field(default_factory=generate_id)

    agent_id: str
    agent_name: str

    execution_id: str

    status: AgentExecutionStatus

    success: bool

    output: Any = None

    artifacts: dict[str, Any] = Field(default_factory=dict)

    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

    confidence: float | None = Field(default=None, ge=0.0, le=1.0)

    metrics: dict[str, float] = Field(default_factory=dict)

    started_at: datetime | None = None
    completed_at: datetime | None = None

    metadata: dict[str, Any] = Field(default_factory=dict)


class AgentContext(BaseModel):
    """
    Shared state passed through the agent execution graph.

    Agents should avoid mutating input objects directly. Instead they
    should place derived information inside `state` or `artifacts`.
    """

    execution_id: str = Field(default_factory=generate_id)

    request_id: str | None = None

    input: Any = None

    state: dict[str, Any] = Field(default_factory=dict)

    artifacts: dict[str, Any] = Field(default_factory=dict)

    agent_results: dict[str, AgentResult] = Field(default_factory=dict)

    metadata: dict[str, Any] = Field(default_factory=dict)

    current_stage: str | None = None

    started_at: datetime = Field(default_factory=utc_now)

    completed_at: datetime | None = None

    def set_state(self, key: str, value: Any) -> None:
        """Store shared execution state."""
        self.state[key] = value

    def get_state(self, key: str, default: Any = None) -> Any:
        """Retrieve shared execution state."""
        return self.state.get(key, default)

    def add_artifact(self, name: str, artifact: Any) -> None:
        """Register an artifact produced during execution."""
        self.artifacts[name] = artifact

    def add_result(self, result: AgentResult) -> None:
        """Register an agent result."""
        self.agent_results[result.agent_id] = result

    def finalize(self) -> None:
        """Mark the context as completed."""
        self.completed_at = utc_now()


class BaseAgent(ABC):
    """
    Abstract base class for every NEXUS-SENSE agent.

    Subclasses implement:
        - validate_input()
        - execute()

    The public `run()` method owns lifecycle handling, timing,
    error normalization, and result construction.
    """

    agent_id: str = "base-agent"
    name: str = "Base Agent"
    version: str = "0.1.0"

    status: AgentStatus = AgentStatus.ACTIVE

    capabilities: tuple[AgentCapability, ...] = ()

    def __init__(self) -> None:
        self._last_execution: AgentExecution | None = None

    @property
    def is_available(self) -> bool:
        """Return whether the agent can currently execute."""
        return self.status == AgentStatus.ACTIVE

    def describe(self) -> dict[str, Any]:
        """Return machine-readable agent metadata."""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "version": self.version,
            "status": self.status.value,
            "capabilities": [
                capability.model_dump()
                for capability in self.capabilities
            ],
        }

    async def run(self, context: AgentContext) -> AgentResult:
        """
        Execute the agent through the standard lifecycle.
        """

        execution = AgentExecution(
            agent_id=self.agent_id,
            parent_execution_id=context.execution_id,
        )

        self._last_execution = execution

        if not self.is_available:
            execution.status = AgentExecutionStatus.SKIPPED

            return AgentResult(
                agent_id=self.agent_id,
                agent_name=self.name,
                execution_id=execution.execution_id,
                status=AgentExecutionStatus.SKIPPED,
                success=False,
                errors=[
                    f"Agent '{self.agent_id}' is currently "
                    f"{self.status.value}."
                ],
            )

        execution.status = AgentExecutionStatus.VALIDATING

        started = perf_counter()

        try:
            await self.validate_input(context)

            execution.start()

            context.current_stage = self.agent_id

            output = await self.execute(context)

            execution.complete()

            elapsed_ms = (perf_counter() - started) * 1000

            result = AgentResult(
                agent_id=self.agent_id,
                agent_name=self.name,
                execution_id=execution.execution_id,
                status=AgentExecutionStatus.COMPLETED,
                success=True,
                output=output,
                confidence=self.estimate_confidence(output),
                metrics={
                    "duration_ms": elapsed_ms,
                },
                started_at=execution.started_at,
                completed_at=execution.completed_at,
            )

            context.add_result(result)

            return result

        except Exception as exc:
            execution.fail(str(exc))

            elapsed_ms = (perf_counter() - started) * 1000

            result = AgentResult(
                agent_id=self.agent_id,
                agent_name=self.name,
                execution_id=execution.execution_id,
                status=AgentExecutionStatus.FAILED,
                success=False,
                errors=[str(exc)],
                metrics={
                    "duration_ms": elapsed_ms,
                },
                started_at=execution.started_at,
                completed_at=execution.completed_at,
            )

            context.add_result(result)

            return result

    async def validate_input(self, context: AgentContext) -> None:
        """
        Validate execution context.

        Subclasses can override this method. The default implementation
        only ensures a context object exists.
        """
        if context is None:
            raise ValueError("Agent context cannot be None.")

    @abstractmethod
    async def execute(self, context: AgentContext) -> Any:
        """Perform the agent-specific operation."""
        raise NotImplementedError

    def estimate_confidence(self, output: Any) -> float | None:
        """
        Estimate output confidence.

        Specialized agents may override this with domain-specific
        confidence calculations.
        """
        if output is None:
            return None

        return 0.5

    def reset(self) -> None:
        """Reset transient execution state."""
        self._last_execution = None