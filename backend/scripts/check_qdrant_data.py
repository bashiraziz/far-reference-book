"""
Script to check what data exists in Qdrant.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.services.vector_store import VectorStoreService
from backend.config.settings import settings
from backend.config.logging import logger

def main():
    logger.info("=== Checking Qdrant Collection ===\n")

    try:
        client = VectorStoreService.get_client()

        # Get collection info
        collection_info = client.get_collection(settings.qdrant_collection_name)
        logger.info(f"Collection: {settings.qdrant_collection_name}")
        logger.info(f"Points count: {collection_info.points_count}")

        # Try to scroll through some points
        logger.info("\nFetching sample points...")
        scroll_result = client.scroll(
            collection_name=settings.qdrant_collection_name,
            limit=10
        )

        points = scroll_result[0]
        logger.info(f"Retrieved {len(points)} points")

        if points:
            logger.info("\nSample points:")
            for i, point in enumerate(points[:5], 1):
                payload = point.payload
                logger.info(f"\n  Point {i}:")
                logger.info(f"    Chapter: {payload.get('chapter', 'N/A')}")
                logger.info(f"    Section: {payload.get('section', 'N/A')}")
                logger.info(f"    Text preview: {payload.get('text', '')[:100]}...")
        else:
            logger.warning("No points found in collection!")

    except Exception as e:
        logger.error(f"Error checking Qdrant: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
