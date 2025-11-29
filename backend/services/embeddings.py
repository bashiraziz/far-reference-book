"""
Embeddings service for generating vector representations of text.

Uses OpenAI's text-embedding-3-small model.
"""

from typing import List
from openai import OpenAI
from backend.config.settings import settings
from backend.config.logging import logger


class EmbeddingsService:
    """Handles text embedding generation."""

    @classmethod
    def get_openai_client(cls) -> OpenAI:
        """Get OpenAI client instance."""
        return OpenAI(api_key=settings.openai_api_key)

    @classmethod
    def generate_embedding(cls, text: str) -> List[float]:
        """
        Generate embedding vector for a single text.

        Args:
            text: Text to embed

        Returns:
            List of floats representing the embedding vector
        """
        client = cls.get_openai_client()

        response = client.embeddings.create(
            model=settings.embedding_model,
            input=text,
            dimensions=settings.embedding_dimensions
        )

        return response.data[0].embedding

    @classmethod
    def generate_embeddings_batch(cls, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in a single API call.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        if not texts:
            return []

        client = cls.get_openai_client()

        response = client.embeddings.create(
            model=settings.embedding_model,
            input=texts,
            dimensions=settings.embedding_dimensions
        )

        # Sort by index to ensure correct order
        embeddings = sorted(response.data, key=lambda x: x.index)
        return [item.embedding for item in embeddings]
