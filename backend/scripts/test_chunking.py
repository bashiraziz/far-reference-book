"""
Test script to debug the chunking process.
"""

import sys
from pathlib import Path
import re

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.config.settings import settings
from backend.config.logging import logger

def chunk_text_generator(text, chunk_size, chunk_overlap):
    """Yield overlapping chunks without storing them all in memory."""
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

        start = end - chunk_overlap if end < text_length else end


def read_markdown_file(file_path):
    """Read content from markdown file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                content = parts[2].strip()
        return content
    except Exception as e:
        logger.error(f"Error reading {file_path}: {e}")
        return ""


def main():
    logger.info("=== Testing FAR Document Chunking ===\n")

    project_root = Path(__file__).parent.parent.parent
    docs_dir = project_root / "docs" / "part-1"

    if not docs_dir.exists():
        logger.error(f"Directory not found: {docs_dir}")
        return

    md_files = sorted(docs_dir.glob('*.md'))
    logger.info(f"Found {len(md_files)} files in part-1\n")

    total_chunks = 0
    for md_file in md_files[:5]:  # Test first 5 files only
        logger.info(f"Reading {md_file.name}...")
        content = read_markdown_file(md_file)

        if not content:
            logger.warning(f"  No content found")
            continue

        logger.info(f"  Content length: {len(content)} characters")

        chunk_count = 0
        for chunk in chunk_text_generator(content, settings.chunk_size, settings.chunk_overlap):
            chunk_count += 1
            total_chunks += 1

            if chunk_count <= 2:  # Show first 2 chunks
                logger.info(f"  Chunk {chunk_count}: {len(chunk)} chars - {chunk[:50]}...")

        logger.info(f"  Total chunks from this file: {chunk_count}\n")

    logger.info(f"=== Summary ===")
    logger.info(f"Processed {min(5, len(md_files))} files")
    logger.info(f"Generated {total_chunks} total chunks")


if __name__ == "__main__":
    main()
