"""Check which FAR parts are currently loaded in Qdrant production database."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.services.vector_store import VectorStoreService
from backend.config.settings import settings
from backend.config.logging import logger

def main():
    """Check which parts are loaded in production database."""
    logger.info("=== Checking Loaded Parts in Production Database ===\n")
    logger.info(f"Collection: {settings.qdrant_collection_name}\n")

    try:
        client = VectorStoreService.get_client()

        # Get collection info
        info = client.get_collection(settings.qdrant_collection_name)
        logger.info(f"Total points: {info.points_count}")
        logger.info(f"Index status: {info.status}\n")

        # Get all unique chapters by scrolling through all points
        logger.info("Fetching all chapters...")
        chapters = set()
        offset = None

        while True:
            result = client.scroll(
                collection_name=settings.qdrant_collection_name,
                limit=100,
                offset=offset,
                with_payload=True,
                with_vectors=False
            )

            points, next_offset = result

            if not points:
                break

            for point in points:
                if 'chapter' in point.payload:
                    chapters.add(point.payload['chapter'])

            offset = next_offset
            if offset is None:
                break

        # Sort and display chapters
        sorted_chapters = sorted(chapters)
        logger.info(f"\nFound {len(sorted_chapters)} unique parts loaded:")
        logger.info(f"Parts: {sorted_chapters}\n")

        # Identify missing parts in range 1-53
        all_parts = set(range(1, 54))
        loaded_parts = set(sorted_chapters)
        missing_parts = sorted(all_parts - loaded_parts)

        if missing_parts:
            logger.info(f"Missing parts (1-53): {missing_parts}")
        else:
            logger.info("All parts 1-53 are loaded!")

        # Count points per part
        logger.info("\nPoints per part:")
        for chapter in sorted_chapters:
            result = client.scroll(
                collection_name=settings.qdrant_collection_name,
                scroll_filter={
                    "must": [
                        {"key": "chapter", "match": {"value": chapter}}
                    ]
                },
                limit=1,
                with_payload=False,
                with_vectors=False
            )
            # Get count by scrolling
            count = 0
            offset = None
            while True:
                result = client.scroll(
                    collection_name=settings.qdrant_collection_name,
                    scroll_filter={
                        "must": [
                            {"key": "chapter", "match": {"value": chapter}}
                        ]
                    },
                    limit=100,
                    offset=offset,
                    with_payload=False,
                    with_vectors=False
                )
                points, next_offset = result
                count += len(points)
                offset = next_offset
                if offset is None:
                    break

            logger.info(f"  Part {chapter}: {count} chunks")

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)

if __name__ == "__main__":
    main()
