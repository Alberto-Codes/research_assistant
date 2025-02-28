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


class CustomLLMClient:
    """A custom LLM client implementation that could be replaced with a real API client.
    
    This is an example showing how you could swap in different LLM implementations
    through dependency injection. In a real application, this would be replaced
    with a client that connects to an actual LLM API.
    
    Attributes:
        prefix: An optional prefix to add to each generated response.
    """
    
    def __init__(self, prefix: Optional[str] = None):
        """Initialize the custom LLM client with an optional prefix.
        
        Args:
            prefix: A prefix string to add to all generated responses.
        """
        self.prefix = prefix
    
    async def generate_text(self, prompt: str) -> str:
        """Generate text based on the prompt, adding the custom prefix if set.
        
        Args:
            prompt: The text prompt to generate from.
            
        Returns:
            The generated text, with prefix if set.
        """
        # In a real implementation, this would call an LLM API
        if "hello" in prompt.lower():
            result = "Hello"
        elif "world" in prompt.lower():
            result = "World"
        else:
            result = "Response"
            
        # Add the prefix if one is set
        if self.prefix:
            result = f"{self.prefix} {result}"
            
        return result


@dataclass
class HelloWorldDependencies:
    """Container for all dependencies needed by the Hello World graph nodes.
    
    This class centralizes all external dependencies required by the graph,
    making it easier to provide different implementations for testing,
    development, or production environments.
    
    Attributes:
        llm_client: The LLM client to use for text generation.
        use_custom_llm: Whether to use the custom LLM client or the mock client.
        prefix: Optional prefix to add to LLM responses when using the custom client.
    """
    
    use_custom_llm: bool = False
    prefix: Optional[str] = None
    llm_client: Optional[LLMClient] = None
    
    def __post_init__(self):
        """Initialize default dependencies if not provided.
        
        This method is automatically called after initialization to
        set up default dependencies based on the configuration.
        """
        if self.llm_client is None:
            if self.use_custom_llm:
                self.llm_client = CustomLLMClient(prefix=self.prefix)
            else:
                self.llm_client = MockLLMClient() 