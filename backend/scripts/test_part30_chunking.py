"""Test chunking on Part 30 file to find the bug."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.config.logging import logger
from backend.config.settings import settings

def chunk_text_generator(text: str, chunk_size: int, chunk_overlap: int):
    """Same chunking logic as populate script."""
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

            # Safety limit for testing
            if count > 1000:
                logger.error(f"INFINITE LOOP DETECTED! Generated {count} chunks from {text_length} chars")
                break

        start = end - chunk_overlap if end < text_length else end

def main():
    """Test chunking on Part 30 file."""
    test_file = Path("docs/part-30/30.101.md")

    logger.info(f"Testing chunking on: {test_file}")

    with open(test_file, 'r', encoding='utf-8') as f:
        content = f.read()

    logger.info(f"File size: {len(content)} characters")

    # Remove frontmatter
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            content = parts[2].strip()

    logger.info(f"Content after frontmatter: {len(content)} characters")
    logger.info(f"Chunk size: {settings.chunk_size}, Overlap: {settings.chunk_overlap}")

    # Generate chunks
    chunks = list(chunk_text_generator(content, settings.chunk_size, settings.chunk_overlap))

    logger.info(f"\nTotal chunks generated: {len(chunks)}")
    logger.info(f"\nFirst 3 chunks:")
    for i, chunk in enumerate(chunks[:3]):
        logger.info(f"\nChunk {i+1} ({len(chunk)} chars):")
        logger.info(f"  {chunk[:100]}...")

    if len(chunks) > 100:
        logger.error(f"\n!!! BUG DETECTED: Generated {len(chunks)} chunks from {len(content)} chars!")
        logger.error(f"This should be about {len(content) // settings.chunk_size + 1} chunks")

if __name__ == "__main__":
    main()
