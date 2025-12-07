"""Check if database has duplicate chunks."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.services.vector_store import VectorStoreService
from backend.config.settings import settings
from backend.config.logging import logger

def main():
    """Check for duplicate text in database."""
    try:
        client = VectorStoreService.get_client()

        # Sample some Part 30 points
        logger.info("Sampling Part 30 chunks to check for duplicates...")

        result = client.scroll(
            collection_name=settings.qdrant_collection_name,
            scroll_filter={
                "must": [
                    {"key": "chapter", "match": {"value": 30}}
                ]
            },
            limit=100
        )

        points, _ = result

        # Check for duplicate text
        texts = {}
        for point in points:
            text = point.payload.get('text', '')[:100]  # First 100 chars
            if text in texts:
                texts[text] += 1
            else:
                texts[text] = 1

        duplicates = {text: count for text, count in texts.items() if count > 1}

        logger.info(f"\nTotal unique text samples: {len(texts)}")
        logger.info(f"Duplicate text found: {len(duplicates)}")

        if duplicates:
            logger.warning("\nDuplicate chunks detected:")
            for text, count in list(duplicates.items())[:5]:
                logger.warning(f"  Found {count} times: {text}...")

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)

if __name__ == "__main__":
    main()
