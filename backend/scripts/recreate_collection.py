"""Recreate Qdrant collection with proper HNSW configuration."""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from qdrant_client.models import VectorParams, Distance, HnswConfigDiff
from backend.services.vector_store import VectorStoreService
from backend.config.settings import settings
from backend.config.logging import logger

def main():
    """Recreate collection with HNSW config."""
    logger.info("=== Recreating Qdrant Collection ===\n")

    try:
        client = VectorStoreService.get_client()
        collection_name = settings.qdrant_collection_name

        # Check current status
        logger.info("Current collection status:")
        collection = client.get_collection(collection_name)
        logger.info(f"  Points: {collection.points_count}")
        logger.info(f"  Status: {collection.status}")
        logger.info(f"  HNSW config: {collection.config.params.vectors}")

        # Confirm deletion
        logger.info(f"\n⚠️  WARNING: This will DELETE all {collection.points_count} points!")
        logger.info(f"Collection: {collection_name}")
        logger.info(f"\nTo proceed, you must manually confirm in code (set CONFIRM=True)")

        CONFIRM = True  # Confirmed by user
        if not CONFIRM:
            logger.warning("\nDeletion NOT confirmed - exiting safely")
            logger.info("\nTo fix this issue:")
            logger.info("1. Set CONFIRM=True in this script")
            logger.info("2. Re-run to delete and recreate collection")
            logger.info("3. Reload Part 5 data with populate_part_5.py")
            return

        # Delete existing collection
        logger.info(f"\nDeleting collection '{collection_name}'...")
        client.delete_collection(collection_name)
        logger.info("Collection deleted")

        # Recreate with proper HNSW config
        logger.info("\nRecreating collection with HNSW configuration...")
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=settings.embedding_dimensions,  # 512
                distance=Distance.COSINE,
                hnsw_config=HnswConfigDiff(
                    m=16,  # Number of edges per node (default: 16)
                    ef_construct=100,  # Size of dynamic candidate list for construction (default: 100)
                    full_scan_threshold=10000  # Threshold for switching to exact search
                )
            )
        )
        logger.info("Collection recreated with HNSW config")

        # Create payload indexes
        logger.info("\nCreating payload indexes...")
        # Fix: use 'source_file' instead of 'file'
        for field_name in ["source_file", "section", "chapter"]:
            try:
                client.create_payload_index(
                    collection_name=collection_name,
                    field_name=field_name,
                    field_schema="keyword" if field_name != "chapter" else "integer"
                )
                logger.info(f"  Created index for '{field_name}'")
            except Exception as e:
                logger.warning(f"  Failed to create index for '{field_name}': {e}")

        logger.info("\n✓ Collection recreated successfully!")
        logger.info("\nNext steps:")
        logger.info("1. Run populate_part_5.py to reload Part 5 data")
        logger.info("2. Test search functionality")

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)

if __name__ == "__main__":
    main()
