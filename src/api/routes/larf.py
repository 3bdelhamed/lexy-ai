import logging
from fastapi import APIRouter, Depends

from api.schemas.larf import LarfAnnotateRequest, LarfResponse
from api.dependencies import get_larf_service
from services.larf.service import LarfService
from core.exceptions import validate_text_length

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/larf", tags=["LARF (Let AI Read First)"])

@router.post("/annotate", response_model=LarfResponse)
async def annotate_text(
    request: LarfAnnotateRequest,
    service: LarfService = Depends(get_larf_service)
):
    """
    Annotate text with HTML tags for dyslexia support (LARF method).
    
    - **text**: Text to annotate (1-10000 characters)
    - **custom_focus**: Optional instruction (e.g., "highlight medical terms")
    """
    # Validate text length
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