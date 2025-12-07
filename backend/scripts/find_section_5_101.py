"""Check if section 5.101 exists in Qdrant database."""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from qdrant_client.models import Filter, FieldCondition, MatchValue
from backend.services.vector_store import VectorStoreService
from backend.config.settings import settings
from backend.config.logging import logger

def main():
    """Search for section 5.101 using filters."""
    logger.info("=== Searching for Section 5.101 ===\n")

    try:
        client = VectorStoreService.get_client()

        # Search with filter for section 5.101
        logger.info("Filtering for section='5.101'...")
        results = client.scroll(
            collection_name=settings.qdrant_collection_name,
            scroll_filter=Filter(
                must=[
                    FieldCondition(
                        key='section',
                        match=MatchValue(value='5.101')
                    )
                ]
            ),
            limit=100
        )

        points = results[0]
        logger.info(f"Found {len(points)} points with section 5.101\n")

        if points:
            logger.info("SUCCESS: Section 5.101 IS in the database!\n")
            for i, point in enumerate(points[:5], 1):
                logger.info(f"Sample {i}:")
                logger.info(f"  ID: {point.id}")
                logger.info(f"  Chapter: {point.payload.get('chapter')}")
                logger.info(f"  Section: {point.payload.get('section')}")
                logger.info(f"  Chunk: {point.payload.get('chunk_index')}")
                logger.info(f"  Text: {point.payload.get('text', '')[:150]}...")
                logger.info("")
        else:
            logger.warning("FAILURE: Section 5.101 NOT FOUND in database")
            logger.info("This means section 5.101 was never successfully loaded")

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)

if __name__ == "__main__":
    main()
