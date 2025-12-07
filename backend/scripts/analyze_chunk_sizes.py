"""Analyze impact of different chunk sizes on Part 5."""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.config.logging import logger

def chunk_text_generator(text: str, chunk_size: int, chunk_overlap: int):
    """Yield overlapping chunks."""
    if not text:
        return

    start = 0
    text_length = len(text)
    count = 0

    while start < text_length:
        end = start + chunk_size

        if end < text_length:
            sentence_end = max(
                text.rfind('. ', start, end),
                text.rfind('! ', start, end),
                text.rfind('? ', start, end)
            )

            if sentence_end > start:
                end = sentence_end + 1
            else:
                space = text.rfind(' ', start, end)
                if space > start:
                    end = space

        chunk = text[start:end].strip()
        if chunk:
            count += 1
            yield chunk

        start = end - chunk_overlap if end < text_length else end

    return count

def analyze_file(file_path: Path, chunk_size: int, overlap: int):
    """Analyze a single file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Remove frontmatter
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            content = parts[2].strip()

    chunks = list(chunk_text_generator(content, chunk_size, overlap))
    return len(chunks), len(content)

def main():
    """Analyze Part 5 with different chunk sizes."""
    logger.info("=== Chunk Size Analysis for Part 5 ===\n")

    project_root = Path(__file__).parent.parent.parent
    part5_dir = project_root / "docs" / "part-5"

    if not part5_dir.exists():
        logger.error(f"Directory not found: {part5_dir}")
        return

    md_files = sorted(part5_dir.glob('*.md'))
    logger.info(f"Analyzing {len(md_files)} files from Part 5\n")

    # Test different chunk sizes
    chunk_configs = [
        (600, 150, "Current (600 chars)"),
        (1200, 200, "Medium (1200 chars)"),
        (1800, 300, "Large (1800 chars)"),
        (2400, 400, "Very Large (2400 chars)"),
    ]

    logger.info(f"{'Config':<25} {'Total Chunks':<15} {'Chars/Chunk':<15} {'Storage %':<15}")
    logger.info("=" * 70)

    baseline_chunks = None

    for chunk_size, overlap, label in chunk_configs:
        total_chunks = 0
        total_chars = 0

        for md_file in md_files:
            chunks, chars = analyze_file(md_file, chunk_size, overlap)
            total_chunks += chunks
            total_chars += chars

        avg_chunk_size = total_chars / total_chunks if total_chunks > 0 else 0

        if baseline_chunks is None:
            baseline_chunks = total_chunks
            storage_pct = 100.0
        else:
            storage_pct = (total_chunks / baseline_chunks) * 100

        logger.info(
            f"{label:<25} {total_chunks:<15,} {avg_chunk_size:<15.0f} {storage_pct:<15.1f}%"
        )

    logger.info("\n=== Recommendations ===")
    logger.info("1. Current (600): Best precision, but exceeds 1GB limit")
    logger.info("2. Medium (1200): 50% storage, good balance for FAR content")
    logger.info("3. Large (1800): 33% storage, still captures full sections")
    logger.info("4. Very Large (2400): 25% storage, may lose precision")
    logger.info("\nRecommended: 1200-1500 chars for FAR regulations")

if __name__ == "__main__":
    main()
