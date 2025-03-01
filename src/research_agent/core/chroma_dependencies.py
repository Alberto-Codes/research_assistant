"""
ChromaDB dependencies for the Research Agent graph.

This module defines the ChromaDB dependencies that can be injected into nodes,
including the ChromaDBClient protocol and its implementation.
"""

import logging
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Protocol

import chromadb
from chromadb.config import Settings

# Module-specific logger
logger = logging.getLogger(__name__)


class ChromaDBClient(Protocol):
    """Protocol defining the interface for a ChromaDB client.

    This protocol ensures that any ChromaDB client implementation provides
    the necessary methods to interact with ChromaDB.
    """

    def get_or_create_collection(self, collection_name: str) -> Any:
        """Get or create a collection in ChromaDB.

        Args:
            collection_name: The name of the collection to get or create.

        Returns:
            The ChromaDB collection object.
        """
        ...

    def add_documents(
        self,
        collection_name: str,
        documents: List[str],
        document_ids: Optional[List[str]] = None,
        metadata: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Add documents to a ChromaDB collection.

        Args:
            collection_name: The name of the collection to add documents to.
            documents: The list of document texts to add.
            document_ids: Optional list of document IDs.
            metadata: Optional list of metadata dictionaries.

        Returns:
            A dictionary with information about the add operation.
        """
        ...

    def query(
        self,
        collection_name: str,
        query_texts: List[str],
        n_results: int = 10,
    ) -> Dict[str, Any]:
        """Query documents from a ChromaDB collection.

        Args:
            collection_name: The name of the collection to query from.
            query_texts: The list of query texts.
            n_results: The number of results to return.

        Returns:
            A dictionary with query results.
        """
        ...


class DefaultChromaDBClient:
    """A client for ChromaDB.

    This implementation uses the standard ChromaDB client to interact with
    a local or remote ChromaDB instance.

    Attributes:
        client: The ChromaDB client instance.
        persist_directory: The directory where ChromaDB data is persisted.
    """

    def __init__(
        self,
        persist_directory: str = "./chroma_db",
        host: Optional[str] = None,
        port: Optional[int] = None,
    ) -> None:
        """Initialize the ChromaDB client.

        Args:
            persist_directory: The directory where ChromaDB data should be persisted.
            host: Optional host for a remote ChromaDB server.
            port: Optional port for a remote ChromaDB server.

        Raises:
            Exception: If there is an error initializing the client.
        """
        try:
            self.persist_directory = persist_directory

            # Create the persist directory if it doesn't exist
            os.makedirs(persist_directory, exist_ok=True)

            # Use HTTP client if host and port are provided, otherwise use local
            if host and port:
                self.client = chromadb.HttpClient(host=host, port=port)
                logger.info(f"Initialized ChromaDB HTTP client to {host}:{port}")
            else:
                self.client = chromadb.PersistentClient(
                    path=persist_directory,
                    settings=Settings(allow_reset=True, anonymized_telemetry=False),
                )
                logger.info(f"Initialized ChromaDB persistent client at {persist_directory}")

        except Exception as e:
            logger.error(f"Error initializing ChromaDB client: {e}")
            raise

    def get_or_create_collection(self, collection_name: str) -> Any:
        """Get or create a collection in ChromaDB.

        Args:
            collection_name: The name of the collection to get or create.

        Returns:
            The ChromaDB collection object.
        """
        try:
            collection = self.client.get_or_create_collection(
                name=collection_name, embedding_function=None  # Use the default embedding function
            )
            return collection
        except Exception as e:
            logger.error(f"Error getting/creating collection '{collection_name}': {e}")
            raise

    def add_documents(
        self,
        collection_name: str,
        documents: List[str],
        document_ids: Optional[List[str]] = None,
        metadata: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Add documents to a ChromaDB collection.

        Args:
            collection_name: The name of the collection to add documents to.
            documents: The list of document texts to add.
            document_ids: Optional list of document IDs.
            metadata: Optional list of metadata dictionaries.

        Returns:
            A dictionary with information about the add operation.
        """
        try:
            collection = self.get_or_create_collection(collection_name)

            # If document_ids not provided, create them
            if document_ids is None:
                document_ids = [f"doc_{i}" for i in range(len(documents))]

            # If metadata not provided, create empty metadata
            if metadata is None:
                metadata = [{} for _ in range(len(documents))]

            # Ensure lengths match
            if len(document_ids) != len(documents) or len(metadata) != len(documents):
                raise ValueError("Documents, IDs, and metadata must have the same length")

            # Add the documents
            result = collection.add(documents=documents, ids=document_ids, metadatas=metadata)

            return {
                "collection": collection_name,
                "count": len(documents),
                "ids": document_ids,
                "result": result,
            }

        except Exception as e:
            logger.error(f"Error adding documents to collection '{collection_name}': {e}")
            raise

    def query(
        self,
        collection_name: str,
        query_texts: List[str],
        n_results: int = 10,
    ) -> Dict[str, Any]:
        """Query documents from a ChromaDB collection.

        Args:
            collection_name: The name of the collection to query from.
            query_texts: The list of query texts.
            n_results: The number of results to return.

        Returns:
            A dictionary with query results.
        """
        try:
            collection = self.get_or_create_collection(collection_name)

            results = collection.query(query_texts=query_texts, n_results=n_results)

            return results

        except Exception as e:
            logger.error(f"Error querying collection '{collection_name}': {e}")
            raise


@dataclass
class ChromaDBDependencies:
    """Container for all ChromaDB dependencies needed by the document ingestion graph nodes.

    This class centralizes all ChromaDB dependencies required by the graph,
    making it easier to provide different implementations for testing,
    development, or production environments.

    Attributes:
        chroma_client: The ChromaDB client to use for document operations.
        persist_directory: The directory where ChromaDB data should be persisted.
    """

    persist_directory: str = "./chroma_db"
    chroma_client: Optional[ChromaDBClient] = None

    def __post_init__(self) -> None:
        """Initialize default dependencies if not provided.

        This method is automatically called after initialization to
        set up default dependencies based on the configuration.
        """
        if self.chroma_client is None:
            self.chroma_client = DefaultChromaDBClient(persist_directory=self.persist_directory)
