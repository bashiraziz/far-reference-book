"""
Clear all data from Qdrant collection without deleting the collection itself.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.services.vector_store import VectorStoreService
from backend.config.settings import settings
from backend.config.logging import logger

def clear_collection():
    """Clear all points from the collection."""
    try:
        client = VectorStoreService.get_client()
        collection_name = settings.qdrant_collection_name

        logger.info(f"Clearing all data from collection: {collection_name}")

        # Delete all points by filtering on any existing field
        # Using scroll and delete approach
        from qdrant_client.models import Filter, FieldCondition, MatchAny

        # Get collection info first
        collection_info = client.get_collection(collection_name)
        point_count = collection_info.points_count

        logger.info(f"Collection currently has {point_count} points")

        if point_count == 0:
            logger.info("Collection is already empty")
            return

        # Delete all points using scroll and delete
        offset = None
        deleted_count = 0
        batch_size = 1000

        while True:
            # Scroll through points
            points, next_offset = client.scroll(
                collection_name=collection_name,
                limit=batch_size,
                offset=offset,
                with_payload=False,
                with_vectors=False
            )

            if not points:
                break

            # Extract point IDs
            point_ids = [point.id for point in points]

            # Delete this batch
            client.delete(
                collection_name=collection_name,
                points_selector=point_ids
            )

            deleted_count += len(point_ids)
            logger.info(f"Deleted {deleted_count}/{point_count} points...")

            # Check if we're done
            if next_offset is None:
                break

            offset = next_offset

        # Verify deletion
        final_info = client.get_collection(collection_name)
        final_count = final_info.points_count

        logger.info(f"✓ Collection cleared! Points remaining: {final_count}")
        logger.info(f"Total deleted: {deleted_count} points")

    except Exception as e:
        logger.error(f"Error clearing collection: {e}")
        raise

if __name__ == "__main__":
    clear_collection()
