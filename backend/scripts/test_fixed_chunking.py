"""Test that the fixed chunking works without infinite loops."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.config.logging import logger
from backend.config.settings import settings

def chunk_text_generator_fixed(
    text: str,
    chunk_size: int,
    chunk_overlap: int
):
    """Fixed chunking logic - no infinite loops."""
    if not text:
        return

    start = 0
    text_length = len(text)

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
            yield chunk

        # Calculate next start, ensuring we always advance to avoid infinite loops
        if end < text_length:
            new_start = end - chunk_overlap
            # If new_start would move backwards, skip overlap entirely for this chunk
            if new_start <= start:
                start = end  # Jump to end, no overlap
            else:
                start = new_start
        else:
            start = end

def main():
    """Test chunking with all Part 30 files."""
    part_30_dir = Path("docs/part-30")

    total_chunks = 0
    for md_file in sorted(part_30_dir.glob('*.md')):
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Remove frontmatter
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                content = parts[2].strip()

        # Generate chunks
        chunks = list(chunk_text_generator_fixed(content, settings.chunk_size, settings.chunk_overlap))
        total_chunks += len(chunks)

        logger.info(f"{md_file.name}: {len(content)} chars -> {len(chunks)} chunks")

    logger.info(f"\nTotal chunks from Part 30: {total_chunks}")
    logger.info(f"Expected: ~22 chunks (2 per file × 11 files)")

    if total_chunks > 50:
        logger.error(f"FAILED: Generated too many chunks! ({total_chunks})")
    else:
        logger.info(f"SUCCESS: Chunking works correctly!")

if __name__ == "__main__":
    main()
