"""
Script to populate Qdrant vector database with FAR content.

Reads FAR markdown files, chunks them, generates embeddings, and uploads to Qdrant.
"""

import asyncio
import sys
from pathlib import Path
from typing import List, Dict, Any
import re
from uuid import uuid4

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from qdrant_client.models import PointStruct

from backend.services.vector_store import VectorStoreService
from backend.services.embeddings import EmbeddingsService
from backend.services.text_chunker import TextChunker
from backend.config.settings import settings
from backend.config.logging import logger


def extract_metadata_from_path(file_path: Path) -> Dict[str, Any]:
    """
    Extract metadata from file path.

    Args:
        file_path: Path to markdown file

    Returns:
        Dictionary with chapter, section, and other metadata
    """
    # Extract chapter from parent directory (part-1, part-2, part-3)
    parent_dir = file_path.parent.name
    chapter_match = re.search(r'part[-_](\d+)', parent_dir)
    chapter = int(chapter_match.group(1)) if chapter_match else 1

    # Extract section from filename (e.g., "1.101.md" -> "1.101")
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

        # Remove frontmatter if present
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                content = parts[2].strip()

        return content
    except Exception as e:
        logger.error(f"Error reading {file_path}: {e}")
        return ""


def process_documents(docs_dir: Path) -> List[Dict[str, Any]]:
    """
    Process all markdown files in docs directory.

    Args:
        docs_dir: Path to docs directory containing FAR parts

    Returns:
        List of processed chunks with metadata
    """
    chunks_with_metadata = []

    # Find all markdown files in part-1, part-2, part-3 directories
    for part_dir in ['part-1', 'part-2', 'part-3']:
        part_path = docs_dir / part_dir

        if not part_path.exists():
            logger.warning(f"Directory not found: {part_path}")
            continue

        logger.info(f"Processing {part_dir}...")

        md_files = sorted(part_path.glob('*.md'))

        for md_file in md_files:
            # Read content
            content = read_markdown_file(md_file)

            if not content:
                continue

            # Extract metadata
            metadata = extract_metadata_from_path(md_file)

            # Chunk the content
            chunks = TextChunker.chunk_text(content)

            # Add chunks with metadata
            for i, chunk in enumerate(chunks):
                chunks_with_metadata.append({
                    "text": chunk,
                    "metadata": {
                        **metadata,
                        "chunk_index": i,
                        "total_chunks": len(chunks)
                    }
                })

        logger.info(f"  Found {len(md_files)} files")

    return chunks_with_metadata


async def upload_to_qdrant(chunks_with_metadata: List[Dict[str, Any]]):
    """
    Generate embeddings and upload to Qdrant.

    Args:
        chunks_with_metadata: List of chunks with metadata
    """
    logger.info(f"Generating embeddings for {len(chunks_with_metadata)} chunks...")

    # Process in batches to avoid overwhelming the API
    batch_size = 50
    points = []
    failed_chunks = []

    for i in range(0, len(chunks_with_metadata), batch_size):
        batch = chunks_with_metadata[i:i + batch_size]
        batch_texts = [chunk["text"] for chunk in batch]

        try:
            # Generate embeddings for batch
            embeddings = EmbeddingsService.generate_embeddings_batch(batch_texts)

            # Create points
            for chunk, embedding in zip(batch, embeddings):
                point = PointStruct(
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
                points.append(point)

            logger.info(f"  Processed batch {i//batch_size + 1}/{(len(chunks_with_metadata) + batch_size - 1)//batch_size}")

        except Exception as e:
            logger.error(f"Error processing batch {i//batch_size + 1}: {e}")
            failed_chunks.extend(batch)

    if points:
        logger.info(f"Uploading {len(points)} points to Qdrant...")
        VectorStoreService.upsert_points(points)
        logger.info("✓ Upload complete!")

    if failed_chunks:
        logger.warning(f"⚠ {len(failed_chunks)} chunks failed to process")

    return len(points), len(failed_chunks)


async def main():
    """Main execution function."""
    logger.info("=== FAR Vector Database Population ===\n")

    # Get docs directory
    project_root = Path(__file__).parent.parent.parent
    docs_dir = project_root / "docs"

    if not docs_dir.exists():
        logger.error(f"Docs directory not found: {docs_dir}")
        return

    # Ensure collection exists
    logger.info("Creating Qdrant collection (if not exists)...")
    VectorStoreService.create_collection()

    # Process documents
    logger.info("\nProcessing FAR documents...")
    chunks_with_metadata = process_documents(docs_dir)

    if not chunks_with_metadata:
        logger.error("No chunks found to process!")
        return

    logger.info(f"Total chunks to process: {len(chunks_with_metadata)}\n")

    # Upload to Qdrant
    success_count, fail_count = await upload_to_qdrant(chunks_with_metadata)

    logger.info(f"\n=== Summary ===")
    logger.info(f"Successfully processed: {success_count} chunks")
    logger.info(f"Failed: {fail_count} chunks")


if __name__ == "__main__":
    asyncio.run(main())
