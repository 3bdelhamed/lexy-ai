"""Common schemas used across the API"""
from enum import Enum
from typing import List
from pydantic import BaseModel, Field


class SimplificationMode(str, Enum):
    """Available simplification modes"""
    GENERAL = "general"
    ACADEMIC = "academic"
    TECHNICAL = "technical"
    NARRATIVE = "narrative"
    INTERACTIVE = "interactive"


class SimplificationIntensity(str, Enum):
    """Simplification intensity levels"""
    LIGHT = "light"
    MEDIUM = "medium"
    HEAVY = "heavy"
    CUSTOM = "custom"


class JargonHandling(str, Enum):
    """How to handle technical jargon"""
    REMOVE = "remove"
    DEFINE = "define"
    PRESERVE = "preserve"


class ReplaceComplexWords(str, Enum):
    """Word replacement intensity"""
    OFF = "off"
    LIGHT = "light"
    MEDIUM = "medium"
    HEAVY = "heavy"


class TTSVoice(str, Enum):
    """Available TTS voices (Google Chirp-3-HD/Gemini-TTS)"""
    # Male voices
    PUCK = "Puck"      # Upbeat, conversational, friendly, energetic
    CHARON = "Charon"  # Deep, authoritative, informative, professional
    # Female voices
    ACHERNAR = "Achernar"  # Fast, energetic, soft
    AOEDE = "Aoede"        # Smooth, clear


class WordTimestamp(BaseModel):
    """Word-level timestamp"""
    word: str = Field(..., description="The word")
    start: float = Field(..., description="Start time in seconds")
    end: float = Field(..., description="End time in seconds")


class TextStatistics(BaseModel):
    """Text analysis statistics"""
    original_word_count: int
    simplified_word_count: int
    original_avg_sentence_length: float
    simplified_avg_sentence_length: float
