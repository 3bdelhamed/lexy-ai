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
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


# Global settings instance
settings = Settings()
