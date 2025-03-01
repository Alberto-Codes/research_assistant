"""
State definition for document ingestion in the Research Agent.

This module defines the state class used to store document data as it flows
through the nodes in the document ingestion graph for ChromaDB.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class DocumentState:
    """
    State class for storing documents and their metadata for ChromaDB ingestion.

    Attributes:
        documents: List of document content strings to be ingested.
        document_ids: Optional list of IDs for the documents (will be auto-generated if not provided).
        metadata: Optional list of metadata dictionaries for the documents.
        chroma_collection_name: Name of the ChromaDB collection to use.
        embedding_results: Results from the embedding process.
        ingestion_results: Results from the ingestion process.
        node_execution_history: History of node executions with their outputs.
        total_time: Total time taken for the graph execution.
    """

    documents: List[str] = field(default_factory=list)
    document_ids: Optional[List[str]] = None
    metadata: Optional[List[Dict[str, Any]]] = None
    chroma_collection_name: str = "default_collection"
    embedding_results: Optional[Dict[str, Any]] = None
    ingestion_results: Optional[Dict[str, Any]] = None
    node_execution_history: List[str] = field(default_factory=list)
    total_time: float = 0.0

    def __repr__(self) -> str:
        """Provide a nice string representation of the state."""
        return (
            f"DocumentState("
            f"documents=[{len(self.documents)} docs], "
            f"collection='{self.chroma_collection_name}', "
            f"total_time={self.total_time:.3f}s)"
        ) 