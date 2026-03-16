"""Configuration and settings for Lexy-AI  —  src/core/config.py"""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # ── LLM keys ─────────────────────────────────────────────────────────────
    gemini_api_key: str
    mistral_api_key: str = ""
    groq_api_key: str = ""
    groq_larf_model: str = "llama-3.3-70b-versatile"

    # ── Cache ─────────────────────────────────────────────────────────────────
    cache_enabled: bool = True
    cache_ttl_seconds: int = 86400                  # 24 hours
    upstash_redis_rest_url: str = ""                # Vercel → Storage → Upstash
    upstash_redis_rest_token: str = ""
    admin_api_key: str = ""                         # Protects /admin/cache routes

    # ── File / server ─────────────────────────────────────────────────────────
    max_file_size_mb: float = 10.0
    cors_origins: str = "http://localhost:3000,http://localhost:8000"
    log_level: str = "INFO"

    # ── Computed ──────────────────────────────────────────────────────────────
    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",")]

    @property
    def max_file_size_bytes(self) -> int:
        return int(self.max_file_size_mb * 1024 * 1024)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.gemini_api_key:
            raise ValueError(
                "GEMINI_API_KEY environment variable is required. "
                "Please set it in Vercel dashboard or .env file for local development."
            )


settings = Settings()
