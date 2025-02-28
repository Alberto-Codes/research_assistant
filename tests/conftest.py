"""
Pytest configuration file for the Pydantic Graph test suite.

This file contains fixtures and configuration for the pytest test suite.
"""

import asyncio
import pytest

from hello_world.state import MyState
from hello_world.dependencies import GraphDependencies, MockLLMClient, LLMClient


# We're removing the custom event_loop fixture and using the one provided by pytest-asyncio
# Set default loop scope for asyncio fixtures
pytest_plugins = ["pytest_asyncio"]


@pytest.fixture
def initial_state():
    """Fixture providing a clean initial state for tests."""
    return MyState()


@pytest.fixture
def mock_dependencies():
    """Fixture providing mock dependencies with a MockLLMClient."""
    return GraphDependencies(llm_client=MockLLMClient())


class TestLLMClient:
    """A test LLM client that returns predefined responses."""
    
    def __init__(self, hello_response="Test Hello", world_response="Test World"):
        self.hello_response = hello_response
        self.world_response = world_response
        self.calls = []
    
    async def generate_text(self, prompt: str) -> str:
        """Generate text based on the prompt, tracking calls."""
        self.calls.append(prompt)
        
        if "hello" in prompt.lower():
            return self.hello_response
        elif "world" in prompt.lower():
            return self.world_response
        return "Test Response"


@pytest.fixture
def test_llm_client():
    """Fixture providing a test LLM client that tracks calls."""
    return TestLLMClient()


@pytest.fixture
def test_dependencies(test_llm_client):
    """Fixture providing test dependencies with a TestLLMClient."""
    return GraphDependencies(llm_client=test_llm_client) 