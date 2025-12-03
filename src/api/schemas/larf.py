from typing import Optional
from pydantic import BaseModel, Field

class LarfAnnotateRequest(BaseModel):
    """Request to annotate text for dyslexia support"""
    text: str = Field(..., min_length=1, max_length=100000, description="Text to annotate")
    custom_focus: Optional[str] = Field(
        default=None,
        description="Optional instructions for custom focus (e.g., 'names of songs', 'medical terms')"
    )

class LarfResponse(BaseModel):
    """Response containing annotated HTML"""
    original_text: str
    annotated_html: str
    processing_time_ms: float