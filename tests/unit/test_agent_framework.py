"""
Tests for the NEXUS-SENSE agent framework.
"""

from __future__ import annotations

import pytest

from src.nexus.agents.base import (
    AgentCapability,
    AgentContext,
    AgentExecutionStatus,
    BaseAgent,
)
from src.nexus.agents.orchestrator import (
    AgentOrchestrator,
    AgentRegistry,
)
from src.nexus.agents.anomaly_agent import AnomalyAgent
from src.nexus.agents.decision_agent import DecisionAgent
from src.nexus.agents.extraction_agent import ExtractionAgent
from src.nexus.agents.reasoning_agent import ReasoningAgent
from src.nexus.agents.report_agent import ReportAgent
from src.nexus.agents.research_agent import ResearchAgent
from src.nexus.agents.verification_agent import VerificationAgent


class EchoAgent(BaseAgent):
    agent_id = "echo-agent"
    name = "Echo Agent"

    capabilities = (
        AgentCapability(
            name="echo",
            description="Returns the supplied input.",
        ),
    )

    async def execute(self, context: AgentContext):
        return context.input


class FailingAgent(BaseAgent):
    agent_id = "failing-agent"
    name = "Failing Agent"

    async def execute(self, context: AgentContext):
        raise RuntimeError("intentional failure")


@pytest.mark.asyncio
async def test_agent_lifecycle_success():
    agent = EchoAgent()

    context = AgentContext(
        input={"message": "hello"},
    )

    result = await agent.run(context)

    assert result.success is True
    assert result.status == AgentExecutionStatus.COMPLETED
    assert result.output == {"message": "hello"}
    assert result.metrics["duration_ms"] >= 0


@pytest.mark.asyncio
async def test_agent_lifecycle_failure():
    agent = FailingAgent()

    context = AgentContext(
        input="test",
    )

    result = await agent.run(context)

    assert result.success is False
    assert result.status == AgentExecutionStatus.FAILED
    assert "intentional failure" in result.errors[0]


def test_registry_register_and_get():
    registry = AgentRegistry()

    agent = EchoAgent()

    registry.register(agent)

    assert registry.has("echo-agent")
    assert registry.get("echo-agent") is agent


def test_registry_duplicate_agent_rejected():
    registry = AgentRegistry()

    registry.register(EchoAgent())

    with pytest.raises(ValueError):
        registry.register(EchoAgent())


def test_registry_unknown_dependency_rejected():
    registry = AgentRegistry()

    registry.register(
        EchoAgent(),
        dependencies=["missing-agent"],
    )

    with pytest.raises(ValueError):
        registry.validate_dependencies()


def test_registry_circular_dependency_rejected():
    first = EchoAgent()
    first.agent_id = "first"

    second = EchoAgent()
    second.agent_id = "second"

    registry = AgentRegistry()

    registry.register(
        first,
        dependencies=["second"],
    )

    registry.register(
        second,
        dependencies=["first"],
    )

    with pytest.raises(ValueError):
        registry.validate_dependencies()


@pytest.mark.asyncio
async def test_orchestrator_dependency_order():
    registry = AgentRegistry()

    first = EchoAgent()
    first.agent_id = "first"

    second = EchoAgent()
    second.agent_id = "second"

    registry.register(first)

    registry.register(
        second,
        dependencies=["first"],
    )

    orchestrator = AgentOrchestrator(registry)

    context = AgentContext(
        input="hello",
    )

    result = await orchestrator.run(context)

    assert result.success is True
    assert result.executed_agents == [
        "first",
        "second",
    ]


@pytest.mark.asyncio
async def test_orchestrator_skips_failed_dependency():
    registry = AgentRegistry()

    failing = FailingAgent()

    dependent = EchoAgent()
    dependent.agent_id = "dependent"

    registry.register(failing)

    registry.register(
        dependent,
        dependencies=["failing-agent"],
    )

    orchestrator = AgentOrchestrator(registry)

    result = await orchestrator.run(
        AgentContext(input="test"),
    )

    assert result.success is False
    assert "failing-agent" in result.failed_agents
    assert "dependent" in result.skipped_agents


@pytest.mark.asyncio
async def test_research_agent():
    agent = ResearchAgent()

    result = await agent.run(
        AgentContext(
            input="Investigate market changes.",
        )
    )

    assert result.success
    assert result.output["objective"] == (
        "Investigate market changes."
    )
    assert len(result.output["tasks"]) == 3


@pytest.mark.asyncio
async def test_extraction_agent():
    agent = ExtractionAgent()

    result = await agent.run(
        AgentContext(
            input={
                "content": (
                    "NEXUS works with OpenAI and MongoDB."
                )
            }
        )
    )

    assert result.success
    assert result.output["entity_count"] > 0


@pytest.mark.asyncio
async def test_anomaly_agent():
    agent = AnomalyAgent()

    result = await agent.run(
        AgentContext(
            input={
                "values": [10, 11, 10, 12, 100],
            }
        )
    )

    assert result.success
    assert result.output["values_analyzed"] == 5
    assert result.output["anomaly_count"] >= 1


@pytest.mark.asyncio
async def test_full_agent_chain():
    registry = AgentRegistry()

    registry.register(
        ResearchAgent(),
    )

    registry.register(
        ExtractionAgent(),
    )

    registry.register(
        ReasoningAgent(),
        dependencies=[
            "research-agent",
            "extraction-agent",
        ],
    )

    registry.register(
        VerificationAgent(),
        dependencies=[
            "reasoning-agent",
        ],
    )

    registry.register(
        AnomalyAgent(),
    )

    registry.register(
        ReportAgent(),
        dependencies=[
            "reasoning-agent",
            "verification-agent",
            "anomaly-agent",
        ],
    )

    registry.register(
        DecisionAgent(),
        dependencies=[
            "verification-agent",
            "anomaly-agent",
            "report-agent",
        ],
    )

    orchestrator = AgentOrchestrator(registry)

    context = AgentContext(
        input={
            "objective": "Analyze a hypothetical intelligence signal.",
            "content": (
                "NEXUS identifies Organization Alpha "
                "and Organization Beta."
            ),
            "values": [10, 11, 10, 12, 100],
        }
    )

    # The anomaly agent reads values from the input while the
    # extraction agent reads content from the same shared input.
    anomaly_context = context

    result = await orchestrator.run(anomaly_context)

    assert result.status in {
        "completed",
        "completed_with_failures",
    }

    assert "research-agent" in result.results
    assert "extraction-agent" in result.results
    assert "reasoning-agent" in result.results
    assert "verification-agent" in result.results
    assert "anomaly-agent" in result.results
    assert "report-agent" in result.results
    assert "decision-agent" in result.results

    assert context.completed_at is not None