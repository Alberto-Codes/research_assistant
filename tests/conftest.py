"""
Pytest configuration file for the Pydantic Graph test suite.

This file contains fixtures and configuration for the pytest test suite,
including fixtures for states, dependencies, and LLM clients used across
multiple test modules.
"""

import asyncio

import pytest

from research_agent.core.gemini.dependencies import (
    GeminiDependencies,
    GeminiLLMClient,
    LLMClient,
)
from research_agent.core.gemini.state import GeminiState

# We're removing the custom event_loop fixture and using the one provided by pytest-asyncio
# Set default loop scope for asyncio fixtures
pytest_plugins = ["pytest_asyncio"]


@pytest.fixture
def initial_state():
    """Provide a clean initial state for tests.

    Returns:
        A fresh GeminiState instance with default values.
    """
    return GeminiState()


@pytest.fixture
def mock_dependencies():
    """Provide mock dependencies with a GeminiLLMClient.

    Returns:
        A GeminiDependencies instance configured with a GeminiLLMClient.
    """
    return GeminiDependencies(llm_client=GeminiLLMClient())


class TestLLMClient:
    """A test LLM client that returns predefined responses.

    This client tracks calls made to it and returns predefined responses,
    making it useful for verifying that the correct prompts are used.

    Attributes:
        calls: A list tracking all prompts sent to the client.
    """

    def __init__(self, default_response="Test Response"):
        """Initialize the test LLM client with a default response.

        Args:
            default_response: The default response to return for prompts.
        """
        self.default_response = default_response
        self.calls = []

    async def generate_text(self, prompt: str) -> str:
        """Generate text based on the prompt, tracking calls.

        Args:
            prompt: The text prompt to generate from.

        Returns:
            Predefined response for the prompt.
        """
        self.calls.append(prompt)
        return self.default_response


@pytest.fixture
def test_llm_client():
    """Provide a test LLM client that tracks calls.

    Returns:
        A TestLLMClient instance.
    """
    return TestLLMClient()


@pytest.fixture
def test_dependencies(test_llm_client):
    """Provide test dependencies with a TestLLMClient.

    Args:
        test_llm_client: The TestLLMClient instance from the fixture.

    Returns:
        A GeminiDependencies instance configured with the TestLLMClient.
    """
    return GeminiDependencies(llm_client=test_llm_client)
