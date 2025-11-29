"""
Quick script to populate Parts 1 and 2 to complete the vector database.
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
from backend.config.logging import logger


async def main():
    logger.info("=== Populating Parts 1 and 2 ===")

    # Initialize services
    vector_store = VectorStoreService()
    embeddings = EmbeddingsService()

    # Collection already exists, skip creation
    logger.info("Using existing collection")

    # Get project root
    project_root = Path(__file__).parent.parent.parent

    # Process Part 1 and Part 2
    all_points = []

    for part_num in [1, 2]:
        part_dir = project_root / "data" / "far" / "processed" / f"part_{part_num}"

        if not part_dir.exists():
            logger.warning(f"Part {part_num} directory not found: {part_dir}")
            continue

        files = sorted(part_dir.glob("*.md"))
        logger.info(f"Found {len(files)} Part {part_num} files")

        points = []
        for file_path in files:
            content = file_path.read_text(encoding='utf-8')

            # Remove frontmatter
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    content = parts[2].strip()

            # Extract section from filename
            section = file_path.stem

            # Chunk the content if it's too large
            # Using a conservative chunk size of ~2000 chars (~500 tokens)
            chunks = TextChunker.chunk_text(content, chunk_size=2000, chunk_overlap=200)

            # If chunking results in only 1 chunk, use the whole content
            if len(chunks) == 1:
                chunks = [content]

            # Generate embeddings and create points for each chunk
            for chunk_idx, chunk in enumerate(chunks):
                embedding = embeddings.generate_embedding(chunk)

                # Create point
                point = PointStruct(
                    id=str(uuid4()),
                    vector=embedding,
                    payload={
                        "content": chunk,
                        "chapter": part_num,
                        "section": section,
                        "chunk_index": chunk_idx,
                        "total_chunks": len(chunks),
                        "source_file": str(file_path)
                    }
                )
                points.append(point)

            if len(points) % 10 == 0:
                logger.info(f"  Processed {len(points)} Part {part_num} documents...")

        # Upload in small batches to avoid timeout
        batch_size = 10
        for i in range(0, len(points), batch_size):
            batch = points[i:i+batch_size]
            vector_store.upsert_points(batch)
            logger.info(f"  Uploaded Part {part_num} batch {i//batch_size + 1}/{(len(points)-1)//batch_size + 1} ({len(batch)} points)")

        logger.info(f"Successfully uploaded {len(points)} Part {part_num} documents!")
        all_points.extend(points)

    logger.info(f"\n=== Complete ===")
    logger.info(f"Total documents uploaded: {len(all_points)}")


if __name__ == "__main__":
    from backend.config.settings import settings
    asyncio.run(main())
