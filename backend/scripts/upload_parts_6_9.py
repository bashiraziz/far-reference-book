"""Upload Parts 6-9 to Qdrant production database."""
import asyncio
import sys
from pathlib import Path
from typing import Dict, Any, List, Generator
import re
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from qdrant_client.models import PointStruct
from backend.services.vector_store import VectorStoreService
from backend.services.embeddings import EmbeddingsService
from backend.config.settings import settings
from backend.config.logging import logger

INGEST_CHUNK_SIZE = settings.chunk_size
INGEST_CHUNK_OVERLAP = settings.chunk_overlap


def chunk_text_generator(text: str, chunk_size: int, chunk_overlap: int) -> Generator[str, None, None]:
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

        chunk = text[start:end]
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


def read_markdown_file(md_file: Path) -> str:
    """Read markdown file and strip frontmatter."""
    try:
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Remove frontmatter (between --- markers)
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                content = parts[2].strip()

        return content
    except Exception as e:
        logger.error(f"Error reading {md_file}: {e}")
        return ""


def extract_metadata(md_file: Path) -> Dict[str, Any]:
    """Extract chapter and section from filename."""
    filename = md_file.stem
    match = re.match(r'(\d+)\.(\d+.*)', filename)

    if match:
        chapter = int(match.group(1))
        section = f"{match.group(1)}.{match.group(2)}"
        return {"chapter": chapter, "section": section}

    logger.warning(f"Could not parse filename: {filename}")
    return None


def iter_document_chunks(docs_dir: Path, start_part: int, end_part: int) -> Generator[Dict[str, Any], None, None]:
    """Yield chunks for multiple parts."""
    for part_num in range(start_part, end_part + 1):
        part_dir = docs_dir / f"part-{part_num}"
        if not part_dir.exists():
            logger.warning(f"Directory not found: {part_dir}")
            continue

        logger.info(f"Processing part-{part_num}...")
        md_files = sorted(part_dir.glob('*.md'))

        if len(md_files) == 0:
            logger.warning(f"  No markdown files found in part-{part_num}, skipping")
            continue

        logger.info(f"  Found {len(md_files)} files")

        for md_file in md_files:
            content = read_markdown_file(md_file)
            if not content:
                continue

            metadata = extract_metadata(md_file)
            if not metadata:
                continue

            chunk_index = 0
            for chunk_text in chunk_text_generator(content, INGEST_CHUNK_SIZE, INGEST_CHUNK_OVERLAP):
                yield {
                    "text": chunk_text,
                    "metadata": {
                        "chapter": metadata["chapter"],
                        "section": metadata["section"],
                        "chunk_index": chunk_index,
                        "source_file": str(md_file)
                    }
                }
                chunk_index += 1


def _process_batch(batch: List[Dict[str, Any]]):
    """Process a single batch: embed and upload."""
    texts = [chunk["text"] for chunk in batch]

    try:
        embeddings = EmbeddingsService.generate_embeddings_batch(texts)
    except Exception as e:
        logger.error(f"Failed to generate embeddings: {e}")
        return 0, len(batch)

    points = []
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
    """Upload Parts 6-9 to production database."""
    logger.info("=== Uploading Parts 6-9 to Production Database ===\n")

    project_root = Path(__file__).parent.parent.parent
    docs_dir = project_root / "docs"
    if not docs_dir.exists():
        logger.error(f"Docs directory not found: {docs_dir}")
        return

    logger.info(f"Collection: {settings.qdrant_collection_name}")
    logger.info(f"Chunk size: {INGEST_CHUNK_SIZE} chars")
    logger.info(f"Chunk overlap: {INGEST_CHUNK_OVERLAP} chars")
    logger.info("Note: Part 10 has no markdown files and will be skipped\n")

    chunk_iterator = iter_document_chunks(docs_dir, start_part=6, end_part=10)

    success_count, fail_count = await upload_to_qdrant(chunk_iterator)

    logger.info("\n=== Summary ===")
    logger.info(f"Successfully processed: {success_count} chunks")
    logger.info(f"Failed: {fail_count} chunks")


if __name__ == "__main__":
    asyncio.run(main())
