"""
RAG (Retrieval Augmented Generation) search interface for the Research Agent.

This module provides a Streamlit interface for searching documents using RAG.
"""

import asyncio
import logging
import time
from typing import Dict, Any, List, Optional

import chromadb
import streamlit as st
from pydantic_ai import Agent
from pydantic_ai.models.vertexai import VertexAIModel

from research_agent.core.rag import run_rag_query

# Set up logging
logger = logging.getLogger(__name__)


async def execute_rag_query(
    query: str,
    collection_name: str,
    chroma_dir: str = "./chroma_db",
    project_id: Optional[str] = None,
    model_name: str = "gemini-1.5-pro",
    region: str = "us-central1",
) -> Dict[str, Any]:
    """
    Execute a RAG query using the specified parameters.

    Args:
        query: The query to execute
        collection_name: The name of the ChromaDB collection to query
        chroma_dir: The directory containing the ChromaDB database
        project_id: Optional Google Cloud project ID
        model_name: The name of the Gemini model to use
        region: The Google Cloud region to use

    Returns:
        A dictionary containing the query results
    """
    logger.info(f"Executing RAG query: '{query}'")

    try:
        # Initialize ChromaDB
        logger.info(f"Connecting to ChromaDB at {chroma_dir}")
        chroma_client = chromadb.PersistentClient(path=chroma_dir)

        # Get the collection
        collection = chroma_client.get_collection(collection_name)
        logger.info(f"Found collection '{collection_name}' with {collection.count()} documents")

        # Initialize Gemini model
        logger.info(f"Initializing Gemini model {model_name}")
        gemini_model = VertexAIModel(model_name=model_name, project_id=project_id, region=region)

        # Create a PydanticAI Agent to use the VertexAIModel
        logger.info("Creating Agent with VertexAIModel")
        agent = Agent(gemini_model)

        # Run the RAG query
        logger.info(f"Running RAG query: '{query}'")
        result = await run_rag_query(
            query=query, 
            chroma_collection=collection, 
            gemini_model=agent, 
            project_id=project_id
        )

        logger.info("Successfully completed RAG query")
        return result

    except Exception as e:
        logger.error(f"Error executing RAG query: {e}", exc_info=True)
        return {
            "answer": f"Error: {str(e)}",
            "retrieval_time": 0,
            "generation_time": 0,
            "total_time": 0,
        }


def list_collections(chroma_dir: str = "./chroma_db") -> List[str]:
    """
    List all collections in the ChromaDB database.

    Args:
        chroma_dir: The directory containing the ChromaDB database

    Returns:
        A list of collection names
    """
    try:
        chroma_client = chromadb.PersistentClient(path=chroma_dir)
        # In ChromaDB v0.6.0, list_collections() returns collection names directly
        collections = chroma_client.list_collections()
        # No need to access .name attribute as collections are already strings
        return collections
    except Exception as e:
        logger.error(f"Error listing collections: {e}", exc_info=True)
        return []


def render_rag_search_ui():
    """Render the RAG search UI."""
    st.title("Document Search with RAG")
    st.write(
        """
        Search your documents using RAG (Retrieval Augmented Generation).
        This uses ChromaDB for document retrieval and Gemini for answer generation.
        """
    )

    # Sidebar configuration
    with st.sidebar:
        st.header("Configuration")
        
        # Collection selection
        chroma_dir = st.text_input("ChromaDB Directory", value="./chroma_db")
        collections = list_collections(chroma_dir)
        
        if collections:
            collection_name = st.selectbox(
                "Collection", 
                options=collections,
                index=0 if "my_docs" not in collections else collections.index("my_docs")
            )
            collection_info = f"Selected collection: {collection_name}"
        else:
            collection_name = st.text_input("Collection Name", value="my_docs")
            collection_info = "No collections found. Please ingest documents first."
        
        st.info(collection_info)
        
        # Advanced settings collapsible section
        with st.expander("Advanced Settings"):
            project_id = st.text_input("Google Cloud Project ID (optional)")
            model_name = st.selectbox(
                "Model", 
                options=["gemini-1.5-pro", "gemini-1.5-flash", "gemini-1.0-pro"],
                index=0
            )
            region = st.text_input("Region", value="us-central1")

    # Main query area
    query = st.text_area("Enter your question about the documents:", height=100)
    
    # Only show search button if query is not empty
    if query:
        if st.button("Search Documents", type="primary"):
            with st.spinner("Searching documents and generating answer..."):
                # Start timer
                start_time = time.time()
                
                # Run the RAG query
                result = asyncio.run(execute_rag_query(
                    query=query,
                    collection_name=collection_name,
                    chroma_dir=chroma_dir,
                    project_id=project_id if project_id else None,
                    model_name=model_name,
                    region=region
                ))
                
                # End timer
                end_time = time.time()
                total_time = end_time - start_time
                
                # Display results
                st.markdown("### Answer")
                st.markdown(result["answer"])
                
                # Show execution metrics
                st.subheader("Performance Metrics")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Retrieval Time", f"{result.get('retrieval_time', 0):.2f}s")
                with col2:
                    st.metric("Generation Time", f"{result.get('generation_time', 0):.2f}s")
                with col3:
                    st.metric("Total Time", f"{result.get('total_time', total_time):.2f}s")
    else:
        st.info("Enter a question above to search your documents.")
        
    # Help section
    with st.expander("Help & Tips"):
        st.markdown("""
        ### How to use RAG Search
        
        1. Make sure you have ingested documents using the Document Ingestion page
        2. Select the collection containing your documents
        3. Enter a specific question about the content of your documents
        4. Click the Search button to find relevant information
        
        ### Tips for Better Results
        
        - Ask specific questions rather than open-ended ones
        - If you don't get good results, try rephrasing your question
        - Check that your documents have been properly ingested
        - For large document collections, be more specific in your queries
        """)


if __name__ == "__main__":
    render_rag_search_ui() 