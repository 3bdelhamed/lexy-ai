"""Lexy-AI v2: Serverless Dyslexia Accessibility Platform"""
import sys
from pathlib import Path

src_dir = Path(__file__).parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

import logging
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from core.exceptions import LexyAIException, lexyai_exception_handler, general_exception_handler
from core.middleware import LoggingMiddleware
from api.routes import simplify_router, tts_router, larf_router, extract_router, admin_router
from api.schemas import HealthResponse

logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Lexy-AI v2",
    description="Serverless-First Dyslexia Accessibility Platform",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.add_middleware(LoggingMiddleware)
app.add_exception_handler(LexyAIException, lexyai_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

app.include_router(simplify_router)
app.include_router(tts_router)
app.include_router(larf_router)
app.include_router(extract_router)
app.include_router(admin_router)      # ← new


@app.get("/", response_model=dict)
async def root():
    return {
        "name": "Lexy-AI v2",
        "version": "2.0.0",
        "description": "Serverless-First Dyslexia Accessibility Platform",
        "endpoints": {
            "docs":              "/docs",
            "redoc":             "/redoc",
            "health":            "/health",
            # Extraction
            "extract_pdf":       "/extract/pdf",
            # Simplification
            "simplify_text":     "/simplify/text",
            "simplify_file":     "/simplify/file",
            "simplify_modes":    "/simplify/modes",
            # TTS
            "tts_generate":      "/tts/generate",
            "tts_simplify":      "/tts/simplify",
            "tts_voices":        "/tts/voices",
            # LARF
            "larf_annotate":     "/larf/annotate",
            "larf_file":         "/larf/file",
            # Cache admin
            "cache_stats":       "/admin/cache",
            "cache_toggle":      "/admin/cache/toggle",
            "cache_flush":       "/admin/cache/flush",
        },
    }


@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        version="2.0.0",
    )


application = app   # Vercel ASGI handler alias

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
