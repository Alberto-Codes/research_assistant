"""
Graph definition for document ingestion in the Research Agent.

This module defines the graph structure for document ingestion into ChromaDB.
"""

from __future__ import annotations

import asyncio
import datetime
import logging
import os
from typing import Any, Dict, List, Optional, Tuple

# Try to import from pydantic_graph with a fallback for GraphError
try:
    from pydantic_graph import Graph, GraphError, GraphRunResult
except ImportError:
    from pydantic_graph import Graph, GraphRunResult

    # Define GraphError if it's not available in pydantic_graph
    class GraphError(Exception):
        """Error raised when a graph fails to execute."""

        pass


from research_agent.core.document.dependencies import ChromaDBDependencies
from research_agent.core.document.nodes import ChromaDBIngestionNode
from research_agent.core.document.state import DocumentState

# Set up logging
logger = logging.getLogger(__name__)


async def ingest_documents(
    documents: List[str],
    collection_name: str = "default_collection",
    document_ids: Optional[List[str]] = None,
    metadata: Optional[List[Dict[str, Any]]] = None,
    persist_directory: str = "./chroma_db",
    dependencies: Optional[ChromaDBDependencies] = None,
) -> Tuple[Dict[str, Any], DocumentState, List[Any]]:
    """
    Ingest documents into the research agent.

    This is a convenience function that calls run_document_ingestion_graph.

    Args:
        documents: List of document contents to ingest.
        collection_name: Name of the collection to store documents in.
        document_ids: Optional list of document IDs.
        metadata: Optional list of metadata dictionaries.
        persist_directory: Directory to persist ChromaDB.
        dependencies: Optional dependencies to inject into the graph.

    Returns:
        A tuple containing the result dictionary, the final state, and any errors.
    """
    return await run_document_ingestion_graph(
        documents,
        collection_name,
        document_ids,
        metadata,
        persist_directory,
        dependencies,
    )


def get_document_ingestion_graph() -> Graph:
    """
    Create a Graph for document ingestion into ChromaDB.

    This function creates a Graph for running a node that ingests documents
    into a ChromaDB collection.

    Returns:
        A Graph with a ChromaDBIngestionNode.
    """
    # Create and return the graph with the ChromaDBIngestionNode
    node = ChromaDBIngestionNode()
    return Graph(nodes=[node])


async def run_document_ingestion_graph(
    documents: List[str],
    collection_name: str = "default_collection",
    document_ids: Optional[List[str]] = None,
    metadata: Optional[List[Dict[str, Any]]] = None,
    persist_directory: str = "./chroma_db",
    dependencies: Optional[ChromaDBDependencies] = None,
) -> Tuple[Dict[str, Any], DocumentState, List[Any]]:
    """
    Run the document ingestion graph with a list of documents.

    This function creates a state with the documents, creates a graph,
    and runs it to ingest the documents into ChromaDB.

    Args:
        documents: The list of document contents to ingest.
        collection_name: The name of the ChromaDB collection to use.
        document_ids: Optional list of IDs for the documents.
        metadata: Optional list of metadata dictionaries for the documents.
        persist_directory: The directory where ChromaDB will persist data.
        dependencies: Optional dependencies to inject into the graph.
            If None, default dependencies will be created.

    Returns:
        A tuple containing the ingestion result dictionary, the final state, and any errors.
    """
    # Create a state with the documents
    state = DocumentState(
        documents=documents,
        document_ids=document_ids,
        metadata=metadata,
        chroma_collection_name=collection_name,
    )

    # Create dependencies if not provided
    if dependencies is None:
        dependencies = ChromaDBDependencies(persist_directory=persist_directory)

    # Get the document ingestion graph
    graph = get_document_ingestion_graph()

    # Start timing
    start_time = datetime.datetime.now()
    logger.info("Starting document ingestion graph at %s", start_time)

    # Run the graph
    try:
        result = await graph.run(ChromaDBIngestionNode(), state=state, deps=dependencies)
        result_dict = result.output
        final_state = result.state
        errors = []

    except GraphError as e:
        # Log the error
        logger.error("Document ingestion graph failed: %s", str(e))

        # Return error information
        result_dict = {"error": str(e)}
        final_state = state
        errors = [str(e)]

    # Calculate and log execution time
    end_time = datetime.datetime.now()
    execution_time = (end_time - start_time).total_seconds()
    logger.info("Document ingestion graph completed in %.3f seconds", execution_time)

    return result_dict, final_state, errors


def load_documents_from_directory(directory_path: str) -> List[Dict[str, Any]]:
    """
    Load documents from files in a directory.

    This function loads all text files from a directory and returns them
    as a list of dictionaries with document content and metadata.

    Args:
        directory_path: The path to the directory containing document files.

    Returns:
        A list of dictionaries with document content and metadata.
    """
    documents = []

    # Check if directory exists
    if not os.path.exists(directory_path) or not os.path.isdir(directory_path):
        logger.error(f"Directory '{directory_path}' does not exist or is not a directory")
        return documents

    # Get all files in the directory
    try:
        files = [
            f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))
        ]

        for file_name in files:
            file_path = os.path.join(directory_path, file_name)

            # Read the file content
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read()

                # Create metadata for the document
                file_info = os.stat(file_path)
                metadata = {
                    "filename": file_name,
                    "file_path": file_path,
                    "file_size": file_info.st_size,
                    "created": datetime.datetime.fromtimestamp(file_info.st_ctime).isoformat(),
                    "modified": datetime.datetime.fromtimestamp(file_info.st_mtime).isoformat(),
                }

                # Add document to the list
                documents.append({"content": content, "metadata": metadata})

                logger.info(f"Loaded document from '{file_path}'")

            except Exception as e:
                logger.error(f"Error reading file '{file_path}': {e}")

    except Exception as e:
        logger.error(f"Error listing files in directory '{directory_path}': {e}")

    logger.info("Loaded %d documents from %s", len(documents), directory_path)
    return documents 