"""
Deterministic model providers for local development and testing.

These are deliberately simple and make no claim to provide real
language-model intelligence.
"""

from __future__ import annotations

import hashlib
from typing import Sequence

from nexus.models.embeddings import Embedding
from nexus.models.llm import (
    ChatMessage,
    LLMModel,
    LLMResponse,
)


class MockLLM(LLMModel):
    """Deterministic fake LLM."""

    provider = "mock"

    model_name = "mock-llm"

    supports_streaming = False

    supports_tools = False

    supports_json = False

    async def generate(
        self,
        messages: list[ChatMessage],
        *,
        temperature: float = 0.2,
        max_tokens: int | None = None,
        **kwargs,
    ) -> LLMResponse:

        user_messages = [
            message.content
            for message in messages
            if message.role.value == "user"
        ]

        prompt = (
            user_messages[-1]
            if user_messages
            else ""
        )

        content = (
            "NEXUS-SENSE mock response: "
            f"processed {len(prompt)} characters."
        )

        return LLMResponse(
            content=content,
            model=self.model_name,
            provider=self.provider,
            finish_reason="stop",
            input_tokens=len(prompt) // 4,
            output_tokens=len(content) // 4,
            total_tokens=(
                len(prompt) // 4
                + len(content) // 4
            ),
        )

    async def health(self) -> bool:
        return True


class MockEmbeddingModel:
    """
    Deterministic embedding model.

    It creates a stable pseudo-vector from SHA-256. This is only for
    tests and development plumbing, not semantic representation.
    """

    provider = "mock"

    model_name = "mock-embedding"

    dimensions = 32

    async def embed(
        self,
        text: str,
    ) -> Embedding:

        digest = hashlib.sha256(
            text.encode("utf-8")
        ).digest()

        vector = [
            byte / 255.0
            for byte in digest[: self.dimensions]
        ]

        return Embedding(
            vector,
            model=self.model_name,
        )

    async def embed_many(
        self,
        texts: Sequence[str],
    ) -> list[Embedding]:

        return [
            await self.embed(text)
            for text in texts
        ]

    async def health(self) -> bool:
        return True

    def describe(self):
        return {
            "provider": self.provider,
            "model": self.model_name,
            "dimensions": self.dimensions,
        }