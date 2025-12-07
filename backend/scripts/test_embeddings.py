"""
Test script to verify OpenAI embeddings API is working.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.services.embeddings import EmbeddingsService
from backend.config.logging import logger

def test_single_embedding():
    """Test generating a single embedding."""
    logger.info("Testing single embedding generation...")
    try:
        text = "This is a test of the Federal Acquisition Regulation."
        logger.info(f"Generating embedding for: {text}")
        embedding = EmbeddingsService.generate_embedding(text)
        logger.info(f"Success! Got embedding with dimension: {len(embedding)}")
        return True
    except Exception as e:
        logger.error(f"Failed to generate embedding: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_batch_embeddings():
    """Test generating batch embeddings."""
    logger.info("\nTesting batch embedding generation...")
    try:
        texts = [
            "Federal Acquisition Regulation Part 1",
            "Contracting requirements and procedures",
            "Procurement guidelines and standards"
        ]
        logger.info(f"Generating embeddings for {len(texts)} texts...")
        embeddings = EmbeddingsService.generate_embeddings_batch(texts)
        logger.info(f"Success! Got {len(embeddings)} embeddings")
        for i, emb in enumerate(embeddings):
            logger.info(f"  Embedding {i+1}: dimension {len(emb)}")
        return True
    except Exception as e:
        logger.error(f"Failed to generate batch embeddings: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    logger.info("=== OpenAI Embeddings API Test ===\n")

    success1 = test_single_embedding()
    success2 = test_batch_embeddings()

    logger.info("\n=== Test Results ===")
    logger.info(f"Single embedding: {'PASS' if success1 else 'FAIL'}")
    logger.info(f"Batch embeddings: {'PASS' if success2 else 'FAIL'}")

    if success1 and success2:
        logger.info("\nAll tests passed! OpenAI API is working.")
    else:
        logger.error("\nSome tests failed. Check the errors above.")
