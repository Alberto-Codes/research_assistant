"""
Dependencies for the Hello World graph.

This module defines the dependencies that can be injected into nodes,
including the LLMClient protocol and its implementations. It uses the
dependency injection pattern to allow for flexible component swapping.
"""

from dataclasses import dataclass
from typing import Optional, Protocol

from pydantic_ai import Agent

# Replace Google Cloud imports with pydantic_ai imports
from pydantic_ai.models.vertexai import VertexAIModel


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
        model_name: str = "gemini-1.5-flash-001",
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
                model_name, project_id=project_id, region=location if location else "us-central1"
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
            if hasattr(result, "data"):
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
        project_id: The Google Cloud project ID for the Gemini client.
    """

    project_id: Optional[str] = None
    llm_client: Optional[LLMClient] = None

    def __post_init__(self):
        """Initialize default dependencies if not provided.

        This method is automatically called after initialization to
        set up default dependencies based on the configuration.
        """
        if self.llm_client is None:
            self.llm_client = GeminiLLMClient(project_id=self.project_id)
