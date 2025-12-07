"""Search directly for section 5.101 in Qdrant."""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.services.vector_store import VectorStoreService
from backend.services.embeddings import EmbeddingsService
from backend.config.settings import settings
from backend.config.logging import logger

def main():
    """Search for section 5.101."""
    logger.info("=== Searching for Section 5.101 ===\n")

    try:
        client = VectorStoreService.get_client()

        # Get a sample embedding to search
        query = "method of dissemination of information"
        logger.info(f"Generating embedding for query: '{query}'")
        embedding = EmbeddingsService.generate_embedding(query)

        # Search Qdrant
        logger.info("Searching Qdrant...")
        results = VectorStoreService.search(
            query_vector=embedding,
            limit=10,
            score_threshold=0.0  # Get any results
        )

        logger.info(f"\nFound {len(results)} results:")
        for i, result in enumerate(results, 1):
            logger.info(f"\n  Result {i}:")
            logger.info(f"    Chapter: {result.get('chapter')}")
            logger.info(f"    Section: {result.get('section')}")
            logger.info(f"    Score: {result.get('score', 'N/A')}")
            logger.info(f"    Text preview: {result.get('text', '')[:150]}...")

        # Check if any are 5.101
        has_5_101 = any(result.get('section') == '5.101' for result in results)
        logger.info(f"\n\nSection 5.101 found in results: {has_5_101}")

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)

if __name__ == "__main__":
    main()
