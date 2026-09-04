"""
Verification Agent.

Evaluates whether generated findings have enough supporting evidence.
"""

from __future__ import annotations

from typing import Any

from nexus.agents.base import (
    AgentCapability,
    AgentContext,
    BaseAgent,
)


class VerificationAgent(BaseAgent):
    agent_id = "verification-agent"
    name = "Verification Agent"
    version = "0.1.0"

    capabilities = (
        AgentCapability(
            name="evidence_verification",
            description="Assess evidence coverage and verification status.",
            input_types=["dict"],
            output_types=["verification_result"],
            tags=["verification", "evidence", "quality"],
        ),
    )

    async def execute(self, context: AgentContext) -> Any:
        evidence = context.get_state(
            "evidence",
            [],
        )

        if isinstance(evidence, dict):
            evidence_items = evidence.get(
                "items",
                [],
            )
        elif isinstance(evidence, list):
            evidence_items = evidence
        else:
            evidence_items = []

        count = len(evidence_items)

        if count == 0:
            status = "unverified"
            confidence = 0.0
        elif count == 1:
            status = "partially_verified"
            confidence = 0.4
        else:
            status = "supported"
            confidence = min(
                0.5 + (0.1 * count),
                0.95,
            )

        result = {
            "status": status,
            "evidence_count": count,
            "independent_sources": self._count_sources(
                evidence_items
            ),
            "confidence": confidence,
        }

        context.set_state("verification_result", result)

        return result

    @staticmethod
    def _count_sources(evidence_items: list[Any]) -> int:
        sources: set[str] = set()

        for item in evidence_items:
            if isinstance(item, dict):
                source_id = item.get("source_id")

                if source_id:
                    sources.add(str(source_id))

        return len(sources)

    def estimate_confidence(self, output: Any) -> float | None:
        if not output:
            return None

        return float(
            output.get(
                "confidence",
                0.0,
            )
        )