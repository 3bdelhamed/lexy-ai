"""File parsing utilities for TXT, PDF, and DOCX files"""
import logging
from typing import BinaryIO
import PyPDF2
from docx import Document

from core.exceptions import UnsupportedFileException, ValidationException

logger = logging.getLogger(__name__)


class FileParser:
    """Parse text from various file formats"""
    
    @staticmethod
    def parse_txt(file: BinaryIO) -> str:
        """Parse text from TXT file"""
        try:
            # Try UTF-8 first
            content = file.read()
            try:
                return content.decode('utf-8')
            except UnicodeDecodeError:
                # Fallback to Latin-1
                return content.decode('latin-1')
        except Exception as e:
            logger.error(f"Failed to parse TXT file: {str(e)}")
            raise ValidationException(f"Failed to read TXT file: {str(e)}")
    
    @staticmethod
    def parse_pdf(file: BinaryIO) -> str:
        """Parse text from PDF file"""
        try:
            pdf_reader = PyPDF2.PdfReader(file)
            text_parts = []
            
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
            
            if not text_parts:
                raise ValidationException("No text found in PDF file")
            
            return "\n\n".join(text_parts)
            
        except PyPDF2.errors.PdfReadError as e:
            logger.error(f"Failed to parse PDF file: {str(e)}")
            raise ValidationException(f"Corrupted or invalid PDF file: {str(e)}")
        except Exception as e:
            logger.error(f"Failed to parse PDF file: {str(e)}")
            raise ValidationException(f"Failed to read PDF file: {str(e)}")
    
    @staticmethod
    def parse_docx(file: BinaryIO) -> str:
        """Parse text from DOCX file"""
        try:
            doc = Document(file)
            text_parts = []
            
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text_parts.append(paragraph.text)
            
            if not text_parts:
                raise ValidationException("No text found in DOCX file")
            
            return "\n\n".join(text_parts)
            
        except Exception as e:
            logger.error(f"Failed to parse DOCX file: {str(e)}")
            raise ValidationException(f"Failed to read DOCX file: {str(e)}")
    
    @staticmethod
    def parse_file(file: BinaryIO, filename: str) -> str:
        """
        Parse text from file based on extension.
        
        Args:
            file: File object
            filename: Original filename
        
        Returns:
            Extracted text
        """
        # Get file extension
        extension = filename.split(".")[-1].lower()
        
        # Parse based on extension
        if extension == "txt":
            return FileParser.parse_txt(file)
        elif extension == "pdf":
            return FileParser.parse_pdf(file)
        elif extension == "docx":
            return FileParser.parse_docx(file)
        else:
            raise UnsupportedFileException(extension)
