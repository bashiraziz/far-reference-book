"""
Embeddings service for generating vector representations of text.

Uses Google's Gemini text-embedding-004 model.
"""

from typing import List
import google.generativeai as genai
from backend.config.settings import settings
from backend.config.logging import logger


class EmbeddingsService:
    """Handles text embedding generation."""

    @classmethod
    def _configure_gemini(cls):
        """Configure Gemini API."""
        genai.configure(api_key=settings.gemini_api_key)

    @classmethod
    def generate_embedding(cls, text: str) -> List[float]:
        """
        Generate embedding vector for a single text using Gemini.

        Args:
            text: Text to embed

        Returns:
            List of floats representing the embedding vector
        """
        cls._configure_gemini()

        result = genai.embed_content(
            model=settings.embedding_model,
            content=text,
            task_type="retrieval_document"
        )

        return result['embedding']

    @classmethod
    def generate_embeddings_batch(cls, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        if not texts:
            return []

        cls._configure_gemini()

        embeddings = []
        # Gemini API doesn't support batch embeddings in the same way,
        # so we process them one by one
        for text in texts:
            result = genai.embed_content(
                model=settings.embedding_model,
                content=text,
                task_type="retrieval_document"
            )
            embeddings.append(result['embedding'])

        return embeddings
