"""Dependency injection for API routes"""
from services.simplification import SimplificationService
from services.tts import TTSService
from services.larf import LarfService
# Global service instances (lazy loaded)
_simplification_service = None
_tts_service = None
_larf_service = None

def get_simplification_service() -> SimplificationService:
    """Get or create SimplificationService instance"""
    global _simplification_service
    if _simplification_service is None:
        _simplification_service = SimplificationService()
    return _simplification_service


def get_tts_service() -> TTSService:
    """Get or create TTSService instance"""
    global _tts_service
    if _tts_service is None:
        _tts_service = TTSService()
    return _tts_service

def get_larf_service() -> LarfService:
    """Get or create LarfService instance"""
    global _larf_service
    if _larf_service is None:
        _larf_service = LarfService()
    return _larf_service