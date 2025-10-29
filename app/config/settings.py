from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    app_name: str = "DyslexiaReader API"
    version: str = "1.0.0"
    debug: bool = False
    
    # API Keys
    gemini_api_key: str
    
    # File upload settings
    max_file_size_mb: int = 5
    allowed_file_types: list = ["txt", "pdf", "docx"]
    
    # CORS settings
    cors_origins: list = ["*"]
    
    class Config:
        env_file = ".env"


def get_settings() -> Settings:
    return Settings()