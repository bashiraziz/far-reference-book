"""Simplified Railway test to isolate the issue."""
import requests
import json

RAILWAY_URL = "https://far-reference-book-production.up.railway.app"

def test_health():
    """Test health endpoint."""
    print("=== Test 1: Health Check ===")
    try:
        response = requests.get(f"{RAILWAY_URL}/health", timeout=10)
        print(f"Status: {response.status_code}")
        if response.ok:
            print("[SUCCESS] Backend is running\n")
            return True
        else:
            print(f"[FAIL] Health check failed: {response.text}\n")
            return False
    except Exception as e:
        print(f"[FAIL] {e}\n")
        return False

def test_conversation():
    """Test conversation creation."""
    print("=== Test 2: Conversation Creation ===")
    try:
        response = requests.post(
            f"{RAILWAY_URL}/conversations",
            json={"title": "Simple Test"},
            timeout=10
        )
        print(f"Status: {response.status_code}")
        if response.ok:
            conv_id = response.json().get('id')
            print(f"[SUCCESS] Conversation created: {conv_id}\n")
            return conv_id
        else:
            print(f"[FAIL] {response.text}\n")
            return None
    except Exception as e:
        print(f"[FAIL] {e}\n")
        return None

def test_simple_message(conv_id):
    """Test sending a very simple message."""
    print("=== Test 3: Simple Message ===")
    print("Query: 'Hello'")
    try:
        response = requests.post(
            f"{RAILWAY_URL}/chat/{conv_id}/messages/simple",
            json={"content": "Hello"},
            timeout=60  # Longer timeout
        )
        print(f"Status: {response.status_code}")

        if response.ok:
            data = response.json()
            print("[SUCCESS] Message processed")
            print(f"Response length: {len(data.get('assistant_message', {}).get('content', ''))}")
            return True
        else:
            print(f"[FAIL] {response.status_code} - {response.text}")
            return False

    except requests.Timeout:
        print("[FAIL] Request timed out (>60s)")
        print("Possible causes: Qdrant timeout, OpenAI timeout, or backend hanging")
        return False
    except Exception as e:
        print(f"[FAIL] {e}")
        return False

def test_section_query(conv_id):
    """Test FAR section query."""
    print("\n=== Test 4: FAR Section Query ===")
    print("Query: 'What is FAR Section 5.101?'")
    try:
        response = requests.post(
            f"{RAILWAY_URL}/chat/{conv_id}/messages/simple",
            json={"content": "What is FAR Section 5.101?"},
            timeout=60
        )
        print(f"Status: {response.status_code}")

        if response.ok:
            data = response.json()
            sources = data.get('assistant_message', {}).get('sources', [])
            print(f"[SUCCESS] Query processed")
            print(f"Sources returned: {len(sources)}")
            for s in sources[:3]:
                print(f"  - Section {s.get('section')} ({s.get('relevance_score', 0):.2%})")
            return True
        else:
            print(f"[FAIL] {response.status_code} - {response.text}")
            return False

    except requests.Timeout:
        print("[FAIL] Request timed out (>60s)")
        return False
    except Exception as e:
        print(f"[FAIL] {e}")
        return False

def main():
    print("Railway Deployment - Simplified Test\n")
    print(f"Backend: {RAILWAY_URL}\n")

    # Test 1: Health
    if not test_health():
        print("\nBackend is down. Check Railway deployment status.")
        return

    # Test 2: Conversation
    conv_id = test_conversation()
    if not conv_id:
        print("\nCannot create conversations. Check database connection.")
        return

    # Test 3: Simple message
    if not test_simple_message(conv_id):
        print("\nBasic messaging failed. Check Railway logs for errors.")
        print("Likely causes:")
        print("  - Qdrant connection timeout")
        print("  - OpenAI API key issue")
        print("  - Backend memory/timeout")
        return

    # Test 4: Section query
    test_section_query(conv_id)

    print("\n" + "="*60)
    print("Test complete. Check Railway logs for detailed errors.")
    print("="*60)

if __name__ == "__main__":
    main()
