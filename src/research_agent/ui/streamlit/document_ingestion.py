"""
Document ingestion component for the Streamlit interface.

This module provides a Streamlit component for ingesting documents into ChromaDB.
"""

import asyncio
import datetime
import logging
import os
import tempfile
from typing import Any, Dict, List, Optional

import streamlit as st

from research_agent.api.services import ingest_documents_from_directory

# Set up logging
logger = logging.getLogger(__name__)


async def ingest_uploaded_files(
    uploaded_files: List[Any],
    collection_name: str,
    persist_directory: str = "./chroma_db",
) -> Dict[str, Any]:
    """
    Save uploaded files to a temporary directory and ingest them into ChromaDB.

    Args:
        uploaded_files: List of uploaded files from Streamlit.
        collection_name: Name of the ChromaDB collection to use.
        persist_directory: Directory where ChromaDB data should be persisted.

    Returns:
        A dictionary with ingestion results.
    """
    # Create a temporary directory to store uploaded files
    with tempfile.TemporaryDirectory() as temp_dir:
        # Save uploaded files to the temporary directory
        for uploaded_file in uploaded_files:
            file_path = os.path.join(temp_dir, uploaded_file.name)

            with open(file_path, "wb") as f:
                f.write(uploaded_file.getvalue())

            logger.info(f"Saved uploaded file to {file_path}")

        # Ingest documents from the temporary directory
        result = await ingest_documents_from_directory(
            directory_path=temp_dir,
            collection_name=collection_name,
            persist_directory=persist_directory,
        )

        return result


def render_document_ingestion_ui():
    """
    Render the document ingestion UI component.

    This function provides a Streamlit UI for ingesting documents into ChromaDB.
    """
    st.header("Document Ingestion")
    st.markdown(
        """
        Upload documents to be ingested into ChromaDB for later retrieval and searching.
        
        Supported file types: text (.txt), Markdown (.md), CSV (.csv), JSON (.json), etc.
        """
    )

    # File uploader
    uploaded_files = st.file_uploader(
        "Upload documents",
        accept_multiple_files=True,
        type=["txt", "md", "csv", "json", "pdf", "docx"],
        help="Select files to upload and ingest into ChromaDB",
    )

    # Collection name input
    collection_name = st.text_input(
        "Collection Name",
        value="default_collection",
        help="Name of the ChromaDB collection to store documents in",
    )

    # ChromaDB directory input
    chroma_dir = st.text_input(
        "ChromaDB Directory",
        value="./chroma_db",
        help="Directory where ChromaDB data should be stored",
    )

    # Submit button
    if st.button("Ingest Documents", disabled=not uploaded_files):
        if not uploaded_files:
            st.warning("Please upload at least one document.")
            return

        # Show a spinner while ingesting documents
        with st.spinner("Ingesting documents..."):
            # Create the directory if it doesn't exist
            os.makedirs(chroma_dir, exist_ok=True)

            # Call the ingest function
            try:
                # Use asyncio to run the async function
                result = asyncio.run(
                    ingest_uploaded_files(
                        uploaded_files=uploaded_files,
                        collection_name=collection_name,
                        persist_directory=chroma_dir,
                    )
                )

                # Display the results
                if result.get("success", False):
                    st.success(
                        f"Successfully ingested {result['state']['documents_count']} documents."
                    )

                    # Display ingested documents
                    with st.expander("Ingestion Details", expanded=True):
                        st.write(f"Collection: {result['state']['collection_name']}")
                        st.write(f"Documents: {result['state']['documents_count']}")
                        st.write(f"ChromaDB Directory: {os.path.abspath(chroma_dir)}")
                        st.write(f"Ingestion Time: {result['state']['total_time']:.3f} seconds")

                        # Display each document
                        if "result" in result and isinstance(result["result"], dict):
                            st.subheader("Ingested Documents")
                            for i, doc_id in enumerate(result["result"].get("ids", [])):
                                st.write(f"{i+1}. {doc_id}")
                else:
                    st.error("Failed to ingest documents.")
                    if "errors" in result and result["errors"]:
                        for error in result["errors"]:
                            st.error(f"Error: {error}")

            except Exception as e:
                st.error(f"An error occurred during document ingestion: {str(e)}")
                logger.exception("Error in document ingestion")


if __name__ == "__main__":
    # Set up basic Streamlit configuration
    st.set_page_config(
        page_title="Research Agent - Document Ingestion",
        page_icon="📄",
        layout="centered",
    )

    # Render the UI
    render_document_ingestion_ui()
