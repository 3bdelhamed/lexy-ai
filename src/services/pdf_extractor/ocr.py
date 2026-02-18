import base64
import logging
import io
from abc import ABC, abstractmethod
from typing import Tuple
from core.config import settings

logger = logging.getLogger(__name__)

class OCRService(ABC):
    def __init__(self, name: str, cost_per_page: float, cost_per_region: float):
        self.name = name
        self.cost_per_page = cost_per_page
        self.cost_per_region = cost_per_region
        self.available = False
    
    @abstractmethod
    def process(self, image_bytes: bytes, region_type: str = "general") -> Tuple[str, float]:
        pass

class MistralOCR(OCRService):
    def __init__(self):
        super().__init__("Mistral OCR", 0.001, 0.0002)
        self.api_key = settings.mistral_api_key
        self._init_client()
    
    def _init_client(self):
        if not self.api_key:
            logger.warning("Mistral API key not found in settings. OCR disabled.")
            return
        try:
            from mistralai import Mistral
            self.client = Mistral(api_key=self.api_key)
            self.available = True
        except ImportError:
            logger.error("mistralai package not installed")
            self.available = False
            
    def process(self, image_bytes: bytes, region_type: str = "general") -> Tuple[str, float]:
        if not self.available:
            return "", 0.0
        try:
            base64_image = base64.b64encode(image_bytes).decode('utf-8')
            response = self.client.ocr.process(
                model="mistral-ocr-latest",
                document={
                    "type": "image_url",
                    "image_url": f"data:image/png;base64,{base64_image}"
                }
            )
            if response.pages and len(response.pages) > 0:
                return response.pages[0].markdown, 0.95
            return "", 0.0
        except Exception as e:
            logger.error(f"Mistral OCR error: {e}")
            return "", 0.0