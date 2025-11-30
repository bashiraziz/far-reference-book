"""Test RAG service directly"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from backend.services.rag_service import RAGService

try:
    print("Testing RAG service...")
    result = RAGService.process_query(
        query="What is FAR?",
        conversation_history=[],
        selected_text=None
    )
    print("Success!")
    print(f"Response: {result['content'][:200]}...")
    print(f"Sources: {len(result.get('sources', []))}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
