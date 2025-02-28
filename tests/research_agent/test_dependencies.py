"""
Tests for the dependencies module.

This module tests the functionality of the GraphDependencies class and
related components, including the LLM client implementations.
"""

import asyncio
from typing import Protocol

import pytest

from research_agent.core.dependencies import (
    GeminiLLMClient,
)
from research_agent.core.dependencies import HelloWorldDependencies as GraphDependencies
from research_agent.core.dependencies import (
    LLMClient,
)


class CustomTestLLMClient:
    """A custom test LLM client implementation."""

    def __init__(self, prefix="Custom"):
        self.prefix = prefix

    async def generate_text(self, prompt: str) -> str:
        """Generate text with a custom prefix."""
        if "hello" in prompt.lower():
            return f"{self.prefix} Hello"
        elif "world" in prompt.lower():
            return f"{self.prefix} World"
        return f"{self.prefix} Response"


@pytest.mark.asyncio
async def test_graph_dependencies_default_init():
    """Test that GraphDependencies initializes with a default GeminiLLMClient."""
    # Arrange & Act
    deps = GraphDependencies()

    # Assert
    assert deps.llm_client is not None
    assert isinstance(deps.llm_client, GeminiLLMClient)


@pytest.mark.asyncio
async def test_graph_dependencies_custom_client():
    """Test that GraphDependencies can be initialized with a custom LLM client."""
    # Arrange
    custom_client = CustomTestLLMClient()

    # Act
    deps = GraphDependencies(llm_client=custom_client)

    # Assert
    assert deps.llm_client is custom_client

    # Verify it works through the dependencies
    hello_response = await deps.llm_client.generate_text("Generate a greeting word like 'Hello'")
    assert hello_response == "Custom Hello"
