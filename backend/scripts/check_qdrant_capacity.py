"""Check Qdrant storage capacity and usage."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.services.vector_store import VectorStoreService
from backend.config.settings import settings
from backend.config.logging import logger


def format_bytes(bytes_value):
    """Format bytes to human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f} TB"


def main():
    """Check Qdrant capacity and usage."""
    logger.info("=== Qdrant Storage Capacity Check ===\n")

    try:
        client = VectorStoreService.get_client()
        collection_name = settings.qdrant_collection_name

        # Get collection info
        info = client.get_collection(collection_name)

        logger.info(f"Collection: {collection_name}")
        logger.info(f"Total points: {info.points_count:,}")
        logger.info(f"Index status: {info.status}")
        logger.info(f"Vector dimensions: {settings.embedding_dimensions}")

        # Calculate estimated storage
        # Each point has:
        # - Vector: 512 dimensions × 4 bytes (float32) = 2,048 bytes
        # - Payload (estimated): ~1,000 bytes (text chunk ~600 chars + metadata)
        # Total per point: ~3,048 bytes

        bytes_per_vector = settings.embedding_dimensions * 4  # float32
        estimated_payload_per_point = 1000  # Conservative estimate
        bytes_per_point = bytes_per_vector + estimated_payload_per_point

        total_bytes = info.points_count * bytes_per_point

        logger.info(f"\n--- Storage Estimate ---")
        logger.info(f"Bytes per vector: {bytes_per_vector:,} bytes ({settings.embedding_dimensions} × 4)")
        logger.info(f"Estimated payload per point: {estimated_payload_per_point:,} bytes")
        logger.info(f"Total per point: {bytes_per_point:,} bytes")
        logger.info(f"\nEstimated total storage: {format_bytes(total_bytes)} ({total_bytes:,} bytes)")

        # Qdrant Cloud free tier limit
        free_tier_limit = 1024 * 1024 * 1024  # 1 GB
        usage_percent = (total_bytes / free_tier_limit) * 100
        remaining_bytes = free_tier_limit - total_bytes

        logger.info(f"\n--- Qdrant Cloud Free Tier (1 GB) ---")
        logger.info(f"Used: {format_bytes(total_bytes)} ({usage_percent:.1f}%)")
        logger.info(f"Remaining: {format_bytes(remaining_bytes)} ({100 - usage_percent:.1f}%)")

        # Estimate how many more points can fit
        remaining_points = int(remaining_bytes / bytes_per_point)
        logger.info(f"\nEstimated capacity for additional points: ~{remaining_points:,} chunks")

        # Calculate how many FAR parts that represents
        avg_chunks_per_part = total_bytes / info.points_count if info.points_count > 0 else bytes_per_point
        parts_loaded = 26  # Current: Parts 1-3, 30-52
        total_far_parts = 53
        remaining_parts = total_far_parts - parts_loaded

        logger.info(f"\n--- FAR Parts Analysis ---")
        logger.info(f"Parts currently loaded: {parts_loaded}/{total_far_parts}")
        logger.info(f"Parts remaining: {remaining_parts} (Parts 4-29, 53)")

        # Rough estimate assuming similar chunk density
        avg_chunks_per_part_loaded = info.points_count / parts_loaded
        estimated_chunks_for_remaining = remaining_parts * avg_chunks_per_part_loaded

        logger.info(f"Average chunks per part (loaded): ~{avg_chunks_per_part_loaded:.0f}")
        logger.info(f"Estimated chunks needed for remaining parts: ~{estimated_chunks_for_remaining:.0f}")

        if estimated_chunks_for_remaining <= remaining_points:
            logger.info(f"\n✓ GOOD NEWS: Estimated storage is sufficient for all remaining FAR parts!")
            logger.info(f"  You have room for ~{remaining_points:,} chunks")
            logger.info(f"  You need ~{estimated_chunks_for_remaining:.0f} chunks")
        else:
            logger.info(f"\n⚠ WARNING: May not have enough storage for all remaining parts")
            logger.info(f"  You have room for ~{remaining_points:,} chunks")
            logger.info(f"  You need ~{estimated_chunks_for_remaining:.0f} chunks")
            logger.info(f"  Shortfall: ~{estimated_chunks_for_remaining - remaining_points:.0f} chunks")

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)


if __name__ == "__main__":
    main()
