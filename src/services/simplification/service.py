"""Text simplification service using Google Gemini AI"""
import time
import logging
from typing import Optional
from google import genai
from google.genai import types

from core.config import settings
from core.exceptions import LLMTimeoutException, ValidationException
from api.schemas import (
    SimplificationMode,
    SimplificationIntensity,
    SimplificationOptions,
    TextStatistics
)
from services.simplification.prompts import get_simplification_prompt

logger = logging.getLogger(__name__)


class SimplificationService:
    """Service for text simplification using Google Gemini"""
    
    def __init__(self):
        self._client = None
    
    @property
    def client(self):
        """Lazy load the Gemini client"""
        if self._client is None:
            self._client = genai.Client(api_key=settings.gemini_api_key)
        return self._client
    
    def _calculate_max_sentence_length(
        self,
        mode: SimplificationMode,
        intensity: SimplificationIntensity,
        custom_length: Optional[int] = None
    ) -> int:
        """Calculate maximum sentence length based on mode and intensity"""
        
        # Base lengths by mode
        mode_lengths = {
            SimplificationMode.GENERAL: 15,
            SimplificationMode.ACADEMIC: 18,
            SimplificationMode.TECHNICAL: 15,
            SimplificationMode.NARRATIVE: 12,
            SimplificationMode.INTERACTIVE: 15
        }
        
        base_length = mode_lengths.get(mode, 15)
        
        # Adjust by intensity
        if intensity == SimplificationIntensity.CUSTOM and custom_length:
            return custom_length
        elif intensity == SimplificationIntensity.LIGHT:
            return base_length + 5
        elif intensity == SimplificationIntensity.HEAVY:
            return max(10, base_length - 5)
        else:  # MEDIUM
            return base_length
    
    def _calculate_statistics(self, original: str, simplified: str) -> TextStatistics:
        """Calculate text statistics"""
        
        def count_words(text: str) -> int:
            return len(text.split())
        
        def avg_sentence_length(text: str) -> float:
            sentences = [s.strip() for s in text.replace('!', '.').replace('?', '.').split('.') if s.strip()]
            if not sentences:
                return 0.0
            total_words = sum(len(s.split()) for s in sentences)
            return total_words / len(sentences)
        
        return TextStatistics(
            original_word_count=count_words(original),
            simplified_word_count=count_words(simplified),
            original_avg_sentence_length=avg_sentence_length(original),
            simplified_avg_sentence_length=avg_sentence_length(simplified)
        )
    
    async def simplify_text(
        self,
        text: str,
        mode: SimplificationMode = SimplificationMode.GENERAL,
        intensity: SimplificationIntensity = SimplificationIntensity.MEDIUM,
        custom_sentence_length: Optional[int] = None,
        options: Optional[SimplificationOptions] = None
    ) -> tuple[str, TextStatistics, float]:
        """
        Simplify text using evidence-based dyslexia rules.
        
        Args:
            text: Text to simplify
            mode: Simplification mode
            intensity: Simplification intensity
            custom_sentence_length: Custom sentence length (for custom intensity)
            options: Advanced options
        
        Returns:
            Tuple of (simplified_text, statistics, processing_time_ms)
        """
        start_time = time.time()
        
        # Use default options if not provided
        if options is None:
            options = SimplificationOptions()
        
        # Calculate max sentence length
        max_sentence_length = self._calculate_max_sentence_length(
            mode, intensity, custom_sentence_length
        )
        
        # Convert options to dict for prompt
        options_dict = {
            "break_long_sentences": options.break_long_sentences,
            "use_active_voice": options.use_active_voice,
            "replace_complex_words": options.replace_complex_words.value,
            "jargon_handling": options.jargon_handling.value,
            "use_bullet_points": options.use_bullet_points,
            "paragraph_max_sentences": options.paragraph_max_sentences
        }
        
        # Generate prompt
        prompt = get_simplification_prompt(
            text=text,
            mode=mode,
            intensity=intensity,
            max_sentence_length=max_sentence_length,
            options=options_dict
        )
        
        logger.info(f"Simplifying text with mode={mode.value}, intensity={intensity.value}")
        
        try:
            # Call Gemini API
            # Note: Timeout is handled at the client level, not in GenerateContentConfig
            response = self.client.models.generate_content(
                model='gemini-2.0-flash-lite',
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.6,
                    max_output_tokens=8000
                )
            )
            
            simplified_text = response.text.strip()
            
            # Calculate statistics
            statistics = self._calculate_statistics(text, simplified_text)
            
            processing_time_ms = (time.time() - start_time) * 1000
            
            logger.info(f"Simplification completed in {processing_time_ms:.2f}ms")
            
            return simplified_text, statistics, processing_time_ms
            
        except Exception as e:
            logger.error(f"Simplification failed: {str(e)}")
            if "timeout" in str(e).lower():
                raise LLMTimeoutException()
            raise ValidationException(f"Simplification failed: {str(e)}")
