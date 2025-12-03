import logging
import io
from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, Query

from api.schemas.larf import LarfAnnotateRequest, LarfResponse
from api.dependencies import get_larf_service
from services.larf.service import LarfService
from core.exceptions import validate_text_length
from utils import FileParser, validate_uploaded_file

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/larf", tags=["LARF (Let AI Read First)"])

@router.post("/annotate", response_model=LarfResponse)
async def annotate_text(
    request: LarfAnnotateRequest,
    service: LarfService = Depends(get_larf_service)
):
    """
    Annotate raw text with HTML tags for dyslexia support.
    """
    validate_text_length(request.text)
    
    annotated_html, processing_time = await service.annotate_text(
        text=request.text,
        custom_focus=request.custom_focus
    )
    
    return LarfResponse(
        original_text=request.text,
        annotated_html=annotated_html,
        processing_time_ms=processing_time
    )

@router.post("/file", response_model=LarfResponse)
async def annotate_file(
    file: UploadFile = File(..., description="File to annotate (TXT, PDF, DOCX, max 10MB)"),
    custom_focus: Optional[str] = Query(
        None, 
        description="Optional custom focus (e.g., 'names', 'dates')"
    ),
    service: LarfService = Depends(get_larf_service)
):
    """
    Upload a file and annotate its content for dyslexia support.
    
    - **file**: The document file (PDF, DOCX, or TXT).
    - **custom_focus**: Optional instructions on what to prioritize highlighting.
    """
    content = await validate_uploaded_file(file)
    text = FileParser.parse_file(io.BytesIO(content), file.filename)
    validate_text_length(text)
    
    annotated_html, processing_time = await service.annotate_text(
        text=text,
        custom_focus=custom_focus
    )
    
    return LarfResponse(
        original_text=text,
        annotated_html=annotated_html,
        processing_time_ms=processing_time
    )