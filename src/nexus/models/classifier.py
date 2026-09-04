"""
Classification model abstraction.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Sequence

from pydantic import BaseModel, Field


class Classification(BaseModel):
    """Normalized classification output."""

    label: str

    score: float = Field(
        ge=0.0,
        le=1.0,
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )


class ClassifierModel(ABC):
    """Provider-independent classification interface."""

    model_name: str = "unknown"

    @abstractmethod
    async def classify(
        self,
        text: str,
        labels: Sequence[str],
    ) -> Classification:
        """Classify text against candidate labels."""
        raise NotImplementedError

    @abstractmethod
    async def health(self) -> bool:
        """Return model health."""
        raise NotImplementedError