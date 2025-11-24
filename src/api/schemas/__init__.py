"""API schemas package"""
from .common import (
    SimplificationMode,
    SimplificationIntensity,
    JargonHandling,
    ReplaceComplexWords,
    TTSVoice,
    WordTimestamp,
    TextStatistics
)
from .requests import (
    SimplificationOptions,
    TextSimplifyRequest,
    TTSGenerateRequest,
    TTSSimplifyRequest
)
from .responses import (
    SimplifyResponse,
    TTSResponse,
    TTSSimplifyResponse,
    ErrorResponse,
    HealthResponse,
    ModesResponse,
    VoicesResponse
)

__all__ = [
    # Common
    "SimplificationMode",
    "SimplificationIntensity",
    "JargonHandling",
    "ReplaceComplexWords",
    "TTSVoice",
    "WordTimestamp",
    "TextStatistics",
    # Requests
    "SimplificationOptions",
    "TextSimplifyRequest",
    "TTSGenerateRequest",
    "TTSSimplifyRequest",
    # Responses
    "SimplifyResponse",
    "TTSResponse",
    "TTSSimplifyResponse",
    "ErrorResponse",
    "HealthResponse",
    "ModesResponse",
    "VoicesResponse",
]
