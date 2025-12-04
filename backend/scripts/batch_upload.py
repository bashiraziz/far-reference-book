"""Batch upload - processes files in groups of 50 to avoid hanging"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Distance, VectorParams
from openai import OpenAI
from uuid import uuid4
import os
from dotenv import load_dotenv
import time
import re

# Configuration
START_FILE = int(sys.argv[1]) if len(sys.argv) > 1 else 0
BATCH_SIZE = int(sys.argv[2]) if len(sys.argv) > 2 else 50

print(f"Batch Upload - Starting from file {START_FILE}, processing {BATCH_SIZE} files")

# Load environment
load_dotenv(Path(__file__).parent.parent / '.env')

# Initialize clients
openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
qdrant_client = QdrantClient(
    url=os.getenv('QDRANT_URL'),
    api_key=os.getenv('QDRANT_API_KEY')
)

# Ensure collection exists
try:
    qdrant_client.get_collection('far_content')
    print("Collection exists")
except:
    qdrant_client.create_collection(
        collection_name='far_content',
        vectors_config=VectorParams(size=512, distance=Distance.COSINE)
    )
    print("Collection created")

# Get all files
docs_dir = Path(__file__).parent.parent.parent / 'docs'
all_files = []
for part_num in range(36, 41):
    part_dir = docs_dir / f'part-{part_num}'
    if part_dir.exists():
        all_files.extend(sorted(part_dir.glob('*.md')))

print(f"Total files: {len(all_files)}")
print(f"Processing files {START_FILE} to {min(START_FILE + BATCH_SIZE, len(all_files))}")

# Process batch
files_to_process = all_files[START_FILE:START_FILE + BATCH_SIZE]
total_uploaded = 0
chunk_batch = []

for idx, file_path in enumerate(files_to_process, START_FILE):
    # Read file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            content = parts[2].strip()

    if not content:
        continue

    # Extract metadata
    part_match = re.search(r'part-(\d+)', str(file_path.parent))
    chapter = int(part_match.group(1)) if part_match else 0

    # Chunk
    for i in range(0, len(content), 450):
        chunk = content[i:i+600].strip()
        if chunk:
            chunk_batch.append({
                'text': chunk,
                'chapter': chapter,
                'file': file_path.name
            })

    # Upload every 20 chunks
    if len(chunk_batch) >= 20:
        texts = [item['text'] for item in chunk_batch]
        response = openai_client.embeddings.create(
            model='text-embedding-3-small',
            input=texts,
            dimensions=512
        )
        embeddings = [item.embedding for item in sorted(response.data, key=lambda x: x.index)]

        points = [
            PointStruct(
                id=str(uuid4()),
                vector=emb,
                payload={'text': item['text'], 'chapter': item['chapter'], 'file': item['file']}
            )
            for item, emb in zip(chunk_batch, embeddings)
        ]

        qdrant_client.upsert(collection_name='far_content', points=points)
        total_uploaded += len(points)
        print(f"  File {idx}/{len(all_files)}: {file_path.name} | Total: {total_uploaded} chunks")

        chunk_batch = []
        time.sleep(0.3)

# Upload remaining
if chunk_batch:
    texts = [item['text'] for item in chunk_batch]
    response = openai_client.embeddings.create(
        model='text-embedding-3-small',
        input=texts,
        dimensions=512
    )
    embeddings = [item.embedding for item in sorted(response.data, key=lambda x: x.index)]
    points = [
        PointStruct(id=str(uuid4()), vector=emb, payload={'text': item['text'], 'chapter': item['chapter'], 'file': item['file']})
        for item, emb in zip(chunk_batch, embeddings)
    ]
    qdrant_client.upsert(collection_name='far_content', points=points)
    total_uploaded += len(points)

# Summary
info = qdrant_client.get_collection('far_content')
print(f"\nBatch complete! Uploaded {total_uploaded} chunks")
print(f"Total in collection: {info.points_count}")
print(f"\nNext command: python scripts/batch_upload.py {START_FILE + BATCH_SIZE} {BATCH_SIZE}")
