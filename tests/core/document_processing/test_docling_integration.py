"""
Integration tests for the DoclingProcessor.

These tests use mocks to simulate the Docling library's behavior since the actual library
might not be available in all environments.
"""

import os
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from research_agent.core.document_processing.docling_processor import DoclingProcessor, DoclingProcessorOptions


@pytest.fixture
def test_data_dir():
    """Fixture to get the path to the test data directory."""
    # Start from the current file's directory
    current_dir = Path(__file__).parent
    
    # Navigate up to the tests directory
    tests_dir = current_dir.parent.parent
    
    # Check if test_data exists
    test_data_dir = tests_dir / "test_data"
    if not test_data_dir.exists() or not test_data_dir.is_dir():
        pytest.skip("Test data directory not found")
    
    return test_data_dir


@pytest.fixture
def mock_docling_processor(monkeypatch):
    """Fixture to create a mock DoclingProcessor with simulated functionality."""
    # Create mock document for text processing
    mock_document = MagicMock()
    mock_document.document_type = "text"
    mock_document.export_to_text.return_value = """
    Sample Document for Docling Testing
    
    This is a simple text file that we can use to test the Docling processor.
    
    # Section 1: Introduction
    
    Docling is a document processing library that can handle various document formats.
    
    # Section 2: Features
    
    The main features of Docling include several capabilities.
    
    # Section 3: Testing
    
    This document is being used to test the DoclingProcessor implementation.
    """
    
    # Set up result mock
    mock_result = MagicMock()
    mock_result.document = mock_document
    
    # Create converter mock
    mock_converter = MagicMock()
    mock_converter.convert.return_value = mock_result
    
    # Create DocumentConverter and PipelineOptions mocks
    mock_document_converter_class = MagicMock()
    mock_document_converter_class.return_value = mock_converter
    
    mock_pipeline_options_class = MagicMock()
    
    # Patch _init_docling directly with monkeypatch
    def mocked_init_docling(self):
        self.docling_available = True
        self.DocumentConverter = mock_document_converter_class
        self.PipelineOptions = mock_pipeline_options_class
        self.converter = mock_converter
    
    monkeypatch.setattr(DoclingProcessor, "_init_docling", mocked_init_docling)
    
    # Return processor with mocked internals
    return DoclingProcessor()


def test_processor_initialization(mock_docling_processor):
    """Test that the processor initializes correctly with Docling."""
    assert mock_docling_processor.docling_available is True
    assert mock_docling_processor.converter is not None
    assert mock_docling_processor.PipelineOptions is not None


def test_process_text_file(mock_docling_processor, test_data_dir, monkeypatch):
    """Test processing a simple text file."""
    sample_txt = test_data_dir / "sample.txt"
    if not sample_txt.exists():
        pytest.skip(f"Sample text file not found at {sample_txt}")
    
    # Ensure the path.exists returns True for our test
    monkeypatch.setattr(Path, "exists", lambda _: True)
    
    # Process the file
    document = mock_docling_processor.process_file(str(sample_txt))
    
    # Basic verification
    assert document is not None
    assert hasattr(document, 'document_type')
    assert document.document_type == "text"
    
    # Verify content (using our mocked content)
    text_content = document.export_to_text()
    assert "Sample Document for Docling Testing" in text_content
    assert "Section 1: Introduction" in text_content
    assert "Section 2: Features" in text_content
    assert "Section 3: Testing" in text_content


def test_process_directory(mock_docling_processor, test_data_dir, monkeypatch):
    """Test processing a directory with multiple files."""
    # Create mock file paths
    class MockPath:
        def __init__(self, name):
            self.name = name
        
        def __str__(self):
            return self.name
        
        def is_file(self):
            return True
        
        @property
        def suffix(self):
            return "." + self.name.split(".")[-1]
    
    # Create test files
    test_files = [
        MockPath("sample.txt"),
        MockPath("mock_doc.pdf"),
    ]
    
    # Mock required methods
    monkeypatch.setattr(Path, "exists", lambda _: True)
    monkeypatch.setattr(Path, "is_dir", lambda _: True)
    monkeypatch.setattr(Path, "glob", lambda *args, **kwargs: test_files)
    
    # Process the directory
    results = mock_docling_processor.process_directory(str(test_data_dir))
    
    # Verify results
    assert results is not None
    assert isinstance(results, list)
    assert len(results) == 2  # Should process both mock files
    
    # Check that the document objects are valid
    for _, document in results:
        assert document is not None
        assert hasattr(document, 'document_type')


if __name__ == "__main__":
    pytest.main(["-v", __file__]) 