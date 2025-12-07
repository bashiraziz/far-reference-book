"""Check what parts are actually in the Qdrant database."""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.services.vector_store import VectorStoreService
from backend.config.settings import settings
from backend.config.logging import logger

def main():
    """Check all unique chapters in database."""
    logger.info("=== Checking All Parts in Database ===\n")

    try:
        client = VectorStoreService.get_client()

        # Scroll through database and collect all unique chapters
        logger.info("Scanning database for all unique chapters...")
        chapters = set()
        offset = None
        batch_count = 0
        total_scanned = 0

        while True:
            batch_count += 1
            result = client.scroll(
                collection_name=settings.qdrant_collection_name,
                limit=1000,
                offset=offset
            )

            points, offset = result

            if not points:
                break

            for point in points:
                chapter = point.payload.get('chapter')
                if chapter:
                    chapters.add(chapter)

            total_scanned += len(points)
            if batch_count % 10 == 0:
                logger.info(f"  Scanned {total_scanned} points, found {len(chapters)} unique chapters so far...")

            if offset is None:
                break

        logger.info(f"\nTotal points scanned: {total_scanned}")
        logger.info(f"Unique chapters found: {len(chapters)}")
        logger.info(f"\nAll chapters in database: {sorted(chapters)}")

        # Count points per chapter
        logger.info("\nCounting points per chapter...")
        chapter_counts = {}
        for chapter in sorted(chapters):
            # This is slow but accurate - count points with this chapter
            count_result = client.count(
                collection_name=settings.qdrant_collection_name,
                count_filter={
                    "must": [
                        {"key": "chapter", "match": {"value": chapter}}
                    ]
                }
            )
            chapter_counts[chapter] = count_result.count
            logger.info(f"  Chapter {chapter}: {count_result.count:,} points")

        logger.info(f"\n=== Summary ===")
        logger.info(f"Parts loaded: {sorted(chapters)}")
        logger.info(f"Parts missing: {sorted(set(range(1, 54)) - chapters)[:20]}... (showing first 20)")
        logger.info(f"\nLargest parts:")
        for chapter, count in sorted(chapter_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            logger.info(f"  Part {chapter}: {count:,} points")

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)

if __name__ == "__main__":
    main()
