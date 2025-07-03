"""Application configuration using Pydantic Settings.

This module centralizes all configuration management using environment variables.
Following 12-factor app principles for configuration.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """Main application settings."""
    
    # Application
    app_name: str = "Voice Calendar Agent"
    environment: str = "development"
    debug: bool = True
    
    # API
    api_v1_prefix: str = "/api/v1"
    backend_url: str = "http://localhost:8000"
    frontend_url: str = "http://localhost:5173"
    
    # Database
    database_url: str
    
    # Redis
    redis_url: str
    
    # Security
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 60 * 24  # 24 hours
    
    # VAPI
    vapi_private_key: str
    vapi_webhook_secret: Optional[str] = None
    
    # Google OAuth
    google_client_id: Optional[str] = None
    google_client_secret: Optional[str] = None
    google_redirect_uri: str = "http://localhost:8000/auth/google/callback"
    
    # LangChain
    openai_api_key: Optional[str] = None
    langchain_tracing_v2: bool = True
    langchain_api_key: Optional[str] = None
    langchain_project: str = "voice-calendar-agent"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Export for easy access
settings = get_settings()