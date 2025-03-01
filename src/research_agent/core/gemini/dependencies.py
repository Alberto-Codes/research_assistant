"""
Dependencies for the Gemini graph in the Research Agent.

This module defines the dependencies that can be injected into nodes,
including the LLMClient protocol and its implementations using the
Gemini model via Pydantic-AI.
"""

import logging
from dataclasses import dataclass
from typing import Any, Optional, Protocol

from pydantic_ai import Agent
from pydantic_ai.models.vertexai import VertexAIModel

# Module-specific logger
logger = logging.getLogger(__name__)


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
    Google's Gemini Flash model for generating responses to user prompts.

    Attributes:
        vertex_model: The Pydantic-AI VertexAIModel instance.
        agent: The Pydantic-AI Agent with the configured model.
    """

    def __init__(
        self,
        project_id: Optional[str] = None,
        location: str = "us-central1",
        model_name: str = "gemini-1.5-flash-001",
    ) -> None:
        """Initialize the Gemini LLM client with Pydantic-AI.

        Args:
            project_id: The Google Cloud project ID. If None, will try to detect from environment.
            location: The Google Cloud region where the model is deployed.
            model_name: The name of the Gemini model to use.

        Raises:
            Exception: If there is an error initializing the client.
        """
        self.project_id = project_id
        self.location = location
        self.model_name = model_name
        self.vertex_model = None
        self.agent = None

        # Log the configuration
        logger.info(
            "Initializing GeminiLLMClient with project_id=%s, location=%s, model=%s",
            project_id or "(auto-detect)",
            location,
            model_name,
        )

        try:
            # Initialize the model and agent at creation time
            self.vertex_model = VertexAIModel(
                model_name=model_name, project_id=project_id, region=location
            )
            self.agent = Agent(self.vertex_model)
            logger.info("Successfully initialized Gemini model and agent")
        except Exception as e:
            logger.error(f"Error initializing GeminiLLMClient: {e}")
            raise

    async def generate_text(self, prompt: str) -> str:
        """Generate text using Gemini model based on a prompt.

        Args:
            prompt: The prompt to send to the model.

        Returns:
            The generated text response from Gemini.
        """
        try:
            # Generate a response using the pre-initialized agent
            result = await self.agent.run(prompt)

            # More robust attribute access with getattr and default
            return getattr(result, "data", str(result))
        except Exception as e:
            error_msg = f"Error generating text with Gemini via Pydantic-AI: {e}"
            logger.error(error_msg)
            return f"Error generating response: {e}"


@dataclass
class GeminiDependencies:
    """Container for all dependencies needed by the Gemini Agent graph nodes.

    This class centralizes all external dependencies required by the graph,
    making it easier to provide different implementations for testing,
    development, or production environments.

    Attributes:
        project_id: The Google Cloud project ID for the Gemini client.
        llm_client: The LLM client to use for text generation.
    """

    project_id: Optional[str] = None
    llm_client: Optional[LLMClient] = None

    def __post_init__(self) -> None:
        """Initialize default dependencies if not provided.

        This method is automatically called after initialization to
        set up default dependencies based on the configuration.
        """
        if self.llm_client is None:
            self.llm_client = GeminiLLMClient(project_id=self.project_id)
