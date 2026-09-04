"""
Reasoning Agent.

Constructs structured reasoning inputs from extracted information
and available evidence.
"""

from __future__ import annotations

from typing import Any

from nexus.agents.base import (
    AgentCapability,
    AgentContext,
    BaseAgent,
)


class ReasoningAgent(BaseAgent):
    agent_id = "reasoning-agent"
    name = "Reasoning Agent"
    version = "0.1.0"

    capabilities = (
        AgentCapability(
            name="evidence_reasoning",
            description="Construct structured reasoning over available evidence.",
            input_types=["dict"],
            output_types=["reasoning_trace"],
            requires_llm=True,
            tags=["reasoning", "evidence", "hypothesis"],
        ),
    )

    async def execute(self, context: AgentContext) -> Any:
        extraction = context.get_state(
            "extraction_result",
            {},
        )

        research = context.get_state(
            "research_plan",
            {},
        )

        entity_count = extraction.get(
            "entity_count",
            0,
        ) if isinstance(extraction, dict) else 0

        objective = (
            research.get("objective")
            if isinstance(research, dict)
            else None
        )

        reasoning = {
            "objective": objective,
            "observations": [
                {
                    "type": "entity_signal",
                    "value": entity_count,
                    "interpretation": (
                        "Number of candidate entities extracted "
                        "from available source material."
                    ),
                }
            ],
            "hypotheses": [],
            "evidence_requirements": [
                "independent source confirmation",
                "temporal consistency",
                "entity identity validation",
            ],
            "status": "structured",
        }

        context.set_state("reasoning_trace", reasoning)

        return reasoning

    def estimate_confidence(self, output: Any) -> float | None:
        if not output:
            return 0.0

        observations = output.get("observations", [])

        if observations:
            return 0.5

        return 0.2