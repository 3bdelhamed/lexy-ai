from pydantic import BaseModel, Field

class ExtractResponse(BaseModel):
    """Response model for raw text extraction"""
    filename: str = Field(..., description="Name of the processed file")
    content: str = Field(..., description="Extracted raw text content")
    char_count: int = Field(..., description="Total character count of extracted text")