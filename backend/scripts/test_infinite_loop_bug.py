"""Test if chunk_text_generator can infinite loop."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.config.logging import logger
from backend.config.settings import settings

def chunk_text_generator_buggy(
    text: str,
    chunk_size: int,
    chunk_overlap: int
):
    """Same chunking logic as populate script - buggy version."""
    if not text:
        return

    start = 0
    text_length = len(text)
    count = 0
    max_iterations = 1000  # Safety limit

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

            if count >= max_iterations:
                logger.error(f"INFINITE LOOP DETECTED! Generated {count} chunks from {text_length} chars")
                logger.error(f"Last chunk: start={start}, end={end}, chunk_size={chunk_size}, overlap={chunk_overlap}")
                logger.error(f"Next start would be: {end - chunk_overlap if end < text_length else end}")
                break

        start = end - chunk_overlap if end < text_length else end

        # Debug: check if we're making progress
        if count > 10:
            logger.warning(f"Iteration {count}: start={start}, end={end}, text_length={text_length}")

def main():
    """Test chunking with all Part 30 files."""
    part_30_dir = Path("docs/part-30")

    for md_file in sorted(part_30_dir.glob('*.md')):
        logger.info(f"\nTesting file: {md_file.name}")

        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Remove frontmatter
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                content = parts[2].strip()

        logger.info(f"Content length: {len(content)} chars")

        # Generate chunks
        chunks = list(chunk_text_generator_buggy(content, settings.chunk_size, settings.chunk_overlap))

        logger.info(f"Generated {len(chunks)} chunks")

        if len(chunks) > 10:
            logger.error(f"SUSPICIOUS: {md_file.name} generated {len(chunks)} chunks from {len(content)} chars!")

if __name__ == "__main__":
    main()
