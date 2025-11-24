"""Request schemas for the API"""
from typing import Optional
from pydantic import BaseModel, Field
from .common import (
    SimplificationMode,
    SimplificationIntensity,
    JargonHandling,
    ReplaceComplexWords,
    TTSVoice
)


class SimplificationOptions(BaseModel):
    """Advanced simplification options"""
    break_long_sentences: bool = Field(default=True, description="Break long sentences")
    use_active_voice: bool = Field(default=True, description="Convert to active voice")
    replace_complex_words: ReplaceComplexWords = Field(
        default=ReplaceComplexWords.MEDIUM,
        description="Word replacement intensity"
    )
    jargon_handling: JargonHandling = Field(
        default=JargonHandling.DEFINE,
        description="How to handle technical jargon"
    )
    use_bullet_points: bool = Field(default=True, description="Use bullet points for lists")
    paragraph_max_sentences: int = Field(
        default=3,
        ge=2,
        le=5,
        description="Maximum sentences per paragraph"
    )


class TextSimplifyRequest(BaseModel):
    """Request to simplify text"""
    text: str = Field(..., min_length=1, max_length=100000, description="Text to simplify")
    mode: SimplificationMode = Field(
        default=SimplificationMode.GENERAL,
        description="Simplification mode"
    )
    intensity: SimplificationIntensity = Field(
        default=SimplificationIntensity.MEDIUM,
        description="Simplification intensity"
    )
    custom_sentence_length: Optional[int] = Field(
        default=None,
        ge=5,
        le=50,
        description="Custom sentence length (only for custom intensity)"
    )
    options: Optional[SimplificationOptions] = Field(
        default=None,
        description="Advanced options"
    )


class TTSGenerateRequest(BaseModel):
    """Request to generate TTS"""
    text: str = Field(..., min_length=1, max_length=100000, description="Text to convert to speech")
    voice: TTSVoice = Field(default=TTSVoice.PUCK, description="Voice to use")
    sample_rate: int = Field(default=24000, description="Audio sample rate in Hz")


class TTSSimplifyRequest(BaseModel):
    """Request to simplify and generate TTS"""
    text: str = Field(..., min_length=1, max_length=100000, description="Text to simplify and convert")
    simplification: Optional[TextSimplifyRequest] = Field(
        default=None,
        description="Simplification settings (uses defaults if not provided)"
    )
    voice: TTSVoice = Field(default=TTSVoice.PUCK, description="Voice to use")
    sample_rate: int = Field(default=24000, description="Audio sample rate in Hz")
