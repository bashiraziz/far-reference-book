"""Estimate storage for Parts 30-52 with different chunk sizes."""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.config.logging import logger

def count_files_and_estimate(docs_dir: Path, start_part: int, end_part: int):
    """Count files and estimate chunks for parts."""
    total_files = 0
    total_chars = 0
    part_stats = []

    for part_num in range(start_part, end_part + 1):
        part_dir = docs_dir / f"part-{part_num}"
        if not part_dir.exists():
            continue

        md_files = list(part_dir.glob('*.md'))
        file_count = len(md_files)

        # Calculate total characters in this part
        part_chars = 0
        for md_file in md_files:
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Remove frontmatter
                    if content.startswith('---'):
                        parts = content.split('---', 2)
                        if len(parts) >= 3:
                            content = parts[2].strip()
                    part_chars += len(content)
            except Exception as e:
                logger.warning(f"Error reading {md_file}: {e}")

        if file_count > 0:
            part_stats.append({
                'part': part_num,
                'files': file_count,
                'chars': part_chars
            })
            total_files += file_count
            total_chars += part_chars

    return total_files, total_chars, part_stats

def estimate_chunks(total_chars: int, chunk_size: int, overlap: int) -> int:
    """Estimate number of chunks based on total characters."""
    # Effective step size (accounting for overlap)
    step_size = chunk_size - overlap
    # Estimate chunks (conservative)
    estimated_chunks = int((total_chars / step_size) * 1.2)  # 1.2 factor for sentence boundaries
    return estimated_chunks

def main():
    """Estimate storage for Parts 30-52."""
    logger.info("=== Storage Estimation for Parts 30-52 ===\n")

    project_root = Path(__file__).parent.parent.parent
    docs_dir = project_root / "docs"

    # Count files and characters
    total_files, total_chars, part_stats = count_files_and_estimate(docs_dir, 30, 52)

    logger.info(f"Parts 30-52 Summary:")
    logger.info(f"  Total parts found: {len(part_stats)}")
    logger.info(f"  Total files: {total_files:,}")
    logger.info(f"  Total characters: {total_chars:,}")
    logger.info(f"  Average chars per file: {total_chars / total_files if total_files > 0 else 0:,.0f}\n")

    # Show individual part stats
    logger.info("Individual part breakdown:")
    logger.info(f"{'Part':<8} {'Files':<10} {'Chars':<15} {'MB (est)':<12}")
    logger.info("-" * 50)

    for stat in part_stats:
        mb_estimate = (stat['chars'] * 1.5) / (1024 * 1024)  # Rough estimate with metadata
        logger.info(f"{stat['part']:<8} {stat['files']:<10} {stat['chars']:<15,} {mb_estimate:<12.2f}")

    logger.info("\n" + "=" * 80)
    logger.info("CHUNK SIZE ESTIMATES (for Parts 30-52 only)")
    logger.info("=" * 80 + "\n")

    # Test different chunk sizes
    chunk_configs = [
        (600, 150, "Current (600 chars)"),
        (1200, 250, "Medium (1200 chars)"),
        (1800, 350, "Large (1800 chars)"),
        (2400, 450, "Very Large (2400 chars)"),
    ]

    logger.info(f"{'Config':<25} {'Est. Chunks':<15} {'Est. Storage':<15} {'Fits in 1GB?':<15}")
    logger.info("=" * 70)

    # Assume 1.5KB per chunk with metadata and vectors
    bytes_per_chunk = 1500  # Conservative estimate
    gb_limit = 1024 * 1024 * 1024  # 1GB in bytes

    for chunk_size, overlap, label in chunk_configs:
        estimated_chunks = estimate_chunks(total_chars, chunk_size, overlap)
        estimated_bytes = estimated_chunks * bytes_per_chunk
        estimated_mb = estimated_bytes / (1024 * 1024)
        estimated_gb = estimated_bytes / (1024 * 1024 * 1024)

        fits = "✓ YES" if estimated_bytes < gb_limit else "✗ NO"

        logger.info(
            f"{label:<25} {estimated_chunks:<15,} {estimated_gb:<15.2f} GB {fits:<15}"
        )

    logger.info("\n" + "=" * 80)
    logger.info("RECOMMENDATIONS")
    logger.info("=" * 80)

    # Calculate recommended chunk size
    for chunk_size, overlap, label in chunk_configs:
        estimated_chunks = estimate_chunks(total_chars, chunk_size, overlap)
        estimated_bytes = estimated_chunks * bytes_per_chunk

        if estimated_bytes < gb_limit * 0.9:  # Leave 10% headroom
            logger.info(f"\n✓ RECOMMENDED: {label}")
            logger.info(f"  - Estimated chunks: {estimated_chunks:,}")
            logger.info(f"  - Estimated storage: {estimated_bytes / (1024**3):.2f} GB")
            logger.info(f"  - Headroom: {((gb_limit - estimated_bytes) / gb_limit * 100):.1f}%")
            logger.info(f"  - Coverage: Parts 30-52 (23 parts)")
            break
    else:
        logger.warning("\n✗ Parts 30-52 may not fit in 1GB even with 2400-char chunks")
        logger.warning("  Consider: Self-hosted Qdrant or larger chunks (3000+ chars)")

if __name__ == "__main__":
    main()
