"""
Agent registry and orchestration engine.

The orchestrator is responsible for:
- Discovering registered agents.
- Validating dependencies.
- Executing agents in dependency order.
- Sharing state between agents.
- Supporting selective execution.
- Capturing failures without destroying the entire execution graph.
"""

from __future__ import annotations

from collections import defaultdict, deque
from typing import Any

from pydantic import BaseModel, Field

from nexus.agents.base import (
    AgentContext,
    AgentExecutionStatus,
    AgentResult,
    BaseAgent,
)
from nexus.utils.ids import generate_id
from nexus.utils.timestamps import utc_now


class RegisteredAgent(BaseModel):
    """Metadata about an agent registered with the orchestrator."""

    agent_id: str
    name: str
    dependencies: list[str] = Field(default_factory=list)
    enabled: bool = True


class OrchestrationResult(BaseModel):
    """Complete result of an orchestration run."""

    orchestration_id: str = Field(default_factory=generate_id)

    success: bool

    status: str

    executed_agents: list[str] = Field(default_factory=list)

    skipped_agents: list[str] = Field(default_factory=list)

    failed_agents: list[str] = Field(default_factory=list)

    results: dict[str, AgentResult] = Field(default_factory=dict)

    started_at: Any = Field(default_factory=utc_now)
    completed_at: Any | None = None

    metadata: dict[str, Any] = Field(default_factory=dict)


class AgentRegistry:
    """Central registry for NEXUS-SENSE agents."""

    def __init__(self) -> None:
        self._agents: dict[str, BaseAgent] = {}
        self._dependencies: dict[str, list[str]] = defaultdict(list)

    def register(
        self,
        agent: BaseAgent,
        dependencies: list[str] | None = None,
    ) -> None:
        """Register an agent."""

        if agent.agent_id in self._agents:
            raise ValueError(
                f"Agent '{agent.agent_id}' is already registered."
            )

        self._agents[agent.agent_id] = agent
        self._dependencies[agent.agent_id] = dependencies or []

    def unregister(self, agent_id: str) -> None:
        """Remove an agent from the registry."""

        if agent_id not in self._agents:
            raise KeyError(f"Agent '{agent_id}' is not registered.")

        self._agents.pop(agent_id)
        self._dependencies.pop(agent_id, None)

    def get(self, agent_id: str) -> BaseAgent:
        """Retrieve an agent."""
        try:
            return self._agents[agent_id]
        except KeyError as exc:
            raise KeyError(
                f"Agent '{agent_id}' is not registered."
            ) from exc

    def has(self, agent_id: str) -> bool:
        """Check whether an agent exists."""
        return agent_id in self._agents

    def all(self) -> list[BaseAgent]:
        """Return all registered agents."""
        return list(self._agents.values())

    def dependencies(self, agent_id: str) -> list[str]:
        """Return dependencies for an agent."""
        return list(self._dependencies.get(agent_id, []))

    def describe(self) -> list[RegisteredAgent]:
        """Return registry metadata."""
        return [
            RegisteredAgent(
                agent_id=agent.agent_id,
                name=agent.name,
                dependencies=self.dependencies(agent.agent_id),
                enabled=agent.is_available,
            )
            for agent in self.all()
        ]

    def validate_dependencies(self) -> None:
        """Validate that every dependency is registered."""

        for agent_id, dependencies in self._dependencies.items():
            for dependency in dependencies:
                if dependency not in self._agents:
                    raise ValueError(
                        f"Agent '{agent_id}' depends on unknown "
                        f"agent '{dependency}'."
                    )

        self._topological_order()

    def _topological_order(self) -> list[str]:
        """Return dependency-safe agent execution order."""

        indegree: dict[str, int] = {
            agent_id: 0 for agent_id in self._agents
        }

        graph: dict[str, list[str]] = defaultdict(list)

        for agent_id, dependencies in self._dependencies.items():
            for dependency in dependencies:
                graph[dependency].append(agent_id)
                indegree[agent_id] += 1

        queue = deque(
            agent_id
            for agent_id, degree in indegree.items()
            if degree == 0
        )

        order: list[str] = []

        while queue:
            current = queue.popleft()
            order.append(current)

            for dependent in graph[current]:
                indegree[dependent] -= 1

                if indegree[dependent] == 0:
                    queue.append(dependent)

        if len(order) != len(self._agents):
            raise ValueError(
                "Circular dependency detected in agent graph."
            )

        return order


class AgentOrchestrator:
    """
    Dependency-aware execution engine.

    The orchestrator does not contain domain intelligence. It coordinates
    agents and provides them with shared execution state.
    """

    def __init__(self, registry: AgentRegistry) -> None:
        self.registry = registry

    async def run(
        self,
        context: AgentContext,
        selected_agents: list[str] | None = None,
        stop_on_failure: bool = False,
    ) -> OrchestrationResult:
        """
        Execute the selected agent graph.

        If selected_agents is omitted, the entire registered graph runs.
        """

        started_at = utc_now()

        self.registry.validate_dependencies()

        execution_order = self.registry._topological_order()

        if selected_agents is not None:
            requested = set(selected_agents)

            unknown = requested - set(execution_order)

            if unknown:
                raise ValueError(
                    "Unknown agents requested: "
                    + ", ".join(sorted(unknown))
                )

            execution_order = [
                agent_id
                for agent_id in execution_order
                if agent_id in requested
            ]

        results: dict[str, AgentResult] = {}

        executed_agents: list[str] = []
        skipped_agents: list[str] = []
        failed_agents: list[str] = []

        for agent_id in execution_order:
            agent = self.registry.get(agent_id)

            dependencies = self.registry.dependencies(agent_id)

            failed_dependency = any(
                dependency in failed_agents
                for dependency in dependencies
            )

            if failed_dependency:
                skipped_agents.append(agent_id)

                skipped_result = AgentResult(
                    agent_id=agent.agent_id,
                    agent_name=agent.name,
                    execution_id=context.execution_id,
                    status=AgentExecutionStatus.SKIPPED,
                    success=False,
                    errors=[
                        "Skipped because a required dependency failed."
                    ],
                )

                results[agent_id] = skipped_result
                context.add_result(skipped_result)

                continue

            result = await agent.run(context)

            results[agent_id] = result

            if result.success:
                executed_agents.append(agent_id)
            else:
                failed_agents.append(agent_id)

                if stop_on_failure:
                    break

        context.finalize()

        completed_at = utc_now()

        success = len(failed_agents) == 0

        status = (
            "completed"
            if success
            else "completed_with_failures"
        )

        return OrchestrationResult(
            success=success,
            status=status,
            executed_agents=executed_agents,
            skipped_agents=skipped_agents,
            failed_agents=failed_agents,
            results=results,
            started_at=started_at,
            completed_at=completed_at,
            metadata={
                "agent_count": len(execution_order),
                "state_keys": list(context.state.keys()),
                "artifact_keys": list(context.artifacts.keys()),
            },
        )