"""
ChromaDB dependencies for the document ingestion graph in the Research Agent.

This module defines the ChromaDB dependencies that can be injected into nodes,
including the ChromaDBClient protocol and its implementation.
"""

import logging
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Protocol

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

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
            documents: List of document content strings to add.
            document_ids: Optional list of IDs for the documents.
            metadata: Optional list of metadata for the documents.

        Returns:
            A dictionary containing information about the operation.
        """
        ...

    def query(
        self,
        collection_name: str,
        query_texts: List[str],
        n_results: int = 10,
    ) -> Dict[str, Any]:
        """Query a ChromaDB collection.

        Args:
            collection_name: The name of the collection to query.
            query_texts: List of query text strings.
            n_results: Maximum number of results to return per query.

        Returns:
            A dictionary containing the query results.
        """
        ...


class DefaultChromaDBClient:
    """Default implementation of the ChromaDBClient protocol.

    This class provides a concrete implementation of the ChromaDBClient
    protocol using the actual ChromaDB library.
    """

    def __init__(
        self,
        persist_directory: str = "./chroma_db",
        host: Optional[str] = None,
        port: Optional[int] = None,
    ) -> None:
        """Initialize the ChromaDB client.

        Args:
            persist_directory: Directory where ChromaDB data will be persisted.
                Used only if host is None.
            host: Optional host address for a ChromaDB server.
                If provided, a remote client will be created.
            port: Optional port for a ChromaDB server.
                Used only if host is provided.
        """
        self.persist_directory = persist_directory
        self.host = host
        self.port = port
        self.client = None
        self.embedding_function = None

        # Create the persist directory if it doesn't exist
        if host is None and not os.path.exists(persist_directory):
            os.makedirs(persist_directory)
            logger.info(f"Created persist directory: {persist_directory}")

        # Log the configuration
        if host is not None:
            logger.info(f"Initializing ChromaDB client with host={host}, port={port}")
        else:
            logger.info(f"Initializing ChromaDB client with persist_directory={persist_directory}")

        # Initialize the client and embedding function
        self._initialize_client()
        self._initialize_embedding_function()

    def _initialize_client(self) -> None:
        """Initialize the ChromaDB client based on configuration.

        This method creates either a persistent local client or a remote
        client based on the host parameter.
        """
        try:
            if self.host is not None:
                # Create a remote client
                self.client = chromadb.HttpClient(host=self.host, port=self.port)
                logger.info(f"Connected to ChromaDB server at {self.host}:{self.port}")
            else:
                # Create a persistent local client with settings from original implementation
                self.client = chromadb.PersistentClient(
                    path=self.persist_directory,
                    settings=Settings(allow_reset=True, anonymized_telemetry=False),
                )
                logger.info(f"Created persistent ChromaDB client at {self.persist_directory}")
        except Exception as e:
            logger.error(f"Error initializing ChromaDB client: {str(e)}")
            raise

    def _initialize_embedding_function(self) -> None:
        """Initialize the embedding function for ChromaDB.

        This method sets up the default embedding function to convert
        text to vector embeddings.
        """
        try:
            # Use the default embedding function
            self.embedding_function = embedding_functions.DefaultEmbeddingFunction()
            logger.info("Initialized default embedding function")
        except Exception as e:
            logger.error(f"Error initializing embedding function: {str(e)}")
            raise

    def get_or_create_collection(self, collection_name: str) -> Any:
        """Get or create a collection in ChromaDB.

        Args:
            collection_name: The name of the collection to get or create.

        Returns:
            The ChromaDB collection object.
        """
        try:
            # Get or create the collection with the embedding function
            collection = self.client.get_or_create_collection(
                name=collection_name,
                embedding_function=self.embedding_function,
            )
            logger.info(f"Using collection: {collection_name}")
            return collection
        except Exception as e:
            logger.error(f"Error getting/creating collection '{collection_name}': {str(e)}")
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
            documents: List of document content strings to add.
            document_ids: Optional list of IDs for the documents.
            metadata: Optional list of metadata for the documents.

        Returns:
            A dictionary containing information about the operation.
        """
        try:
            # Get or create the collection
            collection = self.get_or_create_collection(collection_name)

            # Generate IDs if not provided
            if document_ids is None:
                import uuid

                document_ids = [str(uuid.uuid4()) for _ in range(len(documents))]

            # Create empty metadata if not provided
            if metadata is None:
                metadata = [{"source": "unknown"} for _ in range(len(documents))]

            # Ensure we have the same number of IDs, documents, and metadata
            if len(document_ids) != len(documents) or len(metadata) != len(documents):
                error_msg = (
                    f"Mismatch in lengths: documents={len(documents)}, "
                    f"ids={len(document_ids)}, metadata={len(metadata)}"
                )
                logger.error(error_msg)
                return {"error": error_msg}

            # Add the documents to the collection
            collection.add(
                documents=documents,
                ids=document_ids,
                metadatas=metadata,
            )

            logger.info(f"Added {len(documents)} documents to collection '{collection_name}'")

            # Return a success message
            return {
                "success": True,
                "count": len(documents),
                "collection": collection_name,
                "ids": document_ids,
            }

        except Exception as e:
            error_msg = f"Error adding documents to collection '{collection_name}': {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}

    def query(
        self,
        collection_name: str,
        query_texts: List[str],
        n_results: int = 10,
    ) -> Dict[str, Any]:
        """Query a ChromaDB collection.

        Args:
            collection_name: The name of the collection to query.
            query_texts: List of query text strings.
            n_results: Maximum number of results to return per query.

        Returns:
            A dictionary containing the query results.
        """
        try:
            # Get the collection
            collection = self.get_or_create_collection(collection_name)

            # Query the collection
            results = collection.query(
                query_texts=query_texts,
                n_results=n_results,
            )

            logger.info(f"Queried collection '{collection_name}' with {len(query_texts)} queries")

            return results

        except Exception as e:
            error_msg = f"Error querying collection '{collection_name}': {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}


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
