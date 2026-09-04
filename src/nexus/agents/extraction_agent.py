"""
Extraction Agent.

Transforms ingested documents into structured extraction candidates.

The actual NLP/LLM extraction engines can be plugged into this agent
later through the extraction package.
"""

from __future__ import annotations

import re
from typing import Any

from nexus.agents.base import (
    AgentCapability,
    AgentContext,
    BaseAgent,
)


class ExtractionAgent(BaseAgent):
    agent_id = "extraction-agent"
    name = "Extraction Agent"
    version = "0.1.0"

    capabilities = (
        AgentCapability(
            name="entity_extraction",
            description="Identify candidate entities from source content.",
            input_types=["SourceDocument", "list"],
            output_types=["extraction_result"],
            requires_llm=False,
            tags=["nlp", "entities", "extraction"],
        ),
    )

    async def execute(self, context: AgentContext) -> Any:
        source = context.input

        content = self._extract_content(source)

        candidates = self._extract_candidates(content)

        result = {
            "entities": candidates,
            "entity_count": len(candidates),
            "source_length": len(content),
            "status": "extracted",
        }

        context.set_state("extraction_result", result)

        return result

    @staticmethod
    def _extract_content(source: Any) -> str:
        if source is None:
            return ""

        if isinstance(source, str):
            return source

        if isinstance(source, dict):
            return str(
                source.get("content")
                or source.get("text")
                or ""
            )

        content = getattr(source, "content", None)

        if content is not None:
            return str(content)

        return str(source)

    @staticmethod
    def _extract_candidates(content: str) -> list[dict[str, Any]]:
        """
        Lightweight deterministic candidate extraction.

        This intentionally does not pretend to be a production NER model.
        It provides a stable foundation for later model integration.
        """

        candidates: list[dict[str, Any]] = []

        for match in re.finditer(
            r"\b[A-Z][A-Za-z0-9_-]{2,}\b",
            content,
        ):
            value = match.group(0)

            candidates.append(
                {
                    "text": value,
                    "start": match.start(),
                    "end": match.end(),
                    "type": "candidate",
                }
            )

        return candidates[:100]