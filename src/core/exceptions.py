"""Custom exceptions and error handlers for Lexy-AI"""
from typing import Optional, Dict, Any
from fastapi import Request
from fastapi.responses import JSONResponse
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


# Custom Exception Classes
class LexyAIException(Exception):
    """Base exception for Lexy-AI"""
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationException(LexyAIException):
    """Input validation errors"""
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(message, status_code=400, details=details)


class FileSizeException(LexyAIException):
    """File size limit exceeded"""
    def __init__(self, size_mb: float, max_mb: float):
        super().__init__(
            f"File size {size_mb:.2f}MB exceeds limit of {max_mb}MB",
            status_code=413,
            details={"size_mb": size_mb, "max_mb": max_mb}
        )


class UnsupportedFileException(LexyAIException):
    """Unsupported file type"""
    def __init__(self, file_type: str):
        super().__init__(
            f"Unsupported file type: {file_type}",
            status_code=415,
            details={"file_type": file_type, "supported": ["txt", "pdf", "docx"]}
        )


class LLMTimeoutException(LexyAIException):
    """LLM request timeout"""
    def __init__(self):
        super().__init__(
            "Request timeout - text may be too long or service is slow",
            status_code=504,
            details={"suggestion": "Try shorter text or retry later"}
        )


class TTSGenerationException(LexyAIException):
    """TTS generation failed"""
    def __init__(self, reason: str):
        super().__init__(
            f"TTS generation failed: {reason}",
            status_code=500,
            details={"reason": reason}
        )


# Exception Handlers
async def lexyai_exception_handler(
    request: Request,
    exc: LexyAIException
) -> JSONResponse:
    """Handle custom Lexy-AI exceptions"""
    logger.error(
        f"LexyAI Exception: {exc.message}",
        extra={"details": exc.details, "path": request.url.path}
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.__class__.__name__,
            "message": exc.message,
            "details": exc.details,
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url.path)
        }
    )


async def general_exception_handler(
    request: Request,
    exc: Exception
) -> JSONResponse:
    """Handle unexpected exceptions"""
    logger.exception(
        f"Unexpected exception: {str(exc)}",
        extra={"path": request.url.path}
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred",
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url.path)
        }
    )


# Utility Functions
def validate_text_length(text: str, max_length: int = 100000):
    """Validate text length"""
    if not text or not text.strip():
        raise ValidationException(
            "Text cannot be empty",
            details={"field": "text"}
        )
    
    if len(text) > max_length:
        raise ValidationException(
            f"Text exceeds maximum length of {max_length} characters",
            details={
                "field": "text",
                "received_length": len(text),
                "max_length": max_length
            }
        )


def validate_file_size(file_size_bytes: int, max_bytes: int):
    """Validate file size"""
    if file_size_bytes > max_bytes:
        size_mb = file_size_bytes / (1024 * 1024)
        max_mb = max_bytes / (1024 * 1024)
        raise FileSizeException(size_mb, max_mb)


def validate_file_type(filename: str, allowed_types: list = None):
    """Validate file type"""
    if allowed_types is None:
        allowed_types = ["txt", "pdf", "docx"]
    
    extension = filename.split(".")[-1].lower()
    if extension not in allowed_types:
        raise UnsupportedFileException(extension)
