"""LARF schemas  —  src/api/schemas/larf.py"""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# ── Request ───────────────────────────────────────────────────────────────────

class LarfAnnotateRequest(BaseModel):
    """Request to annotate text for dyslexia support."""
    text: str = Field(..., min_length=1, max_length=100000, description="Text to annotate")
    custom_focus: Optional[str] = Field(
        default=None,
        description="Optional instructions for custom focus (e.g., 'names of songs', 'medical terms')"
    )
    format: str = Field(
        default="json",
        description="Response format: 'html' returns raw annotated HTML, 'json' returns Flutter-ready JSON"
    )
    use_cache: bool = Field(
        default=True,
        description="Set false to bypass cache and force a fresh LLM call"
    )


# ── HTML response (original behaviour) ───────────────────────────────────────

class LarfResponse(BaseModel):
    """Response containing annotated HTML (original format)."""
    original_text: str
    annotated_html: str
    processing_time_ms: float
    cached: bool = False


# ── Span / Paragraph for JSON response ───────────────────────────────────────

class Span(BaseModel):
    """A run of text with a list of styling annotations."""
    text: str
    annotations: List[str] = Field(
        default_factory=list,
        description=(
            "Annotation tokens: 'bold' | 'highlight' | 'underline' | 'italic' | "
            "'strikethrough' | 'color:#rrggbb' | 'bg_color:#rrggbb' | 'size:Npx'"
        )
    )


class Paragraph(BaseModel):
    """A block of text split into styled spans."""
    index: int
    type: str = Field(default="body", description="body | heading | list_item | quote")
    spans: List[Span]


class DocumentMetadata(BaseModel):
    word_count: int
    paragraph_count: int
    annotation_types: List[str]
    estimated_read_time_sec: int


class LarfDocument(BaseModel):
    """Flutter-ready structured document."""
    document_id: str
    paragraphs: List[Paragraph]
    metadata: DocumentMetadata


# ── JSON response ─────────────────────────────────────────────────────────────

class LarfJsonResponse(BaseModel):
    """Response containing Flutter-ready structured JSON."""
    original_text: str
    annotated_html: str          # raw HTML kept for web / debug use
    data: LarfDocument           # structured JSON for Flutter
    processing_time_ms: float
    cached: bool = False
