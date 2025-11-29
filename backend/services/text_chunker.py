"""
Text chunking utilities for splitting documents into manageable pieces.

Uses character-based splitting with overlap to maintain context.
"""

from typing import List
from backend.config.settings import settings


class TextChunker:
    """Handles document chunking for vector storage."""

    @classmethod
    def chunk_text(
        cls,
        text: str,
        chunk_size: int = None,
        chunk_overlap: int = None
    ) -> List[str]:
        """
        Split text into overlapping chunks.

        Args:
            text: Text to chunk
            chunk_size: Maximum characters per chunk (default from settings)
            chunk_overlap: Characters to overlap between chunks (default from settings)

        Returns:
            List of text chunks
        """
        if chunk_size is None:
            chunk_size = settings.chunk_size
        if chunk_overlap is None:
            chunk_overlap = settings.chunk_overlap

        if not text or len(text) == 0:
            return []

        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_size

            # If this is not the last chunk, try to break at a sentence or word boundary
            if end < len(text):
                # Look for sentence boundary (. ! ?)
                sentence_end = max(
                    text.rfind('. ', start, end),
                    text.rfind('! ', start, end),
                    text.rfind('? ', start, end)
                )

                if sentence_end > start:
                    end = sentence_end + 1
                else:
                    # Look for word boundary
                    space = text.rfind(' ', start, end)
                    if space > start:
                        end = space

            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            # Move start forward, accounting for overlap
            start = end - chunk_overlap if end < len(text) else end

        return chunks
