"""Create fresh production collection with HNSW configuration."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from qdrant_client.models import VectorParams, Distance, HnswConfigDiff
from backend.services.vector_store import VectorStoreService
from backend.config.settings import settings
from backend.config.logging import logger

def main():
    """Create production collection."""
    logger.info("=== Creating Production Qdrant Collection ===\n")

    try:
        client = VectorStoreService.get_client()
        collection_name = settings.qdrant_collection_name

        logger.info(f"Creating collection: {collection_name}")

        # Create with HNSW config
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=settings.embedding_dimensions,  # 512
                distance=Distance.COSINE,
                hnsw_config=HnswConfigDiff(
                    m=16,
                    ef_construct=100,
                    full_scan_threshold=10000
                )
            )
        )
        logger.info("Collection created with HNSW config")

        # Create payload indexes
        logger.info("\nCreating payload indexes...")
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

        logger.info(f"\nProduction collection '{collection_name}' ready!")
        logger.info("Next: Run populate_parts_30_52.py to load data")

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)

if __name__ == "__main__":
    main()
