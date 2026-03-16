import io
import logging
from typing import Union
from fastapi import APIRouter, Depends, UploadFile, File, Query

from api.schemas.larf import LarfAnnotateRequest, LarfResponse, LarfJsonResponse
from api.dependencies import get_larf_service
from services.larf.service import LarfService
from services.larf.html_processor import html_to_larf_json
from core.exceptions import validate_text_length
from utils import FileParser, validate_uploaded_file

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/larf", tags=["LARF (Let AI Read First)"])


def _build_response(
    original_text: str,
    annotated_html: str,
    processing_time: float,
    fmt: str,
    cached: bool,
) -> Union[LarfResponse, LarfJsonResponse]:
    """Return the correct response model based on requested format."""
    if fmt == "html":
        return LarfResponse(
            original_text=original_text,
            annotated_html=annotated_html,
            processing_time_ms=processing_time,
            cached=cached,
        )

    # Default: json — post-process HTML into Flutter-ready structure
    larf_doc = html_to_larf_json(annotated_html, source_text=original_text)
    return LarfJsonResponse(
        original_text=original_text,
        annotated_html=annotated_html,
        data=larf_doc,
        processing_time_ms=processing_time,
        cached=cached,
    )


@router.post(
    "/annotate",
    response_model=Union[LarfJsonResponse, LarfResponse],
    summary="Annotate raw text for dyslexia support",
)
async def annotate_text(
    request: LarfAnnotateRequest,
    service: LarfService = Depends(get_larf_service),
):
    """
    Annotate plain text with HTML tags for dyslexia support.

    - **format**: `"json"` (default) → Flutter-ready paragraphs/spans structure
                  `"html"` → raw annotated HTML (original behaviour)
    - **use_cache**: `true` (default) → serve from cache when available
                     `false` → force fresh LLM call
    """
    validate_text_length(request.text)

    annotated_html, processing_time = await service.annotate_text(
        text=request.text,
        custom_focus=request.custom_focus,
        use_cache=request.use_cache,
    )

    # Detect whether the result came from cache
    # (service returns quickly when cached; we trust the use_cache flag)
    cached = request.use_cache and processing_time < 50  # <50 ms → almost certainly cache

    return _build_response(
        request.text, annotated_html, processing_time, request.format, cached
    )


@router.post(
    "/file",
    response_model=Union[LarfJsonResponse, LarfResponse],
    summary="Upload a file and annotate its content",
)
async def annotate_file(
    file: UploadFile = File(..., description="File to annotate (TXT, PDF, DOCX, max 10MB)"),
    custom_focus: str = Query(None, description="Optional custom focus (e.g., 'names', 'dates')"),
    format: str = Query("json", description="Response format: 'html' | 'json'"),
    use_cache: bool = Query(True, description="Set false to bypass cache"),
    service: LarfService = Depends(get_larf_service),
):
    """
    Upload a file and annotate its content for dyslexia support.
    Supports PDF, DOCX, and TXT.
    """
    content = await validate_uploaded_file(file)
    text = FileParser.parse_file(io.BytesIO(content), file.filename)
    validate_text_length(text)

    annotated_html, processing_time = await service.annotate_text(
        text=text,
        custom_focus=custom_focus,
        use_cache=use_cache,
    )

    cached = use_cache and processing_time < 50

    return _build_response(text, annotated_html, processing_time, format, cached)
