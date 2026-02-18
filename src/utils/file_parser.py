import logging
import io
from typing import BinaryIO
from docx import Document
from core.exceptions import UnsupportedFileException, ValidationException
# NEW IMPORT
from services.pdf_extractor.service import PDFExtractionService

logger = logging.getLogger(__name__)

class FileParser:
    @staticmethod
    def parse_txt(file: BinaryIO) -> str:
        try:
            content = file.read()
            try: return content.decode('utf-8')
            except: return content.decode('latin-1')
        except Exception as e:
            raise ValidationException(f"Failed to read TXT: {str(e)}")
    
    @staticmethod
    def parse_pdf(file: BinaryIO) -> str:
        """Parse text from PDF file using Hybrid Engine"""
        try:
            file_bytes = file.read()
            extractor = PDFExtractionService()
            return extractor.extract_text(file_bytes)
        except Exception as e:
            logger.error(f"Failed to parse PDF: {str(e)}")
            raise ValidationException(f"Failed to process PDF: {str(e)}")
    
    @staticmethod
    def parse_docx(file: BinaryIO) -> str:
        try:
            doc = Document(file)
            return "\n\n".join([p.text for p in doc.paragraphs if p.text.strip()])
        except Exception as e:
            raise ValidationException(f"Failed to read DOCX: {str(e)}")

    @staticmethod
    def parse_file(file: BinaryIO, filename: str) -> str:
        extension = filename.split(".")[-1].lower()
        if extension == "txt": return FileParser.parse_txt(file)
        elif extension == "pdf": return FileParser.parse_pdf(file)
        elif extension == "docx": return FileParser.parse_docx(file)
        else: raise UnsupportedFileException(extension)