"""
Graph definition for document ingestion in the Research Agent.

This module defines the graph structure for document ingestion into ChromaDB.
"""

from __future__ import annotations

import asyncio
import datetime
import logging
import os
from dataclasses import dataclass
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


from research_agent.core.document.dependencies import ChromaDBDependencies, DoclingDependencies
from research_agent.core.document.nodes import ChromaDBIngestionNode, DoclingProcessorNode, FileTypeRouterNode
from research_agent.core.document.state import DocumentState
from research_agent.core.document_processing.docling_processor import DoclingProcessorOptions

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
    Ingest documents into ChromaDB.

    This function takes a list of document strings and ingests them into a
    ChromaDB collection, using document IDs and metadata if provided.

    Args:
        documents: The list of document strings to ingest.
        collection_name: The name of the ChromaDB collection to use.
        document_ids: Optional list of IDs for the documents.
        metadata: Optional list of metadata dictionaries for the documents.
        persist_directory: The directory to persist the ChromaDB data.
        dependencies: Dependencies for ChromaDB (optional).

    Returns:
        A tuple containing (output, final state, logs).
    """
    # Create initial state
    state = DocumentState(
        documents=documents,
        document_ids=document_ids,
        metadata=metadata,
        chroma_collection_name=collection_name,
        node_execution_history=[],
    )
    
    # Create default document IDs if not provided
    if not state.document_ids or len(state.document_ids) != len(documents):
        logger.info("Creating default document IDs")
        state.document_ids = []
        for i, doc in enumerate(documents):
            # Check if there's metadata with a document_id
            doc_id = None
            if state.metadata and i < len(state.metadata) and "document_id" in state.metadata[i]:
                doc_id = state.metadata[i]["document_id"]
            elif state.metadata and i < len(state.metadata) and "filename" in state.metadata[i]:
                # Extract base name and extension if available in metadata
                filename = state.metadata[i]["filename"]
                base_name = state.metadata[i].get("base_name", os.path.splitext(filename)[0])
                extension = state.metadata[i].get("file_extension", os.path.splitext(filename)[1].lstrip('.'))
                doc_id = f"doc_{i}_{base_name}_type_{extension}"
            else:
                # Default ID
                doc_id = f"doc_{i}"
            
            state.document_ids.append(doc_id)
    
    # Set up dependencies
    deps = dependencies or ChromaDBDependencies(persist_directory=persist_directory)
    
    # Run the document ingestion graph
    try:
        result, final_state, logs = await run_document_ingestion_graph(state, deps)
        return result, final_state, logs
    except Exception as e:
        logger.error(f"Error in document ingestion: {e}")
        raise e


async def ingest_files_with_docling(
    file_paths: List[str],
    collection_name: str = "default_collection",
    document_ids: Optional[List[str]] = None,
    metadata: Optional[List[Dict[str, Any]]] = None,
    persist_directory: str = "./chroma_db",
    docling_options: Optional[DoclingProcessorOptions] = None,
    chroma_dependencies: Optional[ChromaDBDependencies] = None,
) -> Tuple[Dict[str, Any], DocumentState, List[Any]]:
    """
    Process files with Docling and ingest them into the research agent.

    This function takes a list of file paths, processes them with Docling,
    and then ingests the processed content into ChromaDB.

    Args:
        file_paths: List of file paths to process with Docling.
        collection_name: Name of ChromaDB collection to use.
        document_ids: Optional list of document IDs.
        metadata: Optional list of document metadata.
        persist_directory: Directory to persist ChromaDB data.
        docling_options: Options for Docling processing.
        chroma_dependencies: Optional ChromaDBDependencies for the graph.

    Returns:
        A tuple containing the ingestion results, final state, and log entries.
    """
    # Create initial state
    state = DocumentState(
        file_paths=file_paths,
        document_ids=document_ids,
        metadata=metadata,
        chroma_collection_name=collection_name,
    )

    # Set up ChromaDB dependencies if not provided
    if chroma_dependencies is None:
        chroma_dependencies = ChromaDBDependencies(persist_directory=persist_directory)

    # Set up Docling dependencies
    docling_dependencies = DoclingDependencies.create(docling_options=docling_options)

    # Run the graph with Docling processing
    result, final_state, logs = await run_document_ingestion_graph_with_docling(
        state, chroma_dependencies, docling_dependencies
    )

    return result, final_state, logs


async def run_document_ingestion_graph(
    state: DocumentState, dependencies: ChromaDBDependencies
) -> Tuple[Dict[str, Any], DocumentState, List[Any]]:
    """
    Run the document ingestion graph with the provided state and dependencies.

    Args:
        state: The document state containing file paths, documents, and other data.
        dependencies: The ChromaDB dependencies required for ingestion.

    Returns:
        A tuple containing (output, state, history)
    """
    graph = get_document_ingestion_graph()
    
    # Use ChromaDBIngestionNode as the starting node
    try:
        result = await graph.run(start_node=ChromaDBIngestionNode(), state=state, deps=dependencies)
        return result.output, result.state, result.history
    except Exception as e:
        logger.error(f"Error running document ingestion graph: {e}")
        raise GraphError(f"Document ingestion failed: {e}")


async def run_document_ingestion_graph_with_docling(
    state: DocumentState,
    chroma_dependencies: ChromaDBDependencies,
    docling_dependencies: DoclingDependencies,
) -> Tuple[Dict[str, Any], DocumentState, List[Any]]:
    """
    Run the document ingestion graph with Docling processing before ingestion.

    Args:
        state: The document state containing file paths, documents, and other data.
        chroma_dependencies: The ChromaDB dependencies required for ingestion.
        docling_dependencies: The Docling dependencies required for document processing.

    Returns:
        A tuple containing (output, state, history)
    """
    graph = get_document_ingestion_graph_with_docling()
    
    # Combine dependencies to provide access to both ChromaDB and Docling clients
    @dataclass
    class CombinedDependencies:
        docling_processor: Any
        chroma_client: Any
        
    combined_deps = CombinedDependencies(
        docling_processor=docling_dependencies.docling_processor,
        chroma_client=chroma_dependencies.chroma_client
    )
    
    # Use FileTypeRouterNode as the starting node
    try:
        result = await graph.run(start_node=FileTypeRouterNode(), state=state, deps=combined_deps)
        return result.output, result.state, result.history
    except Exception as e:
        logger.error(f"Error running document ingestion graph with Docling: {e}")
        raise GraphError(f"Document ingestion with Docling failed: {e}")


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


def get_document_ingestion_graph_with_docling() -> Graph:
    """
    Create a Graph for document processing with Docling and ingestion into ChromaDB.

    This function creates a Graph that first evaluates file types using FileTypeRouterNode,
    then either processes documents with Docling through DoclingProcessorNode
    or routes text files directly to ChromaDBIngestionNode based on file types.

    Returns:
        A Graph starting with FileTypeRouterNode that connects to either
        DoclingProcessorNode or ChromaDBIngestionNode based on file types.
    """
    # Create the nodes
    router_node = FileTypeRouterNode()
    docling_node = DoclingProcessorNode()
    ingestion_node = ChromaDBIngestionNode()
    
    # Return the graph with the connected nodes
    return Graph(nodes=[router_node, docling_node, ingestion_node])


def visualize_document_processing_graph(output_path: str = "document_processing_graph.txt", direction: str = "LR") -> None:
    """
    Generate and save a visualization of the document processing graph.
    
    This function creates a mermaid diagram showing the flow of documents through
    the processing pipeline, including routing based on file types.
    
    Args:
        output_path: Path where the diagram code will be saved.
        direction: Direction of the graph flow ('TB' for top-bottom, 'LR' for left-right,
                  'RL' for right-left, 'BT' for bottom-top). Default is 'LR'.
    """
    try:
        # Generate mermaid code directly without using the Graph class
        mermaid_code = f"""```mermaid
graph {direction}
    title["Research Agent Document Processing Pipeline"]
    style title fill:#f9f,stroke:#333,stroke-width:2px
    
    FileTypeRouter["File Type Router"] --> DoclingProcessor["Docling Processor"]
    FileTypeRouter --> ChromaDBIngestion["ChromaDB Ingestion"]
    DoclingProcessor --> ChromaDBIngestion
    
    classDef default fill:#f9f,stroke:#333,stroke-width:1px;
```"""
        
        # Save the mermaid code to a file
        with open(output_path, "w") as f:
            f.write(mermaid_code)
        
        logger.info(f"Document processing graph visualization code saved to {output_path}")
        logger.info("Use this code with a Mermaid renderer to view the graph (e.g., at https://mermaid.live)")
    except Exception as e:
        logger.error(f"Failed to generate graph visualization: {e}")


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
    logger = logging.getLogger(__name__)

    # Check if directory exists
    if not os.path.exists(directory_path) or not os.path.isdir(directory_path):
        logger.error(f"Directory '{directory_path}' does not exist or is not a directory")
        return documents

    # Get all files in the directory
    try:
        files = [
            f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))
        ]

        for idx, file_name in enumerate(files):
            file_path = os.path.join(directory_path, file_name)

            # Read the file content
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read()

                # Extract file name and extension
                name_parts = os.path.splitext(file_name)
                base_name = name_parts[0]
                extension = name_parts[1].lstrip('.') if len(name_parts) > 1 else ""
                
                # Create a more unique document ID that includes the file type
                doc_id = f"doc_{idx}_{base_name}_type_{extension}"

                # Create metadata for the document
                file_info = os.stat(file_path)
                metadata = {
                    "filename": file_name,
                    "file_path": file_path,
                    "file_size": file_info.st_size,
                    "created": datetime.datetime.fromtimestamp(file_info.st_ctime).isoformat(),
                    "modified": datetime.datetime.fromtimestamp(file_info.st_mtime).isoformat(),
                    "file_extension": extension,
                    "base_name": base_name,
                    "document_id": doc_id  # Store the document ID in metadata for reference
                }

                # Add document to the list
                documents.append({"content": content, "metadata": metadata, "id": doc_id})

                logger.info(f"Loaded document from '{file_path}' with ID: {doc_id}")

            except Exception as e:
                logger.error(f"Error reading file '{file_path}': {e}")

    except Exception as e:
        logger.error(f"Error listing files in directory '{directory_path}': {e}")

    logger.info("Loaded %d documents from %s", len(documents), directory_path)
    return documents
