"""
Simple, direct upload script for FAR content to Qdrant.
Processes files one at a time with progress logging.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.services.vector_store import VectorStoreService
from backend.services.embeddings import EmbeddingsService
from backend.config.logging import logger
from qdrant_client.models import PointStruct
from uuid import uuid4
import time

def read_file(file_path):
    """Read markdown file, removing frontmatter."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            content = parts[2].strip()
    return content

def chunk_text(text, size=600, overlap=150):
    """Simple text chunking."""
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + size, len(text))
        chunks.append(text[start:end].strip())
        start = end - overlap
        if start >= len(text):
            break
    return [c for c in chunks if c]

def main():
    logger.info("=== Simple FAR Upload ===")

    # Create collection
    logger.info("Creating collection...")
    VectorStoreService.create_collection()

    # Get all markdown files from parts 1-3
    docs_dir = Path(__file__).parent.parent.parent / "docs"
    all_files = []
    for part in ['part-1', 'part-2', 'part-3']:
        part_dir = docs_dir / part
        if part_dir.exists():
            all_files.extend(sorted(part_dir.glob('*.md')))

    logger.info(f"Found {len(all_files)} files to process")

    total_uploaded = 0
    batch = []
    batch_size = 20  # Smaller batches

    for file_idx, md_file in enumerate(all_files, 1):
        logger.info(f"[{file_idx}/{len(all_files)}] Processing {md_file.name}")

        try:
            content = read_file(md_file)
            chunks = chunk_text(content)

            for chunk in chunks:
                batch.append({
                    'text': chunk,
                    'file': str(md_file.name)
                })

                # Upload when batch is full
                if len(batch) >= batch_size:
                    # Generate embeddings
                    texts = [item['text'] for item in batch]
                    embeddings = EmbeddingsService.generate_embeddings_batch(texts)

                    # Create points
                    points = [
                        PointStruct(
                            id=str(uuid4()),
                            vector=emb,
                            payload={'text': item['text'], 'file': item['file']}
                        )
                        for item, emb in zip(batch, embeddings)
                    ]

                    # Upload
                    VectorStoreService.upsert_points(points)
                    total_uploaded += len(points)
                    logger.info(f"  Uploaded batch: {len(points)} chunks (total: {total_uploaded})")

                    batch = []
                    time.sleep(0.5)  # Rate limit

        except Exception as e:
            logger.error(f"Error processing {md_file.name}: {e}")

    # Upload remaining
    if batch:
        texts = [item['text'] for item in batch]
        embeddings = EmbeddingsService.generate_embeddings_batch(texts)
        points = [
            PointStruct(
                id=str(uuid4()),
                vector=emb,
                payload={'text': item['text'], 'file': item['file']}
            )
            for item, emb in zip(batch, embeddings)
        ]
        VectorStoreService.upsert_points(points)
        total_uploaded += len(points)
        logger.info(f"Uploaded final batch: {len(points)} chunks")

    logger.info(f"=== COMPLETE: {total_uploaded} total chunks uploaded ===")

if __name__ == "__main__":
    main()
