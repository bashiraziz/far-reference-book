"""Check what collections exist in Qdrant."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.services.vector_store import VectorStoreService
from backend.config.settings import settings

def main():
    """List all Qdrant collections."""
    print("=== Checking Qdrant Collections ===\n")
    print(f"Qdrant URL: {settings.qdrant_url}\n")

    try:
        client = VectorStoreService.get_client()
        collections = client.get_collections().collections

        print(f"Found {len(collections)} collection(s):\n")

        for collection in collections:
            print(f"  - {collection.name}")

            # Get collection info
            info = client.get_collection(collection.name)
            print(f"    Vectors: {info.points_count}")
            print(f"    Vector size: {info.config.params.vectors.size}")
            print()

        # Check which collection the app is configured to use
        print("="*60)
        print(f"Current app configuration:")
        print(f"  QDRANT_COLLECTION_NAME = {settings.qdrant_collection_name}")
        print()

        # Check if configured collection exists
        collection_names = [c.name for c in collections]
        if settings.qdrant_collection_name in collection_names:
            print(f"[SUCCESS] Collection '{settings.qdrant_collection_name}' EXISTS")
        else:
            print(f"[FAIL] Collection '{settings.qdrant_collection_name}' DOES NOT EXIST")
            print(f"\nAvailable collections: {', '.join(collection_names)}")

    except Exception as e:
        print(f"[FAIL] Error connecting to Qdrant: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
