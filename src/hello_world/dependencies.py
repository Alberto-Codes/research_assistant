"""
Dependencies for the Hello World graph.

This module defines the dependencies that can be injected into nodes,
including the LLMClient protocol and its implementations. It uses the
dependency injection pattern to allow for flexible component swapping.
"""

from dataclasses import dataclass
from typing import Optional, Protocol, Any


class LLMClient(Protocol):
    """Protocol defining the interface for an LLM client.
    
    This protocol ensures that any LLM client implementation provides
    the necessary methods to generate text from prompts.
    """
    
    async def generate_text(self, prompt: str) -> str:
        """Generate text based on a prompt.
        
        Args:
            prompt: The text prompt to generate from.
            
        Returns:
            The generated text response.
        """
        ...


class MockLLMClient:
    """A mock LLM client for development and testing.
    
    This implementation provides predetermined responses based on
    the content of the prompt, making it useful for testing and
    development without requiring a real LLM API.
    """
    
    async def generate_text(self, prompt: str) -> str:
        """Return a predetermined response based on the prompt.
        
        Args:
            prompt: The text prompt to generate from.
            
        Returns:
            A predetermined response based on keywords in the prompt.
        """
        if "hello" in prompt.lower():
            return "Hello"
        elif "world" in prompt.lower():
            return "World"
        else:
            return "I'm a mock LLM client!"


@dataclass
class GraphDependencies:
    """Container for all dependencies needed by the graph nodes.
    
    This class centralizes all external dependencies required by the graph,
    making it easier to provide different implementations for testing,
    development, or production environments.
    
    Attributes:
        llm_client: The LLM client to use for text generation.
    """
    
    llm_client: Optional[LLMClient] = None
    
    def __post_init__(self):
        """Initialize default dependencies if not provided.
        
        This method is automatically called after initialization to
        set up default dependencies when none are explicitly provided.
        """
        if self.llm_client is None:
            self.llm_client = MockLLMClient() 