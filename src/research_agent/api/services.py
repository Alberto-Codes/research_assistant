"""
Services for the Research Agent application.

This module provides service functions that can be used by different interfaces
(CLI, Streamlit, FastAPI) to access the core functionality of the application.
"""

from typing import Any, Dict, List, Optional, Tuple

from pydantic_graph import Graph

from research_agent.core.document.graph import (
    load_documents_from_directory,
    run_document_ingestion_graph,
)
from research_agent.core.document.state import DocumentState
from research_agent.core.gemini.dependencies import GeminiDependencies
from research_agent.core.gemini.graph import get_gemini_agent_graph as core_get_gemini_agent_graph
from research_agent.core.gemini.graph import run_gemini_agent_graph
from research_agent.core.gemini.nodes import GeminiAgentNode
from research_agent.core.gemini.state import GeminiState

# Try to import GraphDeps, or define it if not available
try:
    from pydantic_graph import GraphDeps
except ImportError:
    # Define GraphDeps locally if not available in pydantic_graph
    class GraphDeps:
        """Mock GraphDeps class used when the real one is not available."""

        pass


async def generate_ai_response(user_prompt: str, project_id: Optional[str] = None) -> GeminiState:
    """
    Generate an AI response using the Gemini model.

    Args:
        user_prompt: The user's prompt to send to the Gemini model.
        project_id: Optional Google Cloud project ID. If None, will try to detect from environment.

    Returns:
        The final state after running the graph.
    """
    # Create dependencies with Gemini configuration
    dependencies = GeminiDependencies(project_id=project_id)

    # Use the run_gemini_agent_graph function
    output, final_state, history = await run_gemini_agent_graph(
        user_prompt=user_prompt, dependencies=dependencies
    )
    return final_state


def get_gemini_agent_graph() -> Graph:
    """
    Get the Gemini agent graph.

    Returns:
        A configured Graph instance.
    """
    # Use the imported function from core module
    return core_get_gemini_agent_graph()


async def ingest_documents(
    documents: List[str],
    collection_name: str,
    document_ids: Optional[List[str]] = None,
    metadata: Optional[List[Dict[str, Any]]] = None,
    persist_directory: str = "./chroma_db",
) -> Dict[str, Any]:
    """
    Ingest documents into a ChromaDB collection.

    This service function wraps the document ingestion graph to provide
    an easy-to-use interface for document ingestion from different interfaces.

    Args:
        documents: List of document content strings to be ingested.
        collection_name: Name of the ChromaDB collection to use.
        document_ids: Optional list of IDs for the documents.
        metadata: Optional list of metadata dictionaries for the documents.
        persist_directory: Directory where ChromaDB data should be persisted.

    Returns:
        A dictionary with ingestion results.
    """
    # Run the document ingestion graph
    result, state, errors = await run_document_ingestion_graph(
        documents=documents,
        collection_name=collection_name,
        document_ids=document_ids,
        metadata=metadata,
        persist_directory=persist_directory,
    )

    # Return a dictionary with detailed results
    return {
        "result": result,
        "state": {
            "documents_count": len(documents),
            "collection_name": collection_name,
            "total_time": getattr(state, "total_time", 0),
            "execution_history": getattr(state, "node_execution_history", []),
        },
        "errors": errors,
        "success": len(errors) == 0,
    }


async def ingest_documents_from_directory(
    directory_path: str,
    collection_name: str,
    persist_directory: str = "./chroma_db",
) -> Dict[str, Any]:
    """
    Load documents from a directory and ingest them into a ChromaDB collection.

    This service function combines loading documents from a directory and
    ingesting them into ChromaDB.

    Args:
        directory_path: The path to the directory containing document files.
        collection_name: Name of the ChromaDB collection to use.
        persist_directory: Directory where ChromaDB data should be persisted.

    Returns:
        A dictionary with ingestion results.
    """
    # Load documents from the directory
    document_dicts = load_documents_from_directory(directory_path)

    if not document_dicts:
        return {
            "success": False,
            "errors": ["No documents found in the specified directory"],
            "state": {
                "documents_count": 0,
                "collection_name": collection_name,
                "total_time": 0,
            },
        }

    # Extract content and metadata
    documents = [doc["content"] for doc in document_dicts]
    metadata = [doc["metadata"] for doc in document_dicts]

    # Generate document IDs based on filenames
    document_ids = [f"doc_{i}_{meta['filename']}" for i, meta in enumerate(metadata)]

    # Call the document ingestion service
    return await ingest_documents(
        documents=documents,
        collection_name=collection_name,
        document_ids=document_ids,
        metadata=metadata,
        persist_directory=persist_directory,
    )
