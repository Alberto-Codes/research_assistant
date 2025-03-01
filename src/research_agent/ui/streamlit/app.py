"""
Main Streamlit application for the Research Agent.

This module serves as the main entry point for the Streamlit web interface,
providing a multi-page application for different features.
"""

import logging

import streamlit as st

# Import individual UI components
from research_agent.ui.streamlit.document_ingestion import render_document_ingestion_ui
from research_agent.ui.streamlit.gemini_chat import main as render_chat_ui
from research_agent.ui.streamlit.rag_search import render_rag_search_ui

# Set up logging
logger = logging.getLogger(__name__)

# Dictionary of available pages and their render functions
PAGES = {
    "Chat with Gemini": render_chat_ui,
    "Document Ingestion": render_document_ingestion_ui,
    "RAG Search": render_rag_search_ui,
}


def main():
    """Main entry point for the Streamlit application."""
    # Set up the page configuration
    st.set_page_config(
        page_title="Research Agent",
        page_icon="🧠",
        layout="centered",
        initial_sidebar_state="expanded",
    )

    # Add a title
    st.title("Research Agent")

    # Add a sidebar for navigation
    with st.sidebar:
        st.title("Navigation")

        # Radio buttons for page selection
        page = st.radio("Select a page:", list(PAGES.keys()))

        # About section at the bottom of the sidebar
        st.markdown("---")
        st.header("About")
        st.markdown(
            """
            Research Agent is a tool for AI-assisted research and document management.
            
            This application is built with:
            - Pydantic Graph for workflows
            - Google Vertex AI and Gemini for LLM capabilities
            - ChromaDB for document storage and retrieval
            """
        )

    # Render the selected page
    PAGES[page]()


if __name__ == "__main__":
    main()
