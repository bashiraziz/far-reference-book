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

    # OpenAI
    openai_api_key: str

    # Qdrant Vector Store
    qdrant_url: str
    qdrant_api_key: str
    qdrant_collection_name: str = "far_content"

    # RAG Settings
    embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536
    max_chunk_retrieval: int = 5
    chunk_size: int = 1000
    chunk_overlap: int = 200

    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:3001"]

    # Logging
    log_level: str = "INFO"

    class Config:
        # Look for .env in backend directory
        env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields in .env


# Global settings instance
settings = Settings()
