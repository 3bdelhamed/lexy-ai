"""Configuration and settings for Lexy-AI"""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Required
    gemini_api_key: str
    
    # Optional with defaults
    max_file_size_mb: float = 10.0
    cors_origins: str = "http://localhost:3000,http://localhost:8000"
    log_level: str = "INFO"
    
    # Computed properties
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string"""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    @property
    def max_file_size_bytes(self) -> int:
        """Convert MB to bytes"""
        return int(self.max_file_size_mb * 1024 * 1024)
    
    model_config = SettingsConfigDict(
        # .env file is optional - Vercel injects env vars directly
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"  # Ignore extra env vars from Vercel runtime
    )
    
    def __init__(self, **kwargs):
        """Initialize settings and validate required fields"""
        super().__init__(**kwargs)
        if not self.gemini_api_key:
            raise ValueError(
                "GEMINI_API_KEY environment variable is required. "
                "Please set it in Vercel dashboard or .env file for local development."
            )


# Global settings instance
settings = Settings()
