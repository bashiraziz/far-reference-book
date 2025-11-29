"""
Quick script to populate only Part 3 to avoid memory issues.
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
from backend.config.logging import logger


async def main():
    logger.info("=== Populating Part 3 Only ===")

    # Initialize services
    vector_store = VectorStoreService()
    embeddings = EmbeddingsService()

    # Collection already exists, skip creation
    logger.info("Using existing collection")

    # Process Part 3 files - use absolute path from project root
    project_root = Path(__file__).parent.parent.parent
    part3_dir = project_root / "data" / "far" / "processed" / "part_3"
    files = sorted(part3_dir.glob("*.md"))

    logger.info(f"Found {len(files)} Part 3 files")

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

        # Generate embedding for the whole document (they're small)
        embedding = embeddings.generate_embedding(content)

        # Create point
        point = PointStruct(
            id=str(uuid4()),
            vector=embedding,
            payload={
                "content": content,
                "chapter": 3,
                "section": section,
                "source_file": str(file_path)
            }
        )
        points.append(point)

        if len(points) % 10 == 0:
            logger.info(f"Processed {len(points)} documents...")

    # Upload in small batches to avoid timeout
    batch_size = 10
    for i in range(0, len(points), batch_size):
        batch = points[i:i+batch_size]
        vector_store.upsert_points(batch)  # Not async
        logger.info(f"Uploaded batch {i//batch_size + 1}/{(len(points)-1)//batch_size + 1} ({len(batch)} points)")

    logger.info(f"Successfully uploaded {len(points)} Part 3 documents!")


if __name__ == "__main__":
    from backend.config.settings import settings
    asyncio.run(main())
