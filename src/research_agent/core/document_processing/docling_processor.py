"""
Module for processing documents using Docling's document understanding capabilities.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import os
import logging
from pathlib import Path

# Create a logger for this module
logger = logging.getLogger(__name__)

@dataclass
class DoclingProcessorOptions:
    """Configuration options for the Docling processor."""
    enable_ocr: bool = True
    extract_tables: bool = True
    extract_images: bool = True
    language: Optional[str] = None
    chunk_size: int = 1000
    chunk_overlap: int = 200


class DoclingProcessor:
    """Processes documents using Docling to extract structured content and metadata."""
    
    def __init__(self, options: Optional[DoclingProcessorOptions] = None):
        """
        Initialize the DoclingProcessor with configuration options.
        
        Args:
            options: Configuration options for document processing
        """
        self.options = options or DoclingProcessorOptions()
        self._init_docling()
        
    def _init_docling(self):
        """
        Initialize the Docling converter and check if the dependency is available.
        
        This is separated to allow for better error handling and testing.
        """
        try:
            # Try to import Docling modules
            from docling.document_converter import DocumentConverter, FormatOption
            from docling.datamodel.pipeline_options import PdfPipelineOptions
            from docling.datamodel.base_models import InputFormat
            
            self.DocumentConverter = DocumentConverter
            self.PdfPipelineOptions = PdfPipelineOptions
            self.InputFormat = InputFormat
            self.FormatOption = FormatOption
            
            logger.info("Using Docling API")
            
            # Initialize with default options - keeping it simple
            # Initialize converter - by default it should handle all formats
            self.converter = DocumentConverter()
            
            self.docling_available = True
            logger.info("Docling successfully initialized")
        except ImportError as e:
            self.docling_available = False
            logger.warning(f"Docling not available: {e}. Some document processing features will be limited.")
            self.DocumentConverter = None
            self.PdfPipelineOptions = None
            self.InputFormat = None
            self.FormatOption = None
            self.converter = None
        
    def process_file(self, file_path: str):
        """
        Process a single file with Docling and return the document.
        
        Args:
            file_path: Path to the file to process
            
        Returns:
            A DoclingDocument object representing the processed document
            
        Raises:
            ValueError: If Docling is not available or the file doesn't exist
            Exception: If there's an error during document processing
        """
        if not self.docling_available:
            raise ValueError("Docling is not available. Please install it with 'pip install docling'")
        
        file_path = Path(file_path)
        if not file_path.exists():
            raise ValueError(f"File not found: {file_path}")
        
        try:
            logger.info(f"Processing file: {file_path}")
            
            # Handle different file types
            file_ext = file_path.suffix.lower()
            
            # For text files, which Docling doesn't support directly, read them ourselves
            if file_ext == '.txt':
                logger.info(f"Processing text file directly: {file_path}")
                with open(file_path, 'r', encoding='utf-8') as f:
                    text_content = f.read()
                
                # Create a simple mock document structure
                from docling.datamodel.document import DoclingDocument, DocumentPart, DocumentPartType
                
                # Create a document with the text content
                document = DoclingDocument(
                    document_name=file_path.name,
                    document_type="text"
                )
                
                # Add the text content as a part
                document.add_part(
                    DocumentPart(
                        content=text_content,
                        type=DocumentPartType.TEXT,
                        metadata={"source": str(file_path)}
                    )
                )
                
                return document
            else:
                # For other supported formats, use Docling's converter
                result = self.converter.convert(str(file_path))
                logger.info(f"Successfully processed file with Docling: {file_path}")
                return result.document
                
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
            raise
    
    def process_directory(self, directory_path: str):
        """
        Process all supported files in a directory.
        
        Args:
            directory_path: Path to the directory containing documents
            
        Returns:
            A list of tuples with (file_path, document) for each successfully processed file
        """
        if not self.docling_available:
            raise ValueError("Docling is not available. Please install it with 'pip install docling'")
        
        directory_path = Path(directory_path)
        if not directory_path.exists() or not directory_path.is_dir():
            raise ValueError(f"Directory not found: {directory_path}")
        
        # Supported file extensions
        supported_extensions = {".pdf", ".docx", ".xlsx", ".html", ".png", ".jpg", ".jpeg", ".txt"}
        
        results = []
        processed_count = 0
        error_count = 0
        
        for file_path in directory_path.glob("**/*"):
            if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                try:
                    document = self.process_file(str(file_path))
                    results.append((str(file_path), document))
                    processed_count += 1
                    logger.info(f"Successfully processed {file_path}")
                except Exception as e:
                    logger.error(f"Error processing {file_path}: {e}")
                    error_count += 1
        
        logger.info(f"Directory processing complete. Processed {processed_count} files with {error_count} errors.")
        return results 