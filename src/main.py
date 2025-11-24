"""Lexy-AI v2: Serverless Dyslexia Accessibility Platform

FastAPI application entry point for Vercel deployment.
"""
import sys
from pathlib import Path

# Add src directory to Python path
src_dir = Path(__file__).parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

import logging
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from core.exceptions import (
    LexyAIException,
    lexyai_exception_handler,
    general_exception_handler
)
from core.middleware import LoggingMiddleware
from api.routes import simplify_router, tts_router
from api.schemas import HealthResponse

# Configure logging
logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Lexy-AI v2",
    description="Serverless-First Dyslexia Accessibility Platform",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Add custom middleware
app.add_middleware(LoggingMiddleware)

# Add exception handlers
app.add_exception_handler(LexyAIException, lexyai_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Include routers
app.include_router(simplify_router)
app.include_router(tts_router)


@app.get("/", response_model=dict)
async def root():
    """
    API information endpoint.
    """
    return {
        "name": "Lexy-AI v2",
        "version": "2.0.0",
        "description": "Serverless-First Dyslexia Accessibility Platform",
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/health",
            "simplify_text": "/simplify/text",
            "simplify_file": "/simplify/file",
            "simplify_modes": "/simplify/modes",
            "tts_generate": "/tts/generate",
            "tts_simplify": "/tts/simplify",
            "tts_voices": "/tts/voices"
        }
    }


@app.get("/health", response_model=HealthResponse)
async def health():
    """
    Health check endpoint.
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        version="2.0.0"
    )


# Vercel serverless handler
# Export as 'app' for Vercel's @vercel/python runtime
# The runtime will automatically wrap this ASGI application
application = app


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
