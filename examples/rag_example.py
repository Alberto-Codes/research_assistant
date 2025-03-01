"""
Retrieval Augmented Generation (RAG) Example with Pydantic AI

This example demonstrates how to build a simple RAG system using Pydantic AI.
It creates a tool that can search through documents and uses it to answer questions.

Requirements:
- pydantic-ai
- openai
- chromadb
"""

from __future__ import annotations

import json
import os
import uuid
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field
from pydantic_ai.agent import Agent
from pydantic_ai.result import get_content

# ------------------ Data Structures ------------------


class Document(BaseModel):
    """A document with content and metadata."""

    id: str
    content: str
    title: Optional[str] = None
    url: Optional[str] = None

    def __str__(self) -> str:
        return f"{self.title or 'Document'}: {self.content[:100]}..."


class ChromaDocumentStore:
    """Document store that uses ChromaDB for vector search."""

    def __init__(
        self, collection_name: str = "rag_documents", persist_directory: Optional[str] = None
    ):
        """Initialize a ChromaDB document store.

        Args:
            collection_name: Name of the ChromaDB collection.
            persist_directory: Directory to persist ChromaDB data. If None, data is stored in memory.
        """
        import chromadb

        # Initialize ChromaDB client
        self.client = chromadb.Client(
            chromadb.Settings(
                persist_directory=persist_directory,
                chroma_db_impl="duckdb+parquet",  # Use DuckDB in-memory if persist_directory is None
            )
        )

        # Get or create collection
        self.collection_name = collection_name
        try:
            self.collection = self.client.get_collection(collection_name)
            print(f"Using existing collection: {collection_name}")
        except ValueError:
            self.collection = self.client.create_collection(
                name=collection_name, metadata={"hnsw:space": "cosine"}  # Use cosine similarity
            )
            print(f"Created new collection: {collection_name}")

        self.document_map: Dict[str, Document] = {}

    def add_documents(self, documents: List[Document], embeddings_model: Optional[str] = None):
        """Add documents to the ChromaDB store.

        Args:
            documents: List of documents to add.
            embeddings_model: OpenAI model to use for embeddings. If None, you must provide
                embeddings separately or ChromaDB will use its own embedding function.
        """
        # Keep a mapping of ChromaDB IDs to original documents
        for doc in documents:
            self.document_map[doc.id] = doc

        # Prepare data for ChromaDB
        ids = [doc.id for doc in documents]
        texts = [doc.content for doc in documents]
        metadatas = [
            {
                "title": doc.title or "",
                "url": doc.url or "",
                "content": doc.content,  # Include content in metadata for retrieval
            }
            for doc in documents
        ]

        # Add documents to ChromaDB collection
        self.collection.add(
            ids=ids,
            documents=texts,
            metadatas=metadatas,
        )

        print(f"Added {len(documents)} documents to ChromaDB collection")

    def search(self, query_text: str, top_k: int = 3) -> List[tuple[Document, float]]:
        """Search for documents similar to the query text.

        Args:
            query_text: Text query to search for.
            top_k: Number of top results to return.

        Returns:
            List of (document, score) tuples.
        """
        # Query the collection
        results = self.collection.query(
            query_texts=[query_text],
            n_results=top_k,
            include=["metadatas", "distances", "documents"],
        )

        # Process results
        documents_results = []
        if results["ids"] and len(results["ids"][0]) > 0:
            for i, doc_id in enumerate(results["ids"][0]):
                # Get the original document from our mapping
                if doc_id in self.document_map:
                    doc = self.document_map[doc_id]
                else:
                    # If not in mapping, create a new document from metadata
                    metadata = results["metadatas"][0][i]
                    doc = Document(
                        id=doc_id,
                        content=metadata.get("content", results["documents"][0][i]),
                        title=metadata.get("title", ""),
                        url=metadata.get("url", ""),
                    )
                    # Update our mapping
                    self.document_map[doc_id] = doc

                # Get the distance/similarity score
                distance = results["distances"][0][i] if "distances" in results else 0.0

                # Add to results
                documents_results.append((doc, distance))

        return documents_results


# ------------------ RAG Tool ------------------


class RetrieveDocsInput(BaseModel):
    """Input for the document retrieval tool."""

    query: str = Field(..., description="The search query to find relevant documents")


class RetrieveDocsOutput(BaseModel):
    """Output from the document retrieval tool."""

    documents: List[Document] = Field(..., description="List of retrieved documents")


class RAGAgent:
    """Agent with RAG capabilities."""

    def __init__(self, document_store: ChromaDocumentStore, openai_api_key: Optional[str] = None):
        if openai_api_key:
            os.environ["OPENAI_API_KEY"] = openai_api_key

        self.document_store = document_store
        self.openai_client = self._create_openai_client()
        self.agent = self._create_agent()

    def _create_openai_client(self):
        from openai import OpenAI

        return OpenAI()

    def _create_agent(self):
        """Create the RAG agent with search capabilities."""

        async def retrieve_docs(input_data: RetrieveDocsInput) -> RetrieveDocsOutput:
            """Retrieve documents relevant to the query."""
            # Search documents directly using the query text
            results = self.document_store.search(input_data.query, top_k=3)

            # Return results
            return RetrieveDocsOutput(documents=[doc for doc, _ in results])

        # Create the agent with the document retrieval tool
        agent = Agent(
            tools=[retrieve_docs],
            system_prompt="""
            You are a helpful research assistant.
            
            When answering questions, follow these steps:
            1. Use the retrieve_docs tool to find relevant documents based on the user's query
            2. Review the retrieved documents to find information relevant to the query
            3. Answer the question using information from the documents, citing your sources
            4. If you cannot find relevant information, acknowledge that you don't know
            
            Always be truthful and helpful.
            """,
            model="gpt-4o",  # You can change this to any supported model
        )

        return agent

    async def answer_question(self, question: str):
        """Answer a question using RAG."""
        result = await self.agent.achat(question)
        return get_content(result)


# ------------------ Example Usage ------------------


async def main():
    """Run a simple RAG example."""

    # Sample documents (in a real system, you'd load these from files/database)
    sample_docs = [
        Document(
            id=str(uuid.uuid4()),
            title="Python Basics",
            content="Python is a high-level, interpreted programming language known for its readability and simplicity.",
        ),
        Document(
            id=str(uuid.uuid4()),
            title="Machine Learning",
            content="Machine learning is a subset of artificial intelligence focused on building systems that learn from data.",
        ),
        Document(
            id=str(uuid.uuid4()),
            title="Neural Networks",
            content="Neural networks are computing systems inspired by biological neural networks in animal brains.",
        ),
        Document(
            id=str(uuid.uuid4()),
            title="Natural Language Processing",
            content="NLP combines linguistics and AI to enable computers to understand, interpret, and generate human language.",
        ),
        Document(
            id=str(uuid.uuid4()),
            title="Retrieval Augmented Generation",
            content="RAG combines retrieval-based and generation-based approaches to enhance language model outputs with facts from external sources.",
        ),
    ]

    # Create document store with ChromaDB
    document_store = ChromaDocumentStore(collection_name="rag_example")

    # Add documents to the store
    document_store.add_documents(sample_docs)

    # Create RAG agent
    rag_agent = RAGAgent(document_store)

    # Example questions
    questions = [
        "What is Python?",
        "How are neural networks related to machine learning?",
        "What is retrieval augmented generation?",
    ]

    # Answer questions
    for question in questions:
        print(f"\nQuestion: {question}")
        answer = await rag_agent.answer_question(question)
        print(f"Answer: {answer}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
