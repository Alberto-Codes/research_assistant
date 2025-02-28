"""
Tests for the dependencies module.

This module tests the functionality of the GeminiDependencies class and
related components, including the LLM client implementations.
"""

import asyncio
from typing import Protocol

import pytest

from research_agent.core.dependencies import (
    GeminiDependencies,
    GeminiLLMClient,
    LLMClient,
)


class CustomTestLLMClient:
    """A custom test LLM client implementation."""

    def __init__(self, prefix="Custom"):
        self.prefix = prefix

    async def generate_text(self, prompt: str) -> str:
        """Generate text with a custom prefix."""
        return f"{self.prefix} response to: {prompt}"


@pytest.mark.asyncio
async def test_gemini_dependencies_default_init():
    """Test that GeminiDependencies initializes with default values."""
    # Arrange & Act
    deps = GeminiDependencies()

    # Assert
    assert deps.project_id is None
    assert deps.llm_client is not None
    assert isinstance(deps.llm_client, GeminiLLMClient)


@pytest.mark.asyncio
async def test_gemini_dependencies_custom_client():
    """Test that GeminiDependencies works with a custom LLM client."""
    # Arrange
    custom_client = CustomTestLLMClient()

    # Act
    deps = GeminiDependencies(llm_client=custom_client)
    result = await deps.llm_client.generate_text("Test prompt")

    # Assert
    assert deps.llm_client is custom_client
    assert result == "Custom response to: Test prompt"


if __name__ == "__main__":
    """Run the tests directly."""
    pytest.main(["-xvs", __file__])
