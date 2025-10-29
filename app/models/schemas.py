from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime
from enum import Enum


class SimplificationMode(str, Enum):
    general = "general"
    academic = "academic"
    technical = "technical"
    narrative = "narrative"
    interactive = "interactive"


class SimplificationIntensity(str, Enum):
    light = "light"
    medium = "medium"
    heavy = "heavy"
    custom = "custom"


class SentenceStructureControls(BaseModel):
    max_sentence_length: Optional[int] = Field(None, ge=5, le=50, description="Maximum words per sentence")
    sentence_breaking_mode: bool = Field(True, description="Automatically split long sentences")
    active_voice_enforcement: bool = Field(True, description="Convert passive to active voice")


class VocabularyControls(BaseModel):
    complex_word_replacement: Optional[Literal["light", "medium", "heavy", "off"]] = Field("medium", description="Complexity threshold for word replacement")
    synonym_suggestion_mode: Literal["auto-replace", "suggest-options", "highlight-only"] = Field("auto-replace", description="How to present word replacements")
    jargon_handling: Literal["remove", "define", "preserve"] = Field("define", description="How to handle technical terms")


class FormattingControls(BaseModel):
    paragraph_length: Optional[int] = Field(3, ge=1, le=5, description="Maximum sentences per paragraph")
    use_bullets: bool = Field(True, description="Use bullet points for lists")
    generous_whitespace: bool = Field(True, description="Add extra line spacing")


class SimplificationOptions(BaseModel):
    mode: SimplificationMode = Field(SimplificationMode.general, description="Simplification mode")
    intensity: SimplificationIntensity = Field(SimplificationIntensity.medium, description="Simplification intensity")
    custom_max_sentence_length: Optional[int] = Field(None, ge=5, le=50, description="Custom max sentence length (only used when intensity is 'custom')")
    sentence_structure: Optional[SentenceStructureControls] = Field(None, description="Sentence structure controls")
    vocabulary: Optional[VocabularyControls] = Field(None, description="Vocabulary controls")
    formatting: Optional[FormattingControls] = Field(None, description="Formatting controls")


class TextInput(BaseModel):
    text: str = Field(..., min_length=1, max_length=10000, description="Text to simplify")
    options: Optional[SimplificationOptions] = Field(None, description="Simplification options")


class SimplificationResponse(BaseModel):
    original_text: str = Field(..., description="Original input text")
    simplified_text: str = Field(..., description="Simplified text for dyslexic readers")
    processing_time_ms: int = Field(..., description="Processing time in milliseconds")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")
    options_used: Optional[SimplificationOptions] = Field(None, description="Options used for simplification")


class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Additional error details")