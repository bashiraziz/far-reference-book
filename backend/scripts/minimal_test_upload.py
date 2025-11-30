"""Minimal test: upload just 5 files to verify the system works"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

print("Step 1: Imports...")
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Distance, VectorParams
from openai import OpenAI
from uuid import uuid4
import os
from dotenv import load_dotenv

print("Step 2: Load environment...")
load_dotenv(Path(__file__).parent.parent / '.env')

print("Step 3: Initialize clients...")
openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
qdrant_client = QdrantClient(
    url=os.getenv('QDRANT_URL'),
    api_key=os.getenv('QDRANT_API_KEY')
)

print("Step 4: Create/verify collection...")
try:
    qdrant_client.get_collection('far_content')
    print("   Collection exists")
except:
    qdrant_client.create_collection(
        collection_name='far_content',
        vectors_config=VectorParams(size=512, distance=Distance.COSINE)
    )
    print("   Collection created")

print("Step 5: Process 5 test files...")
docs_dir = Path(__file__).parent.parent.parent / 'docs' / 'part-1'
files = sorted(docs_dir.glob('*.md'))[:5]

total_uploaded = 0
for idx, file_path in enumerate(files, 1):
    print(f"  [{idx}/5] {file_path.name}")

    # Read file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            content = parts[2].strip()

    # Chunk (simple)
    chunks = [content[i:i+600] for i in range(0, len(content), 450)]
    chunks = [c.strip() for c in chunks if c.strip()]

    # Generate embeddings
    response = openai_client.embeddings.create(
        model='text-embedding-3-small',
        input=chunks,
        dimensions=512
    )
    embeddings = [item.embedding for item in sorted(response.data, key=lambda x: x.index)]

    # Create points
    points = [
        PointStruct(
            id=str(uuid4()),
            vector=emb,
            payload={'text': chunk, 'file': file_path.name}
        )
        for chunk, emb in zip(chunks, embeddings)
    ]

    # Upload
    qdrant_client.upsert(collection_name='far_content', points=points)
    total_uploaded += len(points)
    print(f"      Uploaded {len(points)} chunks (total: {total_uploaded})")

print(f"\nSUCCESS! Uploaded {total_uploaded} chunks from 5 files")

# Verify
info = qdrant_client.get_collection('far_content')
print(f"Final count: {info.points_count} points in collection")
