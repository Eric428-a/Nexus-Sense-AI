"""
Embedding model abstraction.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Sequence


class Embedding:
    """Represents a single embedding vector."""

    def __init__(
        self,
        vector: Sequence[float],
        *,
        model: str,
    ) -> None:
        self.vector = list(vector)
        self.model = model

    @property
    def dimensions(self) -> int:
        return len(self.vector)


class EmbeddingModel(ABC):
    """Provider-independent embedding interface."""

    provider: str = "unknown"

    model_name: str = "unknown"

    dimensions: int | None = None

    @abstractmethod
    async def embed(
        self,
        text: str,
    ) -> Embedding:
        """Create an embedding for one text input."""
        raise NotImplementedError

    async def embed_many(
        self,
        texts: Sequence[str],
    ) -> list[Embedding]:
        """Create embeddings for multiple inputs."""

        return [
            await self.embed(text)
            for text in texts
        ]

    @abstractmethod
    async def health(self) -> bool:
        """Return provider/model health."""
        raise NotImplementedError

    def describe(self) -> dict[str, object]:
        return {
            "provider": self.provider,
            "model": self.model_name,
            "dimensions": self.dimensions,
        }