"""Check field names in Part 4 vs Part 5."""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from qdrant_client.models import Filter, FieldCondition, MatchValue
from backend.services.vector_store import VectorStoreService
from backend.config.settings import settings
from backend.config.logging import logger

def main():
    """Check payload field names."""
    logger.info("=== Checking Payload Field Names ===\n")

    try:
        client = VectorStoreService.get_client()

        # Get first few samples
        logger.info("Sampling first 10 points...")
        result = client.scroll(
            collection_name=settings.qdrant_collection_name,
            limit=10
        )

        if result[0]:
            # Check each point and collect unique payload structures
            payload_structures = {}
            for point in result[0]:
                chapter = point.payload.get('chapter', 'unknown')
                if chapter not in payload_structures:
                    payload_structures[chapter] = {
                        'keys': list(point.payload.keys()),
                        'has_file': 'file' in point.payload,
                        'has_source_file': 'source_file' in point.payload,
                        'sample': point.payload.get('section', 'N/A')
                    }

            logger.info(f"\nFound {len(payload_structures)} unique chapter structures:\n")
            for chapter, info in sorted(payload_structures.items()):
                logger.info(f"Chapter {chapter}:")
                logger.info(f"  Sample section: {info['sample']}")
                logger.info(f"  Payload keys: {info['keys']}")
                logger.info(f"  Has 'file' field: {info['has_file']}")
                logger.info(f"  Has 'source_file' field: {info['has_source_file']}")
                logger.info("")

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)

if __name__ == "__main__":
    main()
