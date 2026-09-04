"""
Provider-independent Large Language Model interfaces.

Agents interact with `LLMModel`, not directly with Groq, OpenAI,
or another provider.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, AsyncIterator

from pydantic import BaseModel, Field


class ChatRole(str, Enum):
    """Standard chat message roles."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class ChatMessage(BaseModel):
    """Normalized chat message."""

    role: ChatRole

    content: str

    name: str | None = None

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )


class LLMResponse(BaseModel):
    """Normalized LLM response."""

    content: str

    model: str

    provider: str

    finish_reason: str | None = None

    input_tokens: int = 0

    output_tokens: int = 0

    total_tokens: int = 0

    latency_ms: float | None = None

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )


class LLMModel(ABC):
    """
    Abstract interface for language models.

    Providers implement this interface without affecting the
    rest of NEXUS-SENSE.
    """

    provider: str = "unknown"

    model_name: str = "unknown"

    supports_streaming: bool = False

    supports_tools: bool = False

    supports_json: bool = False

    async def generate(
        self,
        messages: list[ChatMessage],
        *,
        temperature: float = 0.2,
        max_tokens: int | None = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """Generate a normalized response."""
        raise NotImplementedError

    async def stream(
        self,
        messages: list[ChatMessage],
        *,
        temperature: float = 0.2,
        max_tokens: int | None = None,
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        """Stream generated content."""

        if not self.supports_streaming:
            raise NotImplementedError(
                f"Model '{self.model_name}' does not "
                "support streaming."
            )

        raise NotImplementedError

    @abstractmethod
    async def health(self) -> bool:
        """Return provider/model health."""
        raise NotImplementedError

    def describe(self) -> dict[str, Any]:
        """Return model capabilities."""
        return {
            "provider": self.provider,
            "model": self.model_name,
            "supports_streaming": self.supports_streaming,
            "supports_tools": self.supports_tools,
            "supports_json": self.supports_json,
        }