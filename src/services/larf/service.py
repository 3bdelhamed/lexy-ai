import time
import logging
from groq import AsyncGroq  # Modern SDK import

from core.config import settings
from core.cache import cache_service
from core.exceptions import LLMTimeoutException, ValidationException
from services.larf.prompts import get_larf_system_prompt

logger = logging.getLogger(__name__)

class LarfService:
    """Service for LARF text annotation using Groq"""
    
    def __init__(self):
        self._client = None
    
    @property
    def client(self):
        """Lazy load the Groq client"""
        if self._client is None:
            if not settings.groq_api_key:
                raise ValidationException("GROQ_API_KEY is not set in configuration.")
            
            # Modern SDK initialization
            self._client = AsyncGroq(api_key=settings.groq_api_key)
        return self._client
    
    async def annotate_text(
        self,
        text: str,
        custom_focus: str = None,
        use_cache: bool = True,
    ) -> tuple[str, float]:
        """
        Annotate text with dyslexia-friendly HTML tags using Groq.
        Returns: (annotated_html, processing_time_ms)
        """
        start_time = time.time()
        
        # ── Cache read ────────────────────────────────────────────────────────
        cache_key = cache_service.make_key(
            "larf", f"{text[:500]}:{custom_focus or ''}:{settings.groq_larf_model}"
        )

        if use_cache:
            cached = await cache_service.get(cache_key)
            if cached:
                logger.info("Cache HIT for LARF annotation")
                elapsed = (time.time() - start_time) * 1000
                return cached["annotated_html"], elapsed
                
        # Get the system prompt from your existing prompts file
        system_content = get_larf_system_prompt(custom_focus)
        
        try:
            logger.info(f"Sending LARF annotation request to Groq (Model: {settings.groq_larf_model})")
            
            # Modern SDK: Use max_completion_tokens instead of max_tokens
            chat_completion = await self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": system_content,
                    },
                    {
                        "role": "user",
                        "content": text,
                    }
                ],
                model=settings.groq_larf_model,
                temperature=0.0,
                max_completion_tokens=8000,  # Modern SDK parameter name
                stream=False,
            )
            
            # Extract content
            annotated_html = chat_completion.choices[0].message.content or ""
            
            # Handle empty response
            if not annotated_html.strip():
                raise ValidationException("Model returned empty response")
            
            # Clean up markdown code fences
            annotated_html = annotated_html.strip()
            if annotated_html.startswith("```html"):
                annotated_html = annotated_html[7:]
            elif annotated_html.startswith("```"):
                annotated_html = annotated_html[3:]
            
            if annotated_html.endswith("```"):
                annotated_html = annotated_html[:-3]
            annotated_html = annotated_html.strip()
            
            # ── Cache write ───────────────────────────────────────────────────
            await cache_service.set(cache_key, {"annotated_html": annotated_html})
                
            processing_time_ms = (time.time() - start_time) * 1000
            
            return annotated_html, processing_time_ms

        except Exception as e:
            logger.error(f"LARF annotation failed: {str(e)}")
            if "timeout" in str(e).lower():
                raise LLMTimeoutException()
            raise ValidationException(f"Groq Annotation failed: {str(e)}")