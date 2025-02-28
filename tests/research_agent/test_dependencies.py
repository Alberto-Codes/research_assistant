"""
Tests for the dependencies module.

This module tests the functionality of the GraphDependencies class and
related components, including the LLM client implementations.
"""

import asyncio
from typing import Protocol

import pytest

from research_agent.core.dependencies import HelloWorldDependencies as GraphDependencies
from research_agent.core.dependencies import (
    LLMClient,
    MockLLMClient,
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
async def test_mock_llm_client():
    """Test that the MockLLMClient generates the expected responses."""
    # Arrange
    client = MockLLMClient()

    # Act
    hello_response = await client.generate_text("Generate a greeting word like 'Hello'")
    world_response = await client.generate_text("Generate a noun like 'World'")
    other_response = await client.generate_text("Generate something else")

    # Assert
    assert hello_response == "Hello"
    assert world_response == "World"
    assert other_response == "I'm a mock LLM client!"


@pytest.mark.asyncio
async def test_custom_llm_client():
    """Test that a custom LLM client implementation works correctly."""
    # Arrange
    client = CustomTestLLMClient(prefix="Test")

    # Act
    hello_response = await client.generate_text("Generate a greeting word like 'Hello'")
    world_response = await client.generate_text("Generate a noun like 'World'")

    # Assert
    assert hello_response == "Test Hello"
    assert world_response == "Test World"


@pytest.mark.asyncio
async def test_graph_dependencies_default_init():
    """Test that GraphDependencies initializes with a default MockLLMClient."""
    # Arrange & Act
    deps = GraphDependencies()

    # Assert
    assert deps.llm_client is not None
    assert isinstance(deps.llm_client, MockLLMClient)


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
