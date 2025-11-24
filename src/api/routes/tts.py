"""Text-to-Speech API routes"""
import logging
from fastapi import APIRouter, Depends

from api.schemas import (
    TTSGenerateRequest,
    TTSSimplifyRequest,
    TTSResponse,
    TTSSimplifyResponse,
    VoicesResponse,
    TTSVoice
)
from api.dependencies import get_tts_service, get_simplification_service
from services.tts import TTSService
from services.simplification import SimplificationService
from core.exceptions import validate_text_length

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tts", tags=["Text-to-Speech"])


@router.post("/generate", response_model=TTSResponse)
async def generate_tts(
    request: TTSGenerateRequest,
    service: TTSService = Depends(get_tts_service)
):
    """
    Generate text-to-speech audio with word-level timestamps.
    
    - **text**: Text to convert to speech (1-10000 characters)
    - **voice**: Voice to use (Puck, Chorus, Cora, Dan, Wave)
    - **sample_rate**: Audio sample rate in Hz (default: 24000)
    
    Returns base64-encoded WAV audio with word-level timestamps.
    """
    # Validate text length
    validate_text_length(request.text)
    
    # Generate TTS
    audio_base64, duration, timestamps, processing_time_ms = await service.generate_speech(
        text=request.text,
        voice=request.voice,
        sample_rate=request.sample_rate
    )
    
    return TTSResponse(
        audio_base64=audio_base64,
        audio_format="wav",
        audio_duration=duration,
        timestamps=timestamps,
        processing_time_ms=processing_time_ms
    )


@router.post("/simplify", response_model=TTSSimplifyResponse)
async def simplify_and_generate_tts(
    request: TTSSimplifyRequest,
    tts_service: TTSService = Depends(get_tts_service),
    simplification_service: SimplificationService = Depends(get_simplification_service)
):
    """
    Simplify text and generate TTS audio in one request.
    
    - **text**: Text to simplify and convert to speech
    - **simplification**: Simplification settings (optional, uses defaults if not provided)
    - **voice**: Voice to use
    - **sample_rate**: Audio sample rate in Hz
    
    Returns simplified text with base64-encoded WAV audio and timestamps.
    """
    # Validate text length
    validate_text_length(request.text)
    
    # Use default simplification settings if not provided
    if request.simplification is None:
        from api.schemas.common import SimplificationMode, SimplificationIntensity
        mode = SimplificationMode.GENERAL
        intensity = SimplificationIntensity.MEDIUM
        custom_length = None
        options = None
    else:
        mode = request.simplification.mode
        intensity = request.simplification.intensity
        custom_length = request.simplification.custom_sentence_length
        options = request.simplification.options
    
    # Simplify text
    simplified_text, _, simplify_time = await simplification_service.simplify_text(
        text=request.text,
        mode=mode,
        intensity=intensity,
        custom_sentence_length=custom_length,
        options=options
    )
    
    # Generate TTS from simplified text
    audio_base64, duration, timestamps, tts_time = await tts_service.generate_speech(
        text=simplified_text,
        voice=request.voice,
        sample_rate=request.sample_rate
    )
    
    total_time = simplify_time + tts_time
    
    return TTSSimplifyResponse(
        original_text=request.text,
        simplified_text=simplified_text,
        audio_base64=audio_base64,
        audio_format="wav",
        audio_duration=duration,
        timestamps=timestamps,
        processing_time_ms=total_time
    )


@router.get("/voices", response_model=VoicesResponse)
async def get_voices():
    """
    Get available TTS voices.
    """
    voices = [voice.value for voice in TTSVoice]
    
    return VoicesResponse(
        voices=voices,
        default_voice=TTSVoice.PUCK.value
    )
