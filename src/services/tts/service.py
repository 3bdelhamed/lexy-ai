"""Text-to-Speech service using Google Gemini"""
import time
import logging
import io
import wave
import base64
from typing import List

from google import genai
from google.genai import types

from core.config import settings
from core.exceptions import TTSGenerationException
from api.schemas.common import TTSVoice, WordTimestamp
from services.tts.timestamp import calculate_timestamps

logger = logging.getLogger(__name__)


class TTSService:
    """Service for text-to-speech generation using Google Gemini"""
    
    def __init__(self):
        self._client = None
    
    @property
    def client(self):
        """Lazy load the Gemini client"""
        if self._client is None:
            self._client = genai.Client(api_key=settings.gemini_api_key)
        return self._client
    
    def _get_audio_duration(self, wav_bytes: bytes) -> float:
        """Extract audio duration from WAV file"""
        try:
            with wave.open(io.BytesIO(wav_bytes), 'rb') as wf:
                frames = wf.getnframes()
                rate = wf.getframerate()
                duration = frames / float(rate)
                return duration
        except Exception as e:
            logger.error(f"Failed to get audio duration: {str(e)}")
            return 0.0
    
    def _wrap_in_wav(self, raw_audio: bytes, sample_rate: int = 24000) -> bytes:
        """Wrap raw PCM audio in WAV container"""
        buffer = io.BytesIO()
        
        try:
            with wave.open(buffer, 'wb') as wf:
                wf.setnchannels(1)  # Mono
                wf.setsampwidth(2)  # 16-bit
                wf.setframerate(sample_rate)
                wf.writeframes(raw_audio)
            
            return buffer.getvalue()
        except Exception as e:
            logger.error(f"Failed to create WAV file: {str(e)}")
            raise TTSGenerationException(f"WAV creation failed: {str(e)}")
    
    async def generate_speech(
        self,
        text: str,
        voice: TTSVoice = TTSVoice.PUCK,
        sample_rate: int = 24000
    ) -> tuple[str, float, List[WordTimestamp], float]:
        """
        Generate speech audio in-memory with word-level timestamps.
        
        Args:
            text: Text to convert to speech
            voice: Voice to use
            sample_rate: Audio sample rate in Hz
        
        Returns:
            Tuple of (base64_audio, duration, timestamps, processing_time_ms)
        """
        start_time = time.time()
        
        logger.info(f"Generating TTS with voice={voice.value}, sample_rate={sample_rate}")
        
        try:
            # Generate speech using Gemini TTS
            response = self.client.models.generate_content(
                model='gemini-2.5-flash-preview-tts',
                contents=text,
                config=types.GenerateContentConfig(
                    response_modalities=['AUDIO'],
                    speech_config=types.SpeechConfig(
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name=voice.value
                            )
                        )
                    )
                )
            )
            
            # Get raw audio data
            if not response.candidates or not response.candidates[0].content.parts:
                raise TTSGenerationException("No audio data in response")
            
            # Extract audio from response
            audio_part = None
            for part in response.candidates[0].content.parts:
                if hasattr(part, 'inline_data') and part.inline_data:
                    audio_part = part.inline_data
                    break
            
            if not audio_part:
                raise TTSGenerationException("No audio data found in response")
            
            raw_audio = audio_part.data
            
            # Wrap in WAV container
            wav_bytes = self._wrap_in_wav(raw_audio, sample_rate)
            
            # Get audio duration
            duration = self._get_audio_duration(wav_bytes)
            
            # Encode to base64
            audio_base64 = base64.b64encode(wav_bytes).decode('utf-8')
            
            # Calculate word-level timestamps
            timestamps = calculate_timestamps(text, duration)
            
            processing_time_ms = (time.time() - start_time) * 1000
            
            logger.info(
                f"TTS generation completed in {processing_time_ms:.2f}ms, "
                f"duration={duration:.2f}s, words={len(timestamps)}"
            )
            
            return audio_base64, duration, timestamps, processing_time_ms
            
        except Exception as e:
            logger.error(f"TTS generation failed: {str(e)}")
            if isinstance(e, TTSGenerationException):
                raise
            raise TTSGenerationException(str(e))
