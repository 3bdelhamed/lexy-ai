"""API routes package"""
from .simplify import router as simplify_router
from .tts import router as tts_router
from .larf import router as larf_router
__all__ = ["simplify_router", "tts_router", "larf_router"]  