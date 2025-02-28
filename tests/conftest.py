"""
Pytest configuration file for the Pydantic Graph test suite.

This file contains fixtures and configuration for the pytest test suite,
including fixtures for states, dependencies, and LLM clients used across
multiple test modules.
"""

import asyncio
import pytest

from hello_world.core.state import MyState
from hello_world.core.dependencies import HelloWorldDependencies as GraphDependencies, MockLLMClient, LLMClient


# We're removing the custom event_loop fixture and using the one provided by pytest-asyncio
# Set default loop scope for asyncio fixtures
pytest_plugins = ["pytest_asyncio"]


@pytest.fixture
def initial_state():
    """Provide a clean initial state for tests.
    
    Returns:
        A fresh MyState instance with default values.
    """
    return MyState()


@pytest.fixture
def mock_dependencies():
    """Provide mock dependencies with a MockLLMClient.
    
    Returns:
        A GraphDependencies instance configured with a MockLLMClient.
    """
    return GraphDependencies(llm_client=MockLLMClient())


class TestLLMClient:
    """A test LLM client that returns predefined responses.
    
    This client tracks calls made to it and returns predefined responses,
    making it useful for verifying that the correct prompts are used.
    
    Attributes:
        hello_response: The response to return for hello prompts.
        world_response: The response to return for world prompts.
        calls: A list tracking all prompts sent to the client.
    """
    
    def __init__(self, hello_response="Test Hello", world_response="Test World"):
        """Initialize the test LLM client with predefined responses.
        
        Args:
            hello_response: The response to return for hello prompts.
            world_response: The response to return for world prompts.
        """
        self.hello_response = hello_response
        self.world_response = world_response
        self.calls = []
    
    async def generate_text(self, prompt: str) -> str:
        """Generate text based on the prompt, tracking calls.
        
        Args:
            prompt: The text prompt to generate from.
            
        Returns:
            Predefined responses based on the content of the prompt.
        """
        self.calls.append(prompt)
        
        if "hello" in prompt.lower():
            return self.hello_response
        elif "world" in prompt.lower():
            return self.world_response
        return "Test Response"


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
        A GraphDependencies instance configured with the TestLLMClient.
    """
    return GraphDependencies(llm_client=test_llm_client) 