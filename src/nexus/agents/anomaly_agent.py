"""
Anomaly Agent.

Identifies unusual numerical or structural observations.

This first implementation provides deterministic baseline detection.
More advanced statistical and ML detectors can be plugged in later.
"""

from __future__ import annotations

import statistics
from typing import Any

from nexus.agents.base import (
    AgentCapability,
    AgentContext,
    BaseAgent,
)


class AnomalyAgent(BaseAgent):
    agent_id = "anomaly-agent"
    name = "Anomaly Detection Agent"
    version = "0.1.0"

    capabilities = (
        AgentCapability(
            name="numeric_anomaly_detection",
            description="Detect unusually distant numerical observations.",
            input_types=["list", "dict"],
            output_types=["anomaly_report"],
            tags=["anomaly", "statistics", "monitoring"],
        ),
    )

    async def execute(self, context: AgentContext) -> Any:
        values = self._extract_values(context)

        if len(values) < 3:
            result = {
                "values_analyzed": len(values),
                "anomalies": [],
                "status": "insufficient_data",
            }

            context.set_state("anomaly_report", result)

            return result

        mean = statistics.mean(values)
        stddev = statistics.pstdev(values)

        threshold = mean + (2 * stddev)

        anomalies = [
            {
                "value": value,
                "index": index,
                "distance_from_mean": abs(value - mean),
            }
            for index, value in enumerate(values)
            if abs(value - mean) > 2 * stddev
        ]

        result = {
            "values_analyzed": len(values),
            "mean": mean,
            "stddev": stddev,
            "threshold": threshold,
            "anomalies": anomalies,
            "anomaly_count": len(anomalies),
            "status": "analyzed",
        }

        context.set_state("anomaly_report", result)

        return result

    @staticmethod
    def _extract_values(context: AgentContext) -> list[float]:
        data = context.input

        if isinstance(data, list):
            values = data
        elif isinstance(data, dict):
            values = data.get("values", [])
        else:
            values = context.get_state("values", [])

        result: list[float] = []

        for value in values:
            try:
                result.append(float(value))
            except (TypeError, ValueError):
                continue

        return result