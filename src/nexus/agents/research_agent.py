"""
Research Agent.

Responsible for identifying research requirements and preparing
research tasks for downstream intelligence processing.

External search providers can be connected later without changing
the agent contract.
"""

from __future__ import annotations

from typing import Any

from nexus.agents.base import (
    AgentCapability,
    AgentContext,
    BaseAgent,
)


class ResearchAgent(BaseAgent):
    agent_id = "research-agent"
    name = "Research Agent"
    version = "0.1.0"

    capabilities = (
        AgentCapability(
            name="research_planning",
            description="Break a research request into structured tasks.",
            input_types=["str", "dict"],
            output_types=["research_plan"],
            tags=["research", "planning"],
        ),
    )

    async def execute(self, context: AgentContext) -> Any:
        request = context.input

        if isinstance(request, str):
            objective = request
        elif isinstance(request, dict):
            objective = str(
                request.get("objective")
                or request.get("query")
                or request
            )
        else:
            objective = str(request)

        plan = {
            "objective": objective,
            "tasks": [
                {
                    "task_id": "research-1",
                    "type": "source_discovery",
                    "description": "Identify relevant information sources.",
                },
                {
                    "task_id": "research-2",
                    "type": "evidence_collection",
                    "description": "Collect evidence relevant to the objective.",
                },
                {
                    "task_id": "research-3",
                    "type": "cross_validation",
                    "description": "Compare evidence across independent sources.",
                },
            ],
            "status": "planned",
        }

        context.set_state("research_plan", plan)

        return plan