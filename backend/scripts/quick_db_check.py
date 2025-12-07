"""Quick database status check."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.services.vector_store import VectorStoreService
from backend.config.settings import settings
from backend.config.logging import logger

def main():
    """Check database status."""
    try:
        client = VectorStoreService.get_client()
        collection = client.get_collection(settings.qdrant_collection_name)

        logger.info(f"Total points: {collection.points_count:,}")
        logger.info(f"Index status: {collection.status}")

        # Quick sample to see what chapters are being loaded
        result = client.scroll(
            collection_name=settings.qdrant_collection_name,
            limit=10
        )

        points, _ = result
        if points:
            chapters = set(p.payload.get('chapter') for p in points if p.payload)
            logger.info(f"Sample chapters: {sorted(chapters)}")

    except Exception as e:
        logger.error(f"Error: {e}")

if __name__ == "__main__":
    main()
