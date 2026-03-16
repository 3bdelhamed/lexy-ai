"""
Cache Service  —  src/core/cache.py
-------------------------------------
Plugs into the existing settings (core/config.py) object.

Drivers:
  PRIMARY   → Upstash Redis (HTTP-based, zero persistent sockets → Vercel-safe)
  FALLBACK  → In-process dict (local dev / no Upstash creds)

New env vars to add to .env / Vercel dashboard:
  CACHE_ENABLED              = true          master toggle (default: true)
  CACHE_TTL_SECONDS          = 86400         per-entry TTL (default: 24 h)
  UPSTASH_REDIS_REST_URL     = https://...   from Vercel → Storage → Upstash
  UPSTASH_REDIS_REST_TOKEN   = ...           from Vercel → Storage → Upstash
  ADMIN_API_KEY              = secret        protects /admin/cache routes
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import time
from typing import Any, Optional

import httpx

logger = logging.getLogger(__name__)


# ─── helpers ────────────────────────────────────────────────────────────────

def _env_bool(key: str, default: bool = True) -> bool:
    val = os.getenv(key, str(default)).strip().lower()
    return val in ("1", "true", "yes", "on")


def _env_int(key: str, default: int) -> int:
    try:
        return int(os.getenv(key, str(default)))
    except ValueError:
        return default


# ─── in-memory fallback ─────────────────────────────────────────────────────

class _MemoryStore:
    """TTL-aware dict. Good for local dev; resets on each cold start."""

    def __init__(self) -> None:
        self._store: dict[str, tuple[Any, float]] = {}

    def get(self, key: str) -> Optional[Any]:
        entry = self._store.get(key)
        if entry is None:
            return None
        value, expires_at = entry
        if time.time() > expires_at:
            del self._store[key]
            return None
        return value

    def set(self, key: str, value: Any, ttl: int) -> None:
        self._store[key] = (value, time.time() + ttl)

    def delete(self, key: str) -> None:
        self._store.pop(key, None)

    def flush(self) -> int:
        count = len(self._store)
        self._store.clear()
        return count

    def stats(self) -> dict:
        now = time.time()
        live = sum(1 for _, (_, exp) in self._store.items() if exp > now)
        return {"driver": "memory", "live_keys": live, "total_keys": len(self._store)}


_memory_store = _MemoryStore()


# ─── Upstash Redis (HTTP) ────────────────────────────────────────────────────

class _UpstashStore:
    """Vercel-safe Redis driver using Upstash REST API (no persistent sockets)."""

    def __init__(self, url: str, token: str) -> None:
        self._url = url.rstrip("/")
        self._headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    async def _pipeline(self, *args: Any) -> Any:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post(
                f"{self._url}/pipeline",
                headers=self._headers,
                json=[[str(a) for a in args]],
            )
            resp.raise_for_status()
            data = resp.json()
            return data[0].get("result") if isinstance(data, list) else data.get("result")

    async def get(self, key: str) -> Optional[Any]:
        raw = await self._pipeline("GET", key)
        if raw is None:
            return None
        try:
            return json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return raw

    async def set(self, key: str, value: Any, ttl: int) -> None:
        await self._pipeline("SET", key, json.dumps(value, ensure_ascii=False), "EX", ttl)

    async def delete(self, key: str) -> None:
        await self._pipeline("DEL", key)

    async def flush(self) -> int:
        cursor, deleted = "0", 0
        async with httpx.AsyncClient(timeout=10.0) as client:
            while True:
                resp = await client.post(
                    f"{self._url}/pipeline",
                    headers=self._headers,
                    json=[["SCAN", cursor, "MATCH", "lexy:*", "COUNT", "100"]],
                )
                resp.raise_for_status()
                cursor, keys = resp.json()[0]["result"]
                if keys:
                    del_resp = await client.post(
                        f"{self._url}/pipeline",
                        headers=self._headers,
                        json=[["DEL"] + keys],
                    )
                    deleted += del_resp.json()[0].get("result", 0)
                if cursor == "0":
                    break
        return deleted

    async def stats(self) -> dict:
        info = await self._pipeline("INFO", "keyspace")
        return {"driver": "upstash_redis", "info": info}


# ─── Public CacheService ─────────────────────────────────────────────────────

class CacheService:
    """
    Unified cache interface.

    Quick usage in a route:
        from core.cache import cache_service

        key = cache_service.make_key("larf", text + severity)
        cached = await cache_service.get(key)
        if cached:
            return cached

        result = ... # expensive LLM call
        await cache_service.set(key, result)
        return result

    Runtime toggle (no restart):
        cache_service.enabled = False
    """

    def __init__(self) -> None:
        self.enabled: bool = _env_bool("CACHE_ENABLED", True)
        self.ttl: int = _env_int("CACHE_TTL_SECONDS", 86400)
        self._upstash: Optional[_UpstashStore] = None

        url = os.getenv("UPSTASH_REDIS_REST_URL", "")
        token = os.getenv("UPSTASH_REDIS_REST_TOKEN", "")
        if url and token:
            self._upstash = _UpstashStore(url, token)
            logger.info("Cache: Upstash Redis driver active")
        else:
            logger.info("Cache: in-memory driver active (no UPSTASH_REDIS_REST_URL set)")

    # ── key helpers ──────────────────────────────────────────────────────────

    @staticmethod
    def make_key(prefix: str, payload: str) -> str:
        """Deterministic cache key from prefix + content hash."""
        digest = hashlib.sha256(payload.encode()).hexdigest()[:20]
        return f"lexy:{prefix}:{digest}"

    # ── core ops ─────────────────────────────────────────────────────────────

    async def get(self, key: str) -> Optional[Any]:
        if not self.enabled:
            return None
        try:
            if self._upstash:
                return await self._upstash.get(key)
            return _memory_store.get(key)
        except Exception as exc:
            logger.warning("Cache GET error: %s", exc)
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        if not self.enabled:
            return
        _ttl = ttl if ttl is not None else self.ttl
        try:
            if self._upstash:
                await self._upstash.set(key, value, _ttl)
            else:
                _memory_store.set(key, value, _ttl)
        except Exception as exc:
            logger.warning("Cache SET error: %s", exc)

    async def delete(self, key: str) -> None:
        try:
            if self._upstash:
                await self._upstash.delete(key)
            else:
                _memory_store.delete(key)
        except Exception as exc:
            logger.warning("Cache DELETE error: %s", exc)

    async def flush(self) -> int:
        try:
            if self._upstash:
                return await self._upstash.flush()
            return _memory_store.flush()
        except Exception as exc:
            logger.warning("Cache FLUSH error: %s", exc)
            return 0

    async def stats(self) -> dict:
        base = {
            "enabled": self.enabled,
            "ttl_seconds": self.ttl,
            "driver": "upstash_redis" if self._upstash else "memory",
        }
        try:
            extra = await self._upstash.stats() if self._upstash else _memory_store.stats()
            return {**base, **extra}
        except Exception as exc:
            return {**base, "error": str(exc)}


# ─── singleton ───────────────────────────────────────────────────────────────
cache_service = CacheService()
