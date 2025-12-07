"""Test uploading a single file to identify the duplication bug."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.config.logging import logger
from backend.services.vector_store import VectorStoreService
from backend.config.settings import settings

def main():
    """Test upload process with just one file."""
    # Read one Part 30 file
    test_file = Path("docs/part-30/30.101.md")

    with open(test_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Remove frontmatter
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            content = parts[2].strip()

    logger.info(f"File content length: {len(content)} chars")
    logger.info(f"File content: {content[:100]}...")

    # Now let's check how many points with this text exist in database
    logger.info("\nChecking database for this content...")

    client = VectorStoreService.get_client()

    # Sample Part 30 points and check for this specific content
    result = client.scroll(
        collection_name=settings.qdrant_collection_name,
        scroll_filter={
            "must": [
                {"key": "chapter", "match": {"value": 30}},
                {"key": "section", "match": {"value": "30.101"}}
            ]
        },
        limit=1000  # Get up to 1000 points
    )

    points, _ = result
    logger.info(f"\nFound {len(points)} points for Part 30, Section 30.101")

    # Check how many unique texts
    unique_texts = set()
    for point in points:
        text = point.payload.get('text', '')
        unique_texts.add(text)

    logger.info(f"Unique text chunks: {len(unique_texts)}")
    logger.info(f"Total points: {len(points)}")
    logger.info(f"Duplication factor: {len(points) / max(len(unique_texts), 1):.0f}x")

    # Show sample of unique chunks
    logger.info("\nUnique chunks found:")
    for i, text in enumerate(list(unique_texts)[:5]):
        logger.info(f"\n{i+1}. ({len(text)} chars) {text[:100]}...")

if __name__ == "__main__":
    main()
