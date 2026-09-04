"""
Report Agent.

Converts accumulated intelligence state into a structured report
candidate.
"""

from __future__ import annotations

from typing import Any

from nexus.agents.base import (
    AgentCapability,
    AgentContext,
    BaseAgent,
)


class ReportAgent(BaseAgent):
    agent_id = "report-agent"
    name = "Intelligence Report Agent"
    version = "0.1.0"

    capabilities = (
        AgentCapability(
            name="report_generation",
            description="Assemble structured intelligence reports.",
            input_types=["dict"],
            output_types=["IntelligenceReport"],
            requires_llm=True,
            tags=["reporting", "summarization", "intelligence"],
        ),
    )

    async def execute(self, context: AgentContext) -> Any:
        research = context.get_state(
            "research_plan",
            {},
        )

        reasoning = context.get_state(
            "reasoning_trace",
            {},
        )

        verification = context.get_state(
            "verification_result",
            {},
        )

        anomalies = context.get_state(
            "anomaly_report",
            {},
        )

        report = {
            "title": self._build_title(research),
            "objective": (
                research.get("objective")
                if isinstance(research, dict)
                else None
            ),
            "summary": self._build_summary(
                reasoning,
                verification,
                anomalies,
            ),
            "sections": [
                {
                    "name": "Reasoning",
                    "content": reasoning,
                },
                {
                    "name": "Verification",
                    "content": verification,
                },
                {
                    "name": "Anomalies",
                    "content": anomalies,
                },
            ],
            "status": "draft",
        }

        context.add_artifact(
            "intelligence_report",
            report,
        )

        context.set_state(
            "report",
            report,
        )

        return report

    @staticmethod
    def _build_title(research: Any) -> str:
        if isinstance(research, dict):
            objective = research.get("objective")

            if objective:
                return f"Intelligence Report — {objective}"

        return "NEXUS-SENSE Intelligence Report"

    @staticmethod
    def _build_summary(
        reasoning: Any,
        verification: Any,
        anomalies: Any,
    ) -> str:
        observation_count = 0

        if isinstance(reasoning, dict):
            observation_count = len(
                reasoning.get("observations", [])
            )

        verification_status = (
            verification.get("status", "unknown")
            if isinstance(verification, dict)
            else "unknown"
        )

        anomaly_count = (
            anomalies.get("anomaly_count", 0)
            if isinstance(anomalies, dict)
            else 0
        )

        return (
            f"The analysis produced {observation_count} structured "
            f"observations. Evidence status: {verification_status}. "
            f"Detected anomalies: {anomaly_count}."
        )