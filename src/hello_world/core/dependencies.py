"""
Dependencies for the Hello World graph.

This module defines the dependencies that can be injected into nodes,
including the LLMClient protocol and its implementations. It uses the
dependency injection pattern to allow for flexible component swapping.
"""

from dataclasses import dataclass
from typing import Optional, Protocol, Any
import warnings
import functools

# Replace Google Cloud imports with pydantic_ai imports
from pydantic_ai.models.vertexai import VertexAIModel
from pydantic_ai import Agent


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
    """A mock LLM client that returns pre-defined responses.
    
    This client is used for testing and development purposes,
    avoiding the need to call actual LLM APIs.
    """
    
    async def generate_text(self, prompt: str) -> str:
        """Return a fixed mock response.
        
        Args:
            prompt: The text prompt (ignored in this implementation).
            
        Returns:
            A fixed mock response.
        """
        return "This is a mock response from an LLM. In a real implementation, this would be generated text."


class CustomLLMClient:
    """A custom LLM client that returns pre-defined responses with a prefix.
    
    This client is used for testing and development with custom prefixes,
    avoiding the need to call actual LLM APIs.
    """
    
    def __init__(self, prefix: Optional[str] = None):
        """Initialize the custom LLM client.
        
        Args:
            prefix: Optional prefix to add to the generated text.
        """
        self.prefix = prefix or ""
    
    async def generate_text(self, prompt: str) -> str:
        """Return a fixed response with an optional prefix.
        
        Args:
            prompt: The text prompt (ignored in this implementation).
            
        Returns:
            A fixed response with an optional prefix.
        """
        text = "This is a custom response from an LLM with a prefix."
        if self.prefix:
            text = f"{self.prefix} {text}"
        return text


def deprecated(func):
    """Mark a function or class as deprecated with a warning."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        warnings.warn(
            f"{func.__name__} is deprecated and will be removed in a future version. "
            "Use proper pytest mocks instead for testing.",
            category=DeprecationWarning,
            stacklevel=2
        )
        return func(*args, **kwargs)
    return wrapper


@deprecated
class MockGeminiLLMClient:
    """A mock Gemini LLM client for local testing without authentication.
    
    DEPRECATED: This class is deprecated and will be removed in the future.
    For testing, use pytest fixtures and mocks instead.
    
    This client simulates the behavior of the Gemini API for development
    and testing purposes when you don't have VertexAI credentials configured.
    """
    
    def __init__(self):
        """Initialize the mock Gemini LLM client."""
        warnings.warn(
            "MockGeminiLLMClient is deprecated. Use pytest fixtures for testing instead.",
            DeprecationWarning,
            stacklevel=2
        )
        self.responses = {
            "What are the three laws of robotics?": """The Three Laws of Robotics, introduced by science fiction writer Isaac Asimov in his 1942 short story "Runaround," are:

1. First Law: A robot may not injure a human being or, through inaction, allow a human being to come to harm.

2. Second Law: A robot must obey the orders given it by human beings except where such orders would conflict with the First Law.

3. Third Law: A robot must protect its own existence as long as such protection does not conflict with the First or Second Law.

Asimov later added a "Zeroth Law" that preceded the others: A robot may not harm humanity, or, by inaction, allow humanity to come to harm.""",
            "What's the significance of the number 42 in literature?": """The number 42 has special significance in literature primarily due to Douglas Adams' science fiction series "The Hitchhiker's Guide to the Galaxy." In this work, 42 is revealed to be "the Answer to the Ultimate Question of Life, the Universe, and Everything," calculated by a supercomputer named Deep Thought over a period of 7.5 million years.

The humor lies in the fact that while the characters know the answer is 42, they don't know what the actual question is, rendering the answer meaningless. This has made 42 a popular cultural reference symbolizing the futility of seeking simple answers to complex philosophical questions.

Beyond Adams' work, the number appears in Lewis Carroll's "Alice's Adventures in Wonderland," where Rule 42 is mentioned in the trial scene ("All persons more than a mile high to leave the court"). Some scholars have speculated that Adams, who studied English literature, may have been influenced by this reference.

The number 42 has since taken on a life of its own in geek culture, appearing as an Easter egg in numerous books, films, television shows, and video games as an homage to Adams' influential work."""
        }
    
    async def generate_text(self, prompt: str) -> str:
        """Generate a mock response based on the prompt.
        
        Args:
            prompt: The text prompt to generate from.
            
        Returns:
            A pre-defined response for known prompts or a generic response.
        """
        # Check if we have a pre-defined response for this prompt
        for key, response in self.responses.items():
            if key.lower() in prompt.lower():
                return response
        
        # Fallback generic response
        return f"This is a mock response to your question about '{prompt[:30]}...'. In a production environment, this would be generated by the actual Gemini model through Vertex AI."


class GeminiLLMClient:
    """A client for Google Vertex AI's Gemini model using Pydantic-AI.
    
    This implementation uses Pydantic-AI's VertexAIModel to connect to
    Google's Gemini Flash 2.0 model for generating responses to user prompts.
    
    Attributes:
        model_name: The name of the Gemini model to use.
        agent: The Pydantic-AI Agent with the configured model.
    """
    
    def __init__(
        self, 
        project_id: Optional[str] = None,
        location: str = "us-central1",
        model_name: str = "gemini-1.5-flash-001"
    ):
        """Initialize the Gemini LLM client with Pydantic-AI.
        
        Args:
            project_id: The Google Cloud project ID. If None, will try to detect from environment.
            location: The Google Cloud region where the model is deployed.
            model_name: The name of the Gemini model to use.
        """
        # Create a Pydantic-AI VertexAIModel and Agent
        try:
            # Create VertexAI model with the correct parameters
            self.vertex_model = VertexAIModel(
                model_name,
                project_id=project_id,
                region=location if location else "us-central1"
            )
            
            # Create an agent with the model
            self.agent = Agent(self.vertex_model)
        except Exception as e:
            print(f"Error initializing GeminiLLMClient: {str(e)}")
            raise
    
    async def generate_text(self, prompt: str) -> str:
        """Generate text using Gemini model based on a prompt.
        
        Args:
            prompt: The text prompt to generate from.
            
        Returns:
            The generated text response from Gemini.
        """
        try:
            # Use the Pydantic-AI Agent's run method
            result = await self.agent.run(prompt)
            
            # Extract the data from the AgentRunResult
            if hasattr(result, 'data'):
                return result.data
            else:
                # In case the result structure changes in the future
                return str(result)
                
        except Exception as e:
            error_msg = f"Error generating text with Gemini via Pydantic-AI: {str(e)}"
            print(error_msg)
            return f"Error generating response: {str(e)}"


@dataclass
class HelloWorldDependencies:
    """Container for all dependencies needed by the Hello World graph nodes.
    
    This class centralizes all external dependencies required by the graph,
    making it easier to provide different implementations for testing,
    development, or production environments.
    
    Attributes:
        llm_client: The LLM client to use for text generation.
        use_custom_llm: Whether to use the custom LLM client or the mock client.
        use_gemini: Whether to use the Gemini LLM client.
        use_mock_gemini: Whether to use the mock Gemini client for local testing.
        prefix: Optional prefix to add to LLM responses when using the custom client.
        project_id: The Google Cloud project ID for the Gemini client.
    """
    
    use_custom_llm: bool = False
    use_gemini: bool = False
    use_mock_gemini: bool = False
    prefix: Optional[str] = None
    project_id: Optional[str] = None
    llm_client: Optional[LLMClient] = None
    
    def __post_init__(self):
        """Initialize default dependencies if not provided.
        
        This method is automatically called after initialization to
        set up default dependencies based on the configuration.
        """
        if self.llm_client is None:
            if self.use_gemini:
                if self.use_mock_gemini:
                    warnings.warn(
                        "The use_mock_gemini flag is deprecated. For testing, "
                        "use pytest fixtures and monkeypatching instead.",
                        DeprecationWarning,
                        stacklevel=2
                    )
                    self.llm_client = MockGeminiLLMClient()
                else:
                    self.llm_client = GeminiLLMClient(project_id=self.project_id)
            elif self.use_custom_llm:
                self.llm_client = CustomLLMClient(prefix=self.prefix)
            else:
                self.llm_client = MockLLMClient() 