"""Test Railway deployment to diagnose collection and search issues."""
import requests
import json

RAILWAY_URL = "https://far-reference-book-production.up.railway.app"

def test_health():
    """Test health endpoint."""
    print("=== Testing Health Endpoint ===")
    try:
        response = requests.get(f"{RAILWAY_URL}/health", timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.ok
    except Exception as e:
        print(f"[FAIL] Health check failed: {e}")
        return False

def test_conversation_create():
    """Test creating a conversation."""
    print("\n=== Testing Conversation Creation ===")
    try:
        response = requests.post(
            f"{RAILWAY_URL}/conversations",
            json={"title": "Test - Section 5.101 Query"},
            timeout=10
        )
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Conversation ID: {data.get('id')}")
        return data.get('id')
    except Exception as e:
        print(f"[FAIL] Failed to create conversation: {e}")
        return None

def test_section_query(conversation_id: str):
    """Test querying for Section 5.101."""
    print("\n=== Testing Section 5.101 Query ===")
    try:
        response = requests.post(
            f"{RAILWAY_URL}/chat/{conversation_id}/messages/simple",
            json={"content": "What is FAR Section 5.101?"},
            timeout=30
        )
        print(f"Status: {response.status_code}")

        if response.ok:
            data = response.json()
            assistant_msg = data.get('assistant_message', {})
            sources = assistant_msg.get('sources', [])

            print(f"\nAssistant Response: {assistant_msg.get('content', 'N/A')[:200]}...")
            print(f"\nSources returned ({len(sources)}):")
            for i, source in enumerate(sources, 1):
                section = source.get('section', 'N/A')
                score = source.get('relevance_score', 0)
                print(f"  {i}. Section {section} - {score:.2%} relevance")

            # Check if Section 5.101 is in results
            has_5_101 = any('5.101' in str(s.get('section', '')) for s in sources)
            if has_5_101:
                print("\n[SUCCESS] Section 5.101 FOUND in results!")
            else:
                print("\n[FAIL] Section 5.101 NOT in results (wrong collection or search issue)")

            return has_5_101
        else:
            print(f"[FAIL] Query failed: {response.text}")
            return False

    except Exception as e:
        print(f"[FAIL] Failed to query: {e}")
        return False

def main():
    """Run diagnostic tests."""
    print("Railway Deployment Diagnostic Test\n")
    print(f"Testing: {RAILWAY_URL}\n")

    # Test 1: Health check
    if not test_health():
        print("\n[FAIL] Health check failed - backend may be down")
        return

    # Test 2: Create conversation
    conversation_id = test_conversation_create()
    if not conversation_id:
        print("\n[FAIL] Could not create conversation")
        return

    # Test 3: Query Section 5.101
    success = test_section_query(conversation_id)

    # Summary
    print("\n" + "="*60)
    if success:
        print("[SUCCESS] DIAGNOSIS: Collection is correct (far_content_production)")
        print("   Section 5.101 found in search results")
    else:
        print("[FAIL] DIAGNOSIS: Likely using OLD collection (far_content)")
        print("   ACTION REQUIRED:")
        print("   1. Check Railway dashboard environment variables")
        print("   2. Ensure QDRANT_COLLECTION_NAME=far_content_production")
        print("   3. Trigger a new deployment if variable was just added")
    print("="*60)

if __name__ == "__main__":
    main()
