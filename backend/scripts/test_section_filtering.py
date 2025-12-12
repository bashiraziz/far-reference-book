"""
Quick test to verify section filtering in RAG service.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.services.rag_service import RAGService

# Test section-specific queries
queries = [
    "What is FAR 52.219-9?",
    "Explain FAR 15.404",
    "What does section 31.205-6 say?"
]

print("=" * 70)
print("TESTING RAG SERVICE SECTION FILTERING")
print("=" * 70)

for query in queries:
    print(f"\nQuery: '{query}'")
    print("-" * 70)

    # Call RAG service (which includes section filtering logic)
    retrieval = RAGService.retrieve_context(query=query, max_chunks=3)
    chunks = retrieval["chunks"]

    print(f"Fallback used: {retrieval['fallback_used']}")
    print(f"Found {len(chunks)} chunks:\n")

    for i, chunk in enumerate(chunks, 1):
        payload = chunk["payload"]
        print(f"  {i}. Part {payload['chapter']}, Section {payload['section']}")
        print(f"     Score: {chunk['score']:.4f}")
        preview = (payload.get('text') or payload.get('content', ''))[:80]
        print(f"     Preview: {preview}...")
        print()

print("=" * 70)
print("TEST COMPLETE")
print("=" * 70)
