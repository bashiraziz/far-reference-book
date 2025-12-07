"""Check which FAR parts are in Qdrant."""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.services.vector_store import VectorStoreService
from backend.config.settings import settings
from backend.config.logging import logger

def main():
    """Check which parts are loaded."""
    try:
        client = VectorStoreService.get_client()

        # Get total count
        collection_info = client.get_collection(settings.qdrant_collection_name)
        logger.info(f"Total points: {collection_info.points_count}")

        # Sample multiple batches to see what parts we have
        logger.info("\nSampling points from end of database...")

        chapters = set()
        sections = set()

        # Sample from different offsets to get variety (including early Part 5 data)
        for offset_val in [1170000, 1180000, 1200000, 1300000]:
            try:
                scroll_result = client.scroll(
                    collection_name=settings.qdrant_collection_name,
                    limit=100,
                    offset=offset_val
                )

                points = scroll_result[0]
                logger.info(f"  Offset {offset_val}: Found {len(points)} points")

                for point in points:
                    chapter = point.payload.get('chapter')
                    section = point.payload.get('section')
                    if chapter:
                        chapters.add(chapter)
                    if section:
                        sections.add(section)
            except:
                logger.info(f"  Offset {offset_val}: No points (past end)")
                break

        logger.info(f"\nChapters found in late samples: {sorted(chapters)}")
        logger.info(f"Total unique chapters: {len(chapters)}")

        # Check specifically for Part 5 (section 5.101)
        has_part_5 = 5 in chapters
        has_section_5_101 = any('5.101' in str(s) for s in sections)

        logger.info(f"\nPart 5 found: {has_part_5}")
        logger.info(f"Section 5.101 found: {has_section_5_101}")

        if has_section_5_101:
            logger.info("✓ Section 5.101 (Method of dissemination of information) is now in the database!")

        # Show some section 5 samples if found
        if sections:
            section_5_samples = [s for s in sections if str(s).startswith('5.')]
            if section_5_samples:
                logger.info(f"\nPart 5 sections found: {sorted(section_5_samples)[:10]}")

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)

if __name__ == "__main__":
    main()
