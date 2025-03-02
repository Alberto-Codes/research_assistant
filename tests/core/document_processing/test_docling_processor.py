"""
Tests for the DoclingProcessor module.
"""

import os
import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path

from research_agent.core.document_processing.docling_processor import DoclingProcessor, DoclingProcessorOptions


def test_options_default_values():
    """Test that default values are set correctly."""
    options = DoclingProcessorOptions()
    assert options.enable_ocr is True
    assert options.extract_tables is True
    assert options.extract_images is True
    assert options.language is None
    assert options.chunk_size == 1000
    assert options.chunk_overlap == 200


def test_options_custom_values():
    """Test that custom values are set correctly."""
    options = DoclingProcessorOptions(
        enable_ocr=False,
        extract_tables=False,
        extract_images=False,
        language="en",
        chunk_size=500,
        chunk_overlap=100
    )
    assert options.enable_ocr is False
    assert options.extract_tables is False
    assert options.extract_images is False
    assert options.language == "en"
    assert options.chunk_size == 500
    assert options.chunk_overlap == 100


def test_initialization():
    """Test basic initialization."""
    processor = DoclingProcessor()
    assert processor.options is not None
    assert isinstance(processor.options, DoclingProcessorOptions)


def test_initialization_with_options():
    """Test initialization with custom options."""
    options = DoclingProcessorOptions(language="en", chunk_size=500)
    processor = DoclingProcessor(options)
    assert processor.options == options


def test_docling_available(monkeypatch):
    """Test when Docling is available"""
    def mock_init_docling(instance):
        instance.docling_available = True
        instance.DocumentConverter = MagicMock()
        instance.PipelineOptions = MagicMock()
        instance.converter = MagicMock()
    
    monkeypatch.setattr(DoclingProcessor, "_init_docling", mock_init_docling)
    
    processor = DoclingProcessor()
    
    # Verify docling is available and the attributes are set
    assert processor.docling_available is True
    assert processor.converter is not None
    assert processor.DocumentConverter is not None
    assert processor.PipelineOptions is not None


def test_docling_not_available(monkeypatch):
    """Test the behavior when Docling is not available"""
    def mock_init_docling(instance):
        instance.docling_available = False
        instance.DocumentConverter = None
        instance.PipelineOptions = None
        instance.converter = None
    
    monkeypatch.setattr(DoclingProcessor, "_init_docling", mock_init_docling)
    
    processor = DoclingProcessor()
    
    # Verify docling is not available
    assert processor.docling_available is False
    assert processor.converter is None
    
    # Verify that attempting to process files raises the expected exception
    with pytest.raises(ValueError, match="Docling is not available"):
        processor.process_file("test.pdf")
    
    with pytest.raises(ValueError, match="Docling is not available"):
        processor.process_directory("test_dir")


def test_process_file_not_found(monkeypatch):
    """Test handling of non-existent files"""
    def mock_init_docling(instance):
        instance.docling_available = True
        instance.DocumentConverter = MagicMock()
        instance.PipelineOptions = MagicMock()
        instance.converter = MagicMock()
    
    monkeypatch.setattr(DoclingProcessor, "_init_docling", mock_init_docling)
    monkeypatch.setattr(Path, "exists", lambda _: False)
    
    processor = DoclingProcessor()
    
    with pytest.raises(ValueError, match="File not found"):
        processor.process_file("nonexistent.pdf")


def test_process_file_success(monkeypatch):
    """Test successful file processing"""
    def mock_init_docling(instance):
        instance.docling_available = True
        instance.PipelineOptions = MagicMock()
        instance.DocumentConverter = MagicMock()
        instance.converter = MagicMock()
        
        # Mock result document
        mock_result = MagicMock()
        mock_document = MagicMock()
        mock_result.document = mock_document
        instance.converter.convert.return_value = mock_result
    
    monkeypatch.setattr(DoclingProcessor, "_init_docling", mock_init_docling)
    monkeypatch.setattr(Path, "exists", lambda _: True)
    
    processor = DoclingProcessor()
    
    # Process a file
    result = processor.process_file("test.pdf")
    
    # Verify the result
    assert result is processor.converter.convert.return_value.document
    processor.converter.convert.assert_called_once()
    processor.PipelineOptions.assert_called_once()


def test_process_directory(monkeypatch):
    """Test directory processing"""
    def mock_init_docling(instance):
        instance.docling_available = True
        instance.PipelineOptions = MagicMock()
        instance.DocumentConverter = MagicMock()
        instance.converter = MagicMock()
        
        # Mock result document
        mock_document = MagicMock()
        mock_result = MagicMock()
        mock_result.document = mock_document
        instance.converter.convert.return_value = mock_result
    
    monkeypatch.setattr(DoclingProcessor, "_init_docling", mock_init_docling)
    monkeypatch.setattr(Path, "exists", lambda _: True)
    monkeypatch.setattr(Path, "is_dir", lambda _: True)
    
    # Create mock file paths that support the necessary interface
    class MockPath:
        def __init__(self, name, is_supported=True):
            self.name = name
            self.is_supported = is_supported
        
        def __str__(self):
            return self.name
        
        def is_file(self):
            return True
        
        @property
        def suffix(self):
            if self.is_supported:
                return "." + self.name.split(".")[-1]
            else:
                return ".unsupported"
    
    # Create test files
    test_files = [
        MockPath("test1.pdf"),
        MockPath("test2.docx"),
        MockPath("test3.txt"),
        MockPath("test4.unsupported", is_supported=False)  # Should be skipped
    ]
    
    def mock_glob(*args, **kwargs):
        return test_files
    
    monkeypatch.setattr(Path, "glob", mock_glob)
    
    processor = DoclingProcessor()
    results = processor.process_directory("test_dir")
    
    # Verify results - should have 3 processed files (not the unsupported one)
    assert len(results) == 3
    assert processor.converter.convert.call_count == 3


def test_process_directory_not_found(monkeypatch):
    """Test handling of non-existent directories"""
    def mock_init_docling(instance):
        instance.docling_available = True
        instance.PipelineOptions = MagicMock()
        instance.DocumentConverter = MagicMock()
        instance.converter = MagicMock()
    
    monkeypatch.setattr(DoclingProcessor, "_init_docling", mock_init_docling)
    monkeypatch.setattr(Path, "exists", lambda _: False)
    
    processor = DoclingProcessor()
    
    with pytest.raises(ValueError, match="Directory not found"):
        processor.process_directory("nonexistent_dir") 