"""Test VectorStoreService.search() directly."""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.services.vector_store import VectorStoreService
from backend.services.embeddings import EmbeddingsService
from backend.config.logging import logger

def main():
    """Test VectorStoreService.search() directly."""
    logger.info("=== Testing VectorStoreService.search() ===\n")

    try:
        query = "method of dissemination of information"
        logger.info(f"Query: '{query}'\n")

        # Generate embedding
        logger.info("Generating embedding...")
        embedding = EmbeddingsService.generate_embedding(query)
        logger.info(f"Embedding dimensions: {len(embedding)}\n")

        # Test with threshold=0.3
        logger.info("Calling VectorStoreService.search(score_threshold=0.3, limit=5)...")
        results = VectorStoreService.search(
            query_vector=embedding,
            limit=5,
            score_threshold=0.3
        )

        logger.info(f"\nReturned {len(results)} results:\n")
        for i, result in enumerate(results, 1):
            logger.info(f"Result {i}:")
            logger.info(f"  ID: {result.get('id')}")
            logger.info(f"  Score: {result.get('score')}")
            logger.info(f"  Payload type: {type(result.get('payload'))}")
            logger.info(f"  Payload keys: {list(result.get('payload', {}).keys())}")

            payload = result.get('payload', {})
            logger.info(f"  Chapter: {payload.get('chapter')}")
            logger.info(f"  Section: {payload.get('section')}")
            logger.info(f"  Text: {payload.get('text', '')[:100]}...")
            logger.info("")

        # Also test with threshold=0.0
        logger.info("\nCalling VectorStoreService.search(score_threshold=0.0, limit=5)...")
        results_all = VectorStoreService.search(
            query_vector=embedding,
            limit=5,
            score_threshold=0.0
        )

        logger.info(f"Returned {len(results_all)} results with threshold=0.0\n")

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)

if __name__ == "__main__":
    main()
