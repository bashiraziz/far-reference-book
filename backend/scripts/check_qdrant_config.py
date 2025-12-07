"""Check Qdrant collection configuration."""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.services.vector_store import VectorStoreService
from backend.config.settings import settings
from backend.config.logging import logger

def main():
    """Check collection config."""
    logger.info("=== Qdrant Collection Configuration ===\n")

    try:
        client = VectorStoreService.get_client()

        # Get collection info
        logger.info("Retrieving collection info...")
        collection = client.get_collection(settings.qdrant_collection_name)

        logger.info(f"Collection: {collection.config.params.vectors}")
        logger.info(f"Total points: {collection.points_count}")
        logger.info(f"Indexed vectors count: {collection.vectors_count}")

        logger.info(f"\nHNSW config:")
        if hasattr(collection.config.params.vectors, '__dict__'):
            vectors_config = collection.config.params.vectors
            logger.info(f"  {vectors_config}")
        else:
            logger.info(f"  {collection.config.params.vectors}")

        logger.info(f"\nOptimizer config:")
        logger.info(f"  {collection.config.optimizer_config}")

        logger.info(f"\nIndexing status:")
        if hasattr(collection, 'status'):
            logger.info(f"  {collection.status}")

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)

if __name__ == "__main__":
    main()
