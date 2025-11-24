"""Input validation utilities"""
from fastapi import UploadFile
from core.config import settings
from core.exceptions import (
    validate_text_length,
    validate_file_size,
    validate_file_type
)


async def validate_uploaded_file(file: UploadFile) -> bytes:
    """
    Validate uploaded file and return content.
    
    Args:
        file: Uploaded file
    
    Returns:
        File content as bytes
    """
    # Validate file type
    validate_file_type(file.filename)
    
    # Read file content
    content = await file.read()
    
    # Validate file size
    validate_file_size(len(content), settings.max_file_size_bytes)
    
    return content
