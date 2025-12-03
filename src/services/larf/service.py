import time
import logging
from google import genai
from google.genai import types

from core.config import settings
from core.exceptions import LLMTimeoutException, ValidationException
from services.larf.prompts import get_larf_system_prompt

logger = logging.getLogger(__name__)

class LarfService:
    """Service for LARF text annotation"""
    
    def __init__(self):
        self._client = None
    
    @property
    def client(self):
        """Lazy load the Gemini client"""
        if self._client is None:
            self._client = genai.Client(api_key=settings.gemini_api_key)
        return self._client
    
    async def annotate_text(self, text: str, custom_focus: str = None) -> tuple[str, float]:
        """
        Annotate text with dyslexia-friendly HTML tags.
        Returns: (annotated_html, processing_time_ms)
        """
        start_time = time.time()
        
        system_prompt = get_larf_system_prompt(custom_focus)
        
        try:
            logger.info("Sending LARF annotation request to Gemini")
            
            # Using flash model for speed as this is a formatting task
            response = self.client.models.generate_content(
                model='gemini-2.0-flash-lite',
                contents=text,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0.0, # Zero temperature for consistent formatting
                    max_output_tokens=8000
                )
            )
            
            annotated_html = response.text.strip()
            
            # Basic cleanup if model included markdown blocks despite instructions
            if annotated_html.startswith("```html"):
                annotated_html = annotated_html[7:]
            if annotated_html.startswith("```"):
                annotated_html = annotated_html[3:]
            if annotated_html.endswith("```"):
                annotated_html = annotated_html[:-3]
                
            processing_time_ms = (time.time() - start_time) * 1000
            
            return annotated_html.strip(), processing_time_ms

        except Exception as e:
            logger.error(f"LARF annotation failed: {str(e)}")
            if "timeout" in str(e).lower():
                raise LLMTimeoutException()
            raise ValidationException(f"Annotation failed: {str(e)}")