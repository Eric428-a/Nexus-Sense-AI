"""
Central model registry and routing system.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from nexus.models.embeddings import EmbeddingModel
from nexus.models.llm import LLMModel


@dataclass(slots=True)
class RegisteredModel:
    """Model registered with NEXUS-SENSE."""

    model_id: str

    model: Any

    model_type: str

    provider: str

    capabilities: set[str] = field(
        default_factory=set
    )

    enabled: bool = True

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


@dataclass(slots=True)
class ModelRoute:
    """Resolution result for a requested capability."""

    model_id: str

    provider: str

    model: Any


class ModelRegistry:
    """
    Registry for all model providers.

    Example capability values:

        text_generation
        embeddings
        classification
        structured_output
        streaming
        tool_calling
    """

    def __init__(self) -> None:
        self._models: dict[str, RegisteredModel] = {}

    def register(
        self,
        model_id: str,
        model: Any,
        *,
        model_type: str,
        provider: str,
        capabilities: set[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:

        if model_id in self._models:
            raise ValueError(
                f"Model '{model_id}' is already registered."
            )

        self._models[model_id] = RegisteredModel(
            model_id=model_id,
            model=model,
            model_type=model_type,
            provider=provider,
            capabilities=capabilities or set(),
            metadata=metadata or {},
        )

    def unregister(
        self,
        model_id: str,
    ) -> None:

        if model_id not in self._models:
            raise KeyError(
                f"Model '{model_id}' is not registered."
            )

        del self._models[model_id]

    def get(
        self,
        model_id: str,
    ) -> Any:

        if model_id not in self._models:
            raise KeyError(
                f"Model '{model_id}' is not registered."
            )

        return self._models[model_id].model

    def route(
        self,
        capability: str,
        *,
        provider: str | None = None,
        model_type: str | None = None,
    ) -> ModelRoute:

        candidates = [
            registered
            for registered in self._models.values()
            if registered.enabled
            and capability in registered.capabilities
        ]

        if provider:
            candidates = [
                candidate
                for candidate in candidates
                if candidate.provider == provider
            ]

        if model_type:
            candidates = [
                candidate
                for candidate in candidates
                if candidate.model_type == model_type
            ]

        if not candidates:
            raise LookupError(
                f"No model available for capability "
                f"'{capability}'."
            )

        selected = candidates[0]

        return ModelRoute(
            model_id=selected.model_id,
            provider=selected.provider,
            model=selected.model,
        )

    def enable(
        self,
        model_id: str,
    ) -> None:
        self._models[model_id].enabled = True

    def disable(
        self,
        model_id: str,
    ) -> None:
        self._models[model_id].enabled = False

    def list_models(self) -> list[RegisteredModel]:
        return list(self._models.values())

    def describe(self) -> list[dict[str, Any]]:
        return [
            {
                "model_id": model.model_id,
                "model_type": model.model_type,
                "provider": model.provider,
                "capabilities": sorted(
                    model.capabilities
                ),
                "enabled": model.enabled,
                "metadata": model.metadata,
            }
            for model in self._models.values()
        ]

    @classmethod
    def with_models(
        cls,
        *,
        llm: LLMModel | None = None,
        embeddings: EmbeddingModel | None = None,
    ) -> "ModelRegistry":
        """Convenience constructor."""

        registry = cls()

        if llm is not None:
            registry.register(
                "default-llm",
                llm,
                model_type="llm",
                provider=llm.provider,
                capabilities={
                    "text_generation",
                    *(
                        {"streaming"}
                        if llm.supports_streaming
                        else set()
                    ),
                    *(
                        {"tool_calling"}
                        if llm.supports_tools
                        else set()
                    ),
                    *(
                        {"structured_output"}
                        if llm.supports_json
                        else set()
                    ),
                },
            )

        if embeddings is not None:
            registry.register(
                "default-embeddings",
                embeddings,
                model_type="embedding",
                provider=embeddings.provider,
                capabilities={
                    "embeddings",
                },
            )

        return registry