"""Response schemas for the API"""
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from .common import (
    SimplificationMode,
    SimplificationIntensity,
    WordTimestamp,
    TextStatistics
)


class SimplifyResponse(BaseModel):
    """Response from text simplification"""
    original_text: str
    simplified_text: str
    processing_time_ms: float
    timestamp: datetime
    mode_used: SimplificationMode
    intensity_used: SimplificationIntensity
    statistics: TextStatistics


class TTSResponse(BaseModel):
    """Response from TTS generation"""
    audio_base64: str = Field(..., description="Base64-encoded WAV audio")
    audio_format: str = Field(default="wav", description="Audio format")
    audio_duration: float = Field(..., description="Audio duration in seconds")
    timestamps: List[WordTimestamp] = Field(..., description="Word-level timestamps")
    processing_time_ms: float


class TTSSimplifyResponse(BaseModel):
    """Response from combined simplification + TTS"""
    original_text: str
    simplified_text: str
    audio_base64: str = Field(..., description="Base64-encoded WAV audio")
    audio_format: str = Field(default="wav", description="Audio format")
    audio_duration: float = Field(..., description="Audio duration in seconds")
    timestamps: List[WordTimestamp] = Field(..., description="Word-level timestamps")
    processing_time_ms: float


class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    message: str
    details: dict
    timestamp: datetime
    path: str


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: datetime
    version: str = "2.0.0"


class ModesResponse(BaseModel):
    """Available simplification modes"""
    modes: List[str]
    intensities: List[str]
    description: dict


class VoicesResponse(BaseModel):
    """Available TTS voices"""
    voices: List[str]
    default_voice: str
