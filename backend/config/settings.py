"""
Application settings and configuration.

Loads environment variables and provides configuration access.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Settings
    api_title: str = "FAR Reference Book API"
    api_version: str = "1.0.0"
    api_description: str = "RAG-powered chatbot for Federal Acquisition Regulations"

    # Database
    neon_database_url: str

    # Google Gemini AI
    gemini_api_key: str

    # Qdrant Vector Store
    qdrant_url: str
    qdrant_api_key: str
    qdrant_collection_name: str = "far_content_production"

    # RAG Settings
    embedding_model: str = "models/text-embedding-004"  # Gemini embedding model
    embedding_dimensions: int = 768  # Gemini embedding dimensions
    chat_model: str = "gemini-2.0-flash-exp"  # Gemini chat model (fast and free)
    max_chunk_retrieval: int = 5
    chunk_size: int = 600  # Optimized for better context while staying under 700MB
    chunk_overlap: int = 150  # Proportional overlap (25%)

    # CORS
    cors_origins: str = "https://bashiraziz.github.io,http://localhost:3000,http://localhost:3001,https://bashiraziz.github.io,https://bashiraziz.github.io/far-reference-book"

    def get_cors_origins(self) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    # Logging
    log_level: str = "INFO"

    class Config:
        # Look for .env in backend directory
        env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields in .env


# Global settings instance
settings = Settings()
