"""
Decision Agent.

Transforms verified intelligence into structured decision signals.

The agent intentionally separates recommendation generation from
actual execution of decisions.
"""

from __future__ import annotations

from typing import Any

from nexus.agents.base import (
    AgentCapability,
    AgentContext,
    BaseAgent,
)


class DecisionAgent(BaseAgent):
    agent_id = "decision-agent"
    name = "Decision Agent"
    version = "0.1.0"

    capabilities = (
        AgentCapability(
            name="decision_support",
            description="Produce structured decision-support signals.",
            input_types=["dict"],
            output_types=["decision"],
            requires_llm=True,
            tags=["decision", "risk", "recommendation"],
        ),
    )

    async def execute(self, context: AgentContext) -> Any:
        verification = context.get_state(
            "verification_result",
            {},
        )

        anomalies = context.get_state(
            "anomaly_report",
            {},
        )

        verification_status = (
            verification.get("status", "unverified")
            if isinstance(verification, dict)
            else "unverified"
        )

        anomaly_count = (
            anomalies.get("anomaly_count", 0)
            if isinstance(anomalies, dict)
            else 0
        )

        if verification_status == "supported" and anomaly_count == 0:
            recommendation = "proceed"
        elif verification_status == "supported":
            recommendation = "review_anomalies"
        else:
            recommendation = "gather_more_evidence"

        decision = {
            "recommendation": recommendation,
            "verification_status": verification_status,
            "anomaly_count": anomaly_count,
            "risk_level": self._risk_level(
                verification_status,
                anomaly_count,
            ),
            "requires_human_review": recommendation != "proceed",
            "status": "generated",
        }

        context.set_state(
            "decision",
            decision,
        )

        return decision

    @staticmethod
    def _risk_level(
        verification_status: str,
        anomaly_count: int,
    ) -> str:
        if verification_status == "unverified":
            return "high"

        if anomaly_count > 3:
            return "high"

        if anomaly_count > 0:
            return "medium"

        return "low"