"""
Script to populate Qdrant vector database with FAR Parts 4-25.

Reads FAR markdown files, chunks them, generates embeddings, and uploads to Qdrant.
"""

import asyncio
import sys
from pathlib import Path
from typing import Dict, Any, List, Generator
import re
from uuid import uuid4
import time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from qdrant_client.models import PointStruct

from backend.services.vector_store import VectorStoreService
from backend.services.embeddings import EmbeddingsService
from backend.config.settings import settings
from backend.config.logging import logger

# Optimized for 1GB Qdrant free tier
INGEST_CHUNK_SIZE = settings.chunk_size  # Now 400 chars
INGEST_CHUNK_OVERLAP = settings.chunk_overlap  # Now 100 chars


def chunk_text_generator(
    text: str,
    chunk_size: int,
    chunk_overlap: int
) -> Generator[str, None, None]:
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


def extract_metadata_from_path(file_path: Path) -> Dict[str, Any]:
    """Extract metadata from file path."""
    parent_dir = file_path.parent.name
    chapter_match = re.search(r'part[-_](\d+)', parent_dir)
    chapter = int(chapter_match.group(1)) if chapter_match else 1
    section = file_path.stem
    return {
        "chapter": chapter,
        "section": section,
        "source_file": str(file_path)
    }


def read_markdown_file(file_path: Path) -> str:
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


def iter_document_chunks(docs_dir: Path, start_part: int = 4, end_part: int = 25) -> Generator[Dict[str, Any], None, None]:
    """Yield chunks lazily so we never hold everything in memory."""
    for part_num in range(start_part, end_part + 1):
        part_dir = docs_dir / f"part-{part_num}"
        if not part_dir.exists():
            logger.warning(f"Directory not found: {part_dir}")
            continue

        logger.info(f"Processing part-{part_num}...")
        md_files = sorted(part_dir.glob('*.md'))
        logger.info(f"  Found {len(md_files)} files")

        for md_file in md_files:
            content = read_markdown_file(md_file)
            if not content:
                continue

            metadata = extract_metadata_from_path(md_file)
            for i, chunk in enumerate(
                chunk_text_generator(content, INGEST_CHUNK_SIZE, INGEST_CHUNK_OVERLAP)
            ):
                yield {
                    "text": chunk,
                    "metadata": {
                        **metadata,
                        "chunk_index": i
                    }
                }


def _process_batch(batch: List[Dict[str, Any]]) -> tuple[int, int]:
    """Generate embeddings for a batch and upload immediately."""
    texts = [chunk["text"] for chunk in batch]
    try:
        embeddings = EmbeddingsService.generate_embeddings_batch(texts)
        # Add small delay to avoid rate limiting
        time.sleep(0.5)
    except Exception as e:
        logger.error(f"Embedding generation failed for batch: {e}")
        return 0, len(batch)

    points: List[PointStruct] = []
    for chunk, embedding in zip(batch, embeddings):
        try:
            points.append(
                PointStruct(
                    id=str(uuid4()),
                    vector=embedding,
                    payload={
                        "text": chunk["text"],
                        "chapter": chunk["metadata"]["chapter"],
                        "section": chunk["metadata"]["section"],
                        "chunk_index": chunk["metadata"]["chunk_index"],
                        "source_file": chunk["metadata"]["source_file"]
                    }
                )
            )
        except Exception as e:
            logger.error(f"Failed to build Qdrant point: {e}")

    if not points:
        return 0, len(batch)

    try:
        VectorStoreService.upsert_points(points)
        return len(points), len(batch) - len(points)
    except Exception as e:
        logger.error(f"Failed to upload batch to Qdrant: {e}")
        return 0, len(batch)


async def upload_to_qdrant(chunks_iter, batch_size: int = 50):
    """Stream chunks through embeddings/Qdrant without large memory usage."""
    logger.info("Streaming chunks to Qdrant...")

    success_count = 0
    fail_count = 0
    batch: List[Dict[str, Any]] = []
    batch_number = 1

    for chunk in chunks_iter:
        batch.append(chunk)
        if len(batch) >= batch_size:
            success, failed = _process_batch(batch)
            success_count += success
            fail_count += failed
            logger.info(f"  Uploaded batch {batch_number} ({success} succeeded, {failed} failed)")
            batch_number += 1
            batch = []

    if batch:
        success, failed = _process_batch(batch)
        success_count += success
        fail_count += failed
        logger.info(f"  Uploaded final batch ({success} succeeded, {failed} failed)")

    return success_count, fail_count


async def main():
    """Main execution function."""
    logger.info("=== FAR Vector Database Population (Parts 4-25) ===\n")

    project_root = Path(__file__).parent.parent.parent
    docs_dir = project_root / "docs"
    if not docs_dir.exists():
        logger.error(f"Docs directory not found: {docs_dir}")
        return

    logger.info("Ensuring Qdrant collection exists...")
    VectorStoreService.create_collection()

    logger.info("\nProcessing FAR documents (Parts 4-25)...")
    chunk_iterator = iter_document_chunks(docs_dir, start_part=4, end_part=25)

    success_count, fail_count = await upload_to_qdrant(chunk_iterator)

    logger.info("\n=== Summary ===")
    logger.info(f"Successfully processed: {success_count} chunks")
    logger.info(f"Failed: {fail_count} chunks")


if __name__ == "__main__":
    asyncio.run(main())
