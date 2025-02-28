"""
Dependencies for the Hello World graph.

This module defines the dependencies that can be injected into nodes.
"""

from dataclasses import dataclass
from typing import Optional, Protocol, Any


class LLMClient(Protocol):
    """Protocol defining the interface for an LLM client."""
    
    async def generate_text(self, prompt: str) -> str:
        """Generate text based on a prompt."""
        ...


class MockLLMClient:
    """A mock LLM client for development and testing."""
    
    async def generate_text(self, prompt: str) -> str:
        """Return a predetermined response based on the prompt."""
        if "hello" in prompt.lower():
            return "Hello"
        elif "world" in prompt.lower():
            return "World"
        else:
            return "I'm a mock LLM client!"


@dataclass
class GraphDependencies:
    """Container for all dependencies needed by the graph nodes."""
    
    llm_client: Optional[LLMClient] = None
    
    def __post_init__(self):
        """Initialize default dependencies if not provided."""
        if self.llm_client is None:
            self.llm_client = MockLLMClient() 