"""
Dependencies for the RAG graph in the Research Agent.

This module defines the dependencies that can be injected into nodes,
including the ChromaDB collection and Gemini model required for
retrieval and generation.
"""

import logging
from dataclasses import dataclass
from typing import Any, Optional, Protocol

# Import conditionally so the module can be loaded without the actual dependencies
try:
    from chromadb import Collection
    from pydantic_ai.models.vertexai import VertexAIModel
except ImportError:
    # These are used only for type annotations, so runtime errors are avoided
    Collection = Any  # type: ignore
    VertexAIModel = Any  # type: ignore

# Module-specific logger
logger = logging.getLogger(__name__)


@dataclass
class RAGDependencies:
    """Container for all dependencies needed by the RAG graph nodes.

    This class centralizes all external dependencies required by the graph,
    making it easier to provide different implementations for testing,
    development, or production environments.

    Attributes:
        chroma_collection: ChromaDB collection for document retrieval
        gemini_model: Vertex AI model for generating responses
        project_id: The Google Cloud project ID (optional)
    """

    chroma_collection: Collection
    gemini_model: VertexAIModel
    project_id: Optional[str] = None
