"""
Prompt management for NEXUS-SENSE.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class PromptTemplate:
    """Reusable prompt template."""

    name: str

    version: str

    system: str

    user_template: str

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def render(
        self,
        **variables: Any,
    ) -> list[dict[str, str]]:

        return [
            {
                "role": "system",
                "content": self.system,
            },
            {
                "role": "user",
                "content": self.user_template.format(
                    **variables
                ),
            },
        ]


class PromptRegistry:
    """Central prompt template registry."""

    def __init__(self) -> None:
        self._templates: dict[
            str,
            PromptTemplate,
        ] = {}

    def register(
        self,
        template: PromptTemplate,
    ) -> None:

        key = (
            f"{template.name}:"
            f"{template.version}"
        )

        if key in self._templates:
            raise ValueError(
                f"Prompt '{key}' already exists."
            )

        self._templates[key] = template

    def get(
        self,
        name: str,
        version: str = "1.0.0",
    ) -> PromptTemplate:

        key = f"{name}:{version}"

        if key not in self._templates:
            raise KeyError(
                f"Prompt '{key}' is not registered."
            )

        return self._templates[key]

    def render(
        self,
        name: str,
        *,
        version: str = "1.0.0",
        **variables: Any,
    ) -> list[dict[str, str]]:

        template = self.get(
            name,
            version,
        )

        return template.render(
            **variables
        )

    def list_templates(self) -> list[str]:
        return sorted(
            self._templates.keys()
        )


def build_default_prompts() -> PromptRegistry:
    """Build standard NEXUS prompt templates."""

    registry = PromptRegistry()

    registry.register(
        PromptTemplate(
            name="research-analysis",
            version="1.0.0",
            system=(
                "You are a research intelligence component "
                "inside NEXUS-SENSE. Distinguish evidence from "
                "inference and avoid unsupported claims."
            ),
            user_template=(
                "Research objective:\n"
                "{objective}\n\n"
                "Evidence context:\n"
                "{context}\n\n"
                "Produce structured analytical observations."
            ),
        )
    )

    registry.register(
        PromptTemplate(
            name="evidence-reasoning",
            version="1.0.0",
            system=(
                "You are an evidence reasoning component. "
                "Assess competing explanations and explicitly "
                "identify uncertainty."
            ),
            user_template=(
                "Question:\n"
                "{question}\n\n"
                "Evidence:\n"
                "{evidence}\n\n"
                "Reason over the available evidence."
            ),
        )
    )

    registry.register(
        PromptTemplate(
            name="intelligence-summary",
            version="1.0.0",
            system=(
                "You are an intelligence reporting component. "
                "Summarize verified findings without presenting "
                "uncertain information as fact."
            ),
            user_template=(
                "Findings:\n"
                "{findings}\n\n"
                "Verification:\n"
                "{verification}\n\n"
                "Prepare a concise intelligence summary."
            ),
        )
    )

    return registry