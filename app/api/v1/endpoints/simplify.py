import logging
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from app.config.settings import Settings, get_settings
from app.models.schemas import TextInput, SimplificationResponse, ErrorResponse
from app.services.simplification_service import SimplificationService
from app.utils.file_parser import FileParser

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/text", response_model=SimplificationResponse)
async def simplify_text(
    text_input: TextInput,
    settings: Settings = Depends(get_settings)
):
    """
    Simplify text for dyslexic readers.
    
    - **text**: The text to simplify
    """
    try:
        # Initialize the service
        service = SimplificationService(settings)
        
        # Simplify the text
        simplified_text, processing_time = await service.simplify_text(text_input.text)
        
        return SimplificationResponse(
            original_text=text_input.text,
            simplified_text=simplified_text,
            processing_time_ms=processing_time
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in simplify_text: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred"
        )


@router.post("/file", response_model=SimplificationResponse)
async def simplify_file(
    file: UploadFile = File(...),
    settings: Settings = Depends(get_settings)
):
    """
    Simplify text from uploaded file for dyslexic readers.
    
    - **file**: The file to process (supports TXT, PDF, DOCX)
    """
    try:
        # Check file size
        file_size = 0
        content = await file.read()
        file_size = len(content)
        await file.seek(0)  # Reset file pointer
        
        max_size_bytes = settings.max_file_size_mb * 1024 * 1024
        if file_size > max_size_bytes:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size is {settings.max_file_size_mb}MB"
            )
        
        # Extract text from file
        file_type, text = await FileParser.extract_text_from_file(file)
        
        # Initialize the service
        service = SimplificationService(settings)
        
        # Simplify the text
        simplified_text, processing_time = await service.simplify_text(text)
        
        return SimplificationResponse(
            original_text=text,
            simplified_text=simplified_text,
            processing_time_ms=processing_time
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in simplify_file: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred"
        )