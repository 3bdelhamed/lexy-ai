"""
Cache Admin Routes  —  src/api/routes/admin.py

GET  /admin/cache         → stats (driver, enabled, ttl, key count)
POST /admin/cache/toggle  → enable/disable + change TTL at runtime
POST /admin/cache/flush   → delete all lexy:* cache entries

Protected by X-Api-Key header matching ADMIN_API_KEY env var.
If ADMIN_API_KEY is blank, routes are open (local dev only).
"""

import logging
from typing import Optional

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

from core.cache import cache_service
from core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin/cache", tags=["Cache Admin"])


# ── auth helper ──────────────────────────────────────────────────────────────

def _require_auth(x_api_key: str = "") -> None:
    if settings.admin_api_key and x_api_key != settings.admin_api_key:
        raise HTTPException(status_code=401, detail="Invalid or missing X-Api-Key header")


# ── schemas ──────────────────────────────────────────────────────────────────

class CacheToggleRequest(BaseModel):
    enabled: bool = Field(..., description="Enable or disable the cache")
    ttl_seconds: Optional[int] = Field(
        None, ge=60, le=604_800,
        description="New TTL in seconds (60 s → 7 days). Omit to keep current TTL."
    )


# ── routes ───────────────────────────────────────────────────────────────────

@router.get("", summary="Cache stats")
async def cache_stats(x_api_key: str = Header(default="")):
    """Returns current cache driver, enabled state, TTL, and key counts."""
    _require_auth(x_api_key)
    return await cache_service.stats()


@router.post("/toggle", summary="Enable / disable cache + update TTL")
async def toggle_cache(body: CacheToggleRequest, x_api_key: str = Header(default="")):
    """
    Toggle the cache on or off at runtime without restarting the server.
    Optionally update TTL for new entries.

    Example — disable for debugging:
        POST /admin/cache/toggle
        { "enabled": false }

    Example — set 1-hour TTL:
        POST /admin/cache/toggle
        { "enabled": true, "ttl_seconds": 3600 }
    """
    _require_auth(x_api_key)
    cache_service.enabled = body.enabled
    if body.ttl_seconds is not None:
        cache_service.ttl = body.ttl_seconds
    logger.info("Cache toggled: enabled=%s ttl=%s", cache_service.enabled, cache_service.ttl)
    return {
        "message": f"Cache {'enabled' if body.enabled else 'disabled'}",
        "enabled": cache_service.enabled,
        "ttl_seconds": cache_service.ttl,
        "driver": "upstash_redis" if cache_service._upstash else "memory",
    }


@router.post("/flush", summary="Delete all cached entries")
async def flush_cache(x_api_key: str = Header(default="")):
    """
    Delete all lexy:* keys from the cache store.
    Useful after changing the Groq model or prompt to avoid stale responses.
    """
    _require_auth(x_api_key)
    deleted = await cache_service.flush()
    logger.info("Cache flushed: %d entries deleted", deleted)
    return {"message": f"Flushed {deleted} cache entries", "deleted": deleted}
