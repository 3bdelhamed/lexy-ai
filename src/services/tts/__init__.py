"""TTS service package"""
from .service import TTSService
from .timestamp import calculate_timestamps

__all__ = ["TTSService", "calculate_timestamps"]
