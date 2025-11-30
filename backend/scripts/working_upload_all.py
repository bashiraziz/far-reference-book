"""Working upload script for ALL FAR parts (1-25)"""
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

print("=" * 60)
print("FAR Vector Database Population (Parts 1-25)")
print("=" * 60)

# Load environment
load_dotenv(Path(__file__).parent.parent / '.env')

# Initialize clients
print("\n1. Initializing clients...")
openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
qdrant_client = QdrantClient(
    url=os.getenv('QDRANT_URL'),
    api_key=os.getenv('QDRANT_API_KEY')
)
print("   [OK] OpenAI and Qdrant clients ready")

# Create/verify collection
print("\n2. Setting up collection...")
try:
    qdrant_client.get_collection('far_content')
    print("   [OK] Collection 'far_content' exists")
except:
    qdrant_client.create_collection(
        collection_name='far_content',
        vectors_config=VectorParams(size=512, distance=Distance.COSINE)
    )
    print("   [OK] Collection 'far_content' created (512 dimensions)")

# Get all files from parts 1-25
print("\n3. Scanning for FAR documents...")
docs_dir = Path(__file__).parent.parent.parent / 'docs'
all_files = []
for part_num in range(1, 26):
    part_dir = docs_dir / f'part-{part_num}'
    if part_dir.exists():
        files = sorted(part_dir.glob('*.md'))
        all_files.extend(files)
        print(f"   Part {part_num:2d}: {len(files):3d} files")

print(f"\n   Total: {len(all_files)} files to process")

# Process files
print("\n4. Processing and uploading...")
print(f"   Chunk size: 600 chars, Overlap: 150 chars")
print(f"   Batch size: 20 chunks per upload\n")

total_uploaded = 0
batch = []
BATCH_SIZE = 20

start_time = time.time()

for file_idx, file_path in enumerate(all_files, 1):
    try:
        # Read file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Remove frontmatter
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                content = parts[2].strip()

        if not content:
            continue

        # Extract metadata
        part_match = re.search(r'part-(\d+)', str(file_path.parent))
        chapter = int(part_match.group(1)) if part_match else 0

        # Chunk text
        chunks = []
        for i in range(0, len(content), 450):  # 600 size - 150 overlap
            chunk = content[i:i+600].strip()
            if chunk:
                chunks.append(chunk)

        # Add to batch
        for chunk in chunks:
            batch.append({
                'text': chunk,
                'chapter': chapter,
                'file': file_path.name
            })

            # Upload when batch is full
            if len(batch) >= BATCH_SIZE:
                # Generate embeddings
                texts = [item['text'] for item in batch]
                response = openai_client.embeddings.create(
                    model='text-embedding-3-small',
                    input=texts,
                    dimensions=512
                )
                embeddings = [item.embedding for item in sorted(response.data, key=lambda x: x.index)]

                # Create points
                points = [
                    PointStruct(
                        id=str(uuid4()),
                        vector=emb,
                        payload={
                            'text': item['text'],
                            'chapter': item['chapter'],
                            'file': item['file']
                        }
                    )
                    for item, emb in zip(batch, embeddings)
                ]

                # Upload
                qdrant_client.upsert(collection_name='far_content', points=points)
                total_uploaded += len(points)

                # Progress
                elapsed = time.time() - start_time
                rate = total_uploaded / elapsed if elapsed > 0 else 0
                print(f"   [{file_idx:3d}/{len(all_files)}] {file_path.name:30s} | {total_uploaded:6d} chunks | {rate:.1f}/sec")

                batch = []
                time.sleep(0.3)  # Rate limit

    except Exception as e:
        print(f"   ERROR on {file_path.name}: {e}")

# Upload remaining
if batch:
    texts = [item['text'] for item in batch]
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
        for item, emb in zip(batch, embeddings)
    ]
    qdrant_client.upsert(collection_name='far_content', points=points)
    total_uploaded += len(points)
    print(f"   Final batch: +{len(points)} chunks")

# Summary
elapsed = time.time() - start_time
info = qdrant_client.get_collection('far_content')
print("\n" + "=" * 60)
print("UPLOAD COMPLETE!")
print("=" * 60)
print(f"  Files processed: {len(all_files)}")
print(f"  Chunks uploaded: {total_uploaded}")
print(f"  Qdrant count:    {info.points_count}")
print(f"  Time elapsed:    {elapsed/60:.1f} minutes")
print(f"  Rate:            {total_uploaded/elapsed:.1f} chunks/sec")
print("=" * 60)
