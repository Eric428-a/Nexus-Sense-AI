"""
Tests for the NEXUS-SENSE model layer.
"""

from __future__ import annotations

import pytest

from src.nexus.models.embeddings import Embedding
from src.nexus.models.llm import (
    ChatMessage,
    ChatRole,
)
from src.nexus.models.model_registry import ModelRegistry
from src.nexus.models.prompts import (
    PromptRegistry,
    PromptTemplate,
    build_default_prompts,
)
from src.nexus.models.providers.mock import (
    MockEmbeddingModel,
    MockLLM,
)


@pytest.mark.asyncio
async def test_mock_llm():
    model = MockLLM()

    response = await model.generate(
        [
            ChatMessage(
                role=ChatRole.USER,
                content="Hello NEXUS.",
            )
        ]
    )

    assert response.provider == "mock"
    assert response.model == "mock-llm"
    assert response.content


@pytest.mark.asyncio
async def test_mock_embedding():
    model = MockEmbeddingModel()

    embedding = await model.embed(
        "NEXUS-SENSE"
    )

    assert isinstance(
        embedding,
        Embedding,
    )

    assert embedding.dimensions == 32


@pytest.mark.asyncio
async def test_embedding_is_deterministic():
    model = MockEmbeddingModel()

    first = await model.embed(
        "same text"
    )

    second = await model.embed(
        "same text"
    )

    assert first.vector == second.vector


def test_model_registry():
    registry = ModelRegistry()

    llm = MockLLM()

    registry.register(
        "test-llm",
        llm,
        model_type="llm",
        provider="mock",
        capabilities={
            "text_generation",
        },
    )

    route = registry.route(
        "text_generation"
    )

    assert route.model_id == "test-llm"
    assert route.provider == "mock"
    assert route.model is llm


def test_model_registry_provider_filter():
    registry = ModelRegistry()

    llm = MockLLM()

    registry.register(
        "test-llm",
        llm,
        model_type="llm",
        provider="mock",
        capabilities={
            "text_generation",
        },
    )

    route = registry.route(
        "text_generation",
        provider="mock",
    )

    assert route.model is llm


def test_model_registry_missing_capability():
    registry = ModelRegistry()

    with pytest.raises(LookupError):
        registry.route(
            "unknown-capability"
        )


def test_model_registry_duplicate():
    registry = ModelRegistry()

    model = MockLLM()

    registry.register(
        "model",
        model,
        model_type="llm",
        provider="mock",
    )

    with pytest.raises(ValueError):
        registry.register(
            "model",
            model,
            model_type="llm",
            provider="mock",
        )


def test_prompt_registry():
    registry = PromptRegistry()

    registry.register(
        PromptTemplate(
            name="test",
            version="1.0.0",
            system="System",
            user_template="Hello {name}",
        )
    )

    messages = registry.render(
        "test",
        name="NEXUS",
    )

    assert messages[0]["role"] == "system"
    assert messages[1]["content"] == (
        "Hello NEXUS"
    )


def test_default_prompts():
    registry = build_default_prompts()

    templates = registry.list_templates()

    assert "research-analysis:1.0.0" in templates
    assert "evidence-reasoning:1.0.0" in templates
    assert "intelligence-summary:1.0.0" in templates