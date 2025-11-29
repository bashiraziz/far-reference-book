"""
Fast batch script to populate Parts 1 and 2.
Uses batch embedding API for efficiency.
"""

import sys
from pathlib import Path
from uuid import uuid4

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from qdrant_client.models import PointStruct
from backend.services.vector_store import VectorStoreService
from backend.services.embeddings import EmbeddingsService
from backend.services.text_chunker import TextChunker
from backend.config.logging import logger


def main():
    logger.info("=== Fast Populating Parts 1 and 2 ===")

    # Initialize services
    vector_store = VectorStoreService()
    embeddings = EmbeddingsService()

    logger.info("Using existing collection")

    # Get project root
    project_root = Path(__file__).parent.parent.parent

    # Collect all chunks first
    all_chunks = []

    for part_num in [1, 2]:
        part_dir = project_root / "data" / "far" / "processed" / f"part_{part_num}"

        if not part_dir.exists():
            logger.warning(f"Part {part_num} directory not found")
            continue

        files = sorted(part_dir.glob("*.md"))
        logger.info(f"Found {len(files)} Part {part_num} files")

        for file_path in files:
            content = file_path.read_text(encoding='utf-8')

            # Remove frontmatter
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    content = parts[2].strip()

            section = file_path.stem

            # Chunk large documents
            chunks = TextChunker.chunk_text(content, chunk_size=2000, chunk_overlap=200)
            if len(chunks) == 1:
                chunks = [content]

            for chunk_idx, chunk in enumerate(chunks):
                all_chunks.append({
                    "text": chunk,
                    "chapter": part_num,
                    "section": section,
                    "chunk_index": chunk_idx,
                    "total_chunks": len(chunks),
                    "source_file": str(file_path)
                })

    logger.info(f"Total chunks to process: {len(all_chunks)}")

    # Process in large batches
    batch_size = 50
    all_points = []

    for i in range(0, len(all_chunks), batch_size):
        batch = all_chunks[i:i+batch_size]
        texts = [c["text"] for c in batch]

        # Generate embeddings in batch
        logger.info(f"Generating embeddings for batch {i//batch_size + 1}/{(len(all_chunks)-1)//batch_size + 1}")
        embeddings_list = embeddings.generate_embeddings_batch(texts)

        # Create points
        for chunk_data, embedding in zip(batch, embeddings_list):
            point = PointStruct(
                id=str(uuid4()),
                vector=embedding,
                payload={
                    "content": chunk_data["text"],
                    "chapter": chunk_data["chapter"],
                    "section": chunk_data["section"],
                    "chunk_index": chunk_data["chunk_index"],
                    "total_chunks": chunk_data["total_chunks"],
                    "source_file": chunk_data["source_file"]
                }
            )
            all_points.append(point)

        # Upload this batch immediately
        if all_points:
            vector_store.upsert_points(all_points)
            logger.info(f"Uploaded {len(all_points)} points")
            all_points = []  # Clear for next batch

    logger.info(f"Complete! Processed {len(all_chunks)} chunks")


if __name__ == "__main__":
    from backend.config.settings import settings
    main()
