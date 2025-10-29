from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class TextInput(BaseModel):
    text: str = Field(..., min_length=1, max_length=10000, description="Text to simplify")


class SimplificationResponse(BaseModel):
    original_text: str = Field(..., description="Original input text")
    simplified_text: str = Field(..., description="Simplified text for dyslexic readers")
    processing_time_ms: int = Field(..., description="Processing time in milliseconds")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")


class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Additional error details")