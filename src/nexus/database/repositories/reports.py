"""
Intelligence report persistence.
"""

from __future__ import annotations

from nexus.reasoning.report import IntelligenceReport


class ReportRepository:
    """Repository for generated intelligence reports."""

    def __init__(self) -> None:
        self._reports: dict[str, IntelligenceReport] = {}

    async def get(self, report_id: str) -> IntelligenceReport | None:
        return self._reports.get(report_id)

    async def save(
        self,
        report: IntelligenceReport,
    ) -> IntelligenceReport:

        self._reports[report.id] = report
        return report

    async def delete(self, report_id: str) -> bool:
        return self._reports.pop(report_id, None) is not None

    async def exists(self, report_id: str) -> bool:
        return report_id in self._reports

    async def list(
        self,
        *,
        limit: int = 100,
    ) -> list[IntelligenceReport]:

        return list(self._reports.values())[:limit]

    async def count(self) -> int:
        return len(self._reports)