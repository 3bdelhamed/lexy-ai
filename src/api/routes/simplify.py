"""Simplification API routes"""
import io
import logging
from datetime import datetime
from fastapi import APIRouter, Depends, UploadFile, File
from fastapi.responses import JSONResponse

from api.schemas import (
    TextSimplifyRequest,
    SimplifyResponse,
    ModesResponse
)
from api.dependencies import get_simplification_service
from services.simplification import SimplificationService, get_mode_descriptions
from core.exceptions import validate_text_length
from utils import FileParser, validate_uploaded_file

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/simplify", tags=["Simplification"])


@router.post("/text", response_model=SimplifyResponse)
async def simplify_text(
    request: TextSimplifyRequest,
    service: SimplificationService = Depends(get_simplification_service)
):
    """
    Simplify text using evidence-based dyslexia guidelines.
    
    - **text**: Text to simplify (1-10000 characters)
    - **mode**: Simplification mode (general, academic, technical, narrative, interactive)
    - **intensity**: Simplification intensity (light, medium, heavy, custom)
    - **custom_sentence_length**: Custom sentence length (only for custom intensity)
    - **options**: Advanced simplification options
    """
    # Validate text length
    validate_text_length(request.text)
    
    # Simplify text
    simplified_text, statistics, processing_time_ms = await service.simplify_text(
        text=request.text,
        mode=request.mode,
        intensity=request.intensity,
        custom_sentence_length=request.custom_sentence_length,
        options=request.options
    )
    
    return SimplifyResponse(
        original_text=request.text,
        simplified_text=simplified_text,
        processing_time_ms=processing_time_ms,
        timestamp=datetime.utcnow(),
        mode_used=request.mode,
        intensity_used=request.intensity,
        statistics=statistics
    )


@router.post("/file", response_model=SimplifyResponse)
async def simplify_file(
    file: UploadFile = File(..., description="File to simplify (TXT, PDF, DOCX, max 10MB)"),
    mode: str = "general",
    intensity: str = "medium",
    service: SimplificationService = Depends(get_simplification_service)
):
    """
    Simplify text from uploaded file.
    
    - **file**: File to upload (TXT, PDF, or DOCX, max 10MB)
    - **mode**: Simplification mode
    - **intensity**: Simplification intensity
    """
    # Validate and read file
    content = await validate_uploaded_file(file)
    
    # Parse file content
    text = FileParser.parse_file(io.BytesIO(content), file.filename)
    
    # Validate extracted text
    validate_text_length(text)
    
    # Simplify text
    from api.schemas.common import SimplificationMode, SimplificationIntensity
    
    simplified_text, statistics, processing_time_ms = await service.simplify_text(
        text=text,
        mode=SimplificationMode(mode),
        intensity=SimplificationIntensity(intensity)
    )
    
    return SimplifyResponse(
        original_text=text,
        simplified_text=simplified_text,
        processing_time_ms=processing_time_ms,
        timestamp=datetime.utcnow(),
        mode_used=SimplificationMode(mode),
        intensity_used=SimplificationIntensity(intensity),
        statistics=statistics
    )


@router.get("/modes", response_model=ModesResponse)
async def get_modes():
    """
    Get available simplification modes and their descriptions.
    """
    modes = get_mode_descriptions()
    
    return ModesResponse(
        modes=list(modes.keys()),
        intensities=["light", "medium", "heavy", "custom"],
        description=modes
    )
