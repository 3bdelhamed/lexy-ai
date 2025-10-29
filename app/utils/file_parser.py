import logging
from typing import Tuple, Optional
import io
from PyPDF2 import PdfReader
from docx import Document
from fastapi import HTTPException, UploadFile

logger = logging.getLogger(__name__)


class FileParser:
    """Utility class for parsing different file formats and extracting text."""
    
    @staticmethod
    async def extract_text_from_file(file: UploadFile) -> Tuple[str, str]:
        """
        Extract text from uploaded file.
        
        Args:
            file: UploadFile object
            
        Returns:
            Tuple of (file_type, extracted_text)
            
        Raises:
            HTTPException: If file type is not supported or parsing fails
        """
        file_type = file.filename.split(".")[-1].lower() if file.filename else ""
        
        if file_type not in ["txt", "pdf", "docx"]:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type: {file_type}. Supported types: txt, pdf, docx"
            )
        
        try:
            content = await file.read()
            
            if file_type == "txt":
                text = FileParser._parse_txt(content)
            elif file_type == "pdf":
                text = FileParser._parse_pdf(content)
            elif file_type == "docx":
                text = FileParser._parse_docx(content)
            else:
                # This should not happen due to the check above
                raise HTTPException(status_code=400, detail="Unsupported file type")
                
            if not text.strip():
                raise HTTPException(
                    status_code=400, 
                    detail="Could not extract text from the file. The file might be empty or corrupted."
                )
                
            return file_type, text
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error parsing file: {str(e)}")
            raise HTTPException(
                status_code=500, 
                detail=f"Error parsing file: {str(e)}"
            )
    
    @staticmethod
    def _parse_txt(content: bytes) -> str:
        """Parse text from TXT file."""
        try:
            return content.decode("utf-8")
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                return content.decode("latin-1")
            except Exception as e:
                raise ValueError(f"Could not decode text file: {str(e)}")
    
    @staticmethod
    def _parse_pdf(content: bytes) -> str:
        """Parse text from PDF file."""
        try:
            pdf_stream = io.BytesIO(content)
            pdf_reader = PdfReader(pdf_stream)
            
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
                
            return text
        except Exception as e:
            raise ValueError(f"Could not parse PDF file: {str(e)}")
    
    @staticmethod
    def _parse_docx(content: bytes) -> str:
        """Parse text from DOCX file."""
        try:
            docx_stream = io.BytesIO(content)
            doc = Document(docx_stream)
            
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
                
            return text
        except Exception as e:
            raise ValueError(f"Could not parse DOCX file: {str(e)}")