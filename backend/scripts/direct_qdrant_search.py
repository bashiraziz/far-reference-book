"""Direct Qdrant search without any filtering."""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.services.vector_store import VectorStoreService
from backend.services.embeddings import EmbeddingsService
from backend.config.settings import settings
from backend.config.logging import logger

def main():
    """Direct search test."""
    logger.info("=== Direct Qdrant Search Test ===\n")

    try:
        client = VectorStoreService.get_client()

        # Generate embedding
        query = "method of dissemination of information"
        logger.info(f"Query: '{query}'")
        embedding = EmbeddingsService.generate_embedding(query)
        logger.info(f"Embedding dimensions: {len(embedding)}\n")

        # Direct query with NO threshold
        logger.info("Searching with NO score threshold...")
        results = client.query_points(
            collection_name=settings.qdrant_collection_name,
            query=embedding,
            limit=10,
            score_threshold=0.0  # Accept ANY result
        ).points

        logger.info(f"Found {len(results)} results:\n")

        for i, result in enumerate(results, 1):
            logger.info(f"Result {i}:")
            logger.info(f"  ID: {result.id}")
            logger.info(f"  Score: {result.score}")
            logger.info(f"  Payload keys: {list(result.payload.keys())}")
            logger.info(f"  Chapter: {result.payload.get('chapter', 'MISSING')}")
            logger.info(f"  Section: {result.payload.get('section', 'MISSING')}")
            logger.info(f"  Text: {result.payload.get('text', 'MISSING')[:100]}...")
            logger.info("")

        # Check for 5.101
        sections = [r.payload.get('section') for r in results]
        has_5_101 = '5.101' in sections or 5.101 in sections
        logger.info(f"Section 5.101 in top 10: {has_5_101}")
        logger.info(f"Sections found: {sections}")

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)

if __name__ == "__main__":
    main()
