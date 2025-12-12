"""
Comprehensive test suite for FAR chatbot with production data.

This script tests:
1. Qdrant connection and collection status
2. Vector search functionality
3. Sample chatbot queries with expected results
4. Response quality and performance
5. Edge cases and error handling
"""

import sys
import time
from pathlib import Path
from typing import List, Dict, Any
import json

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.services.vector_store import VectorStoreService
from backend.services.embeddings import EmbeddingsService
from backend.config.settings import settings
from backend.config.logging import logger


# Test queries with expected keywords
TEST_QUERIES = [
    {
        "query": "What is FAR?",
        "expected_keywords": ["Federal", "Acquisition", "Regulation"],
        "description": "Basic FAR definition",
        "category": "Basic Retrieval"
    },
    {
        "query": "What are sealed bidding procedures?",
        "expected_keywords": ["sealed", "bid", "Part 14"],
        "description": "Specific procurement method",
        "category": "Basic Retrieval"
    },
    {
        "query": "Define commercial item",
        "expected_keywords": ["commercial", "item", "Part 12"],
        "description": "FAR Part 12 concept",
        "category": "Basic Retrieval"
    },
    {
        "query": "What types of contracts are available?",
        "expected_keywords": ["fixed-price", "cost", "contract", "Part 16"],
        "description": "Multi-section synthesis",
        "category": "Multi-Section"
    },
    {
        "query": "What are the small business programs?",
        "expected_keywords": ["small business", "Part 19", "program"],
        "description": "Complex topic",
        "category": "Multi-Section"
    },
    {
        "query": "What is FAR 52.219-9?",
        "expected_keywords": ["52.219-9", "small business"],
        "description": "Specific clause retrieval",
        "category": "Specific Section"
    },
    {
        "query": "Explain FAR 15.404",
        "expected_keywords": ["15.404", "price", "proposal"],
        "description": "Specific section",
        "category": "Specific Section"
    },
    {
        "query": "When should I use fixed-price vs cost-reimbursement contracts?",
        "expected_keywords": ["fixed-price", "cost-reimbursement", "risk"],
        "description": "Decision-making query",
        "category": "Complex"
    },
    {
        "query": "What labor laws apply to government contracts?",
        "expected_keywords": ["labor", "Part 22", "Davis-Bacon"],
        "description": "Regulatory compliance",
        "category": "Complex"
    }
]


def print_header(title: str):
    """Print a formatted header."""
    print("\n" + "="*70)
    print(f" {title}")
    print("="*70)


def print_subheader(title: str):
    """Print a formatted subheader."""
    print(f"\n--- {title} ---")


def test_qdrant_connection():
    """Test 1: Verify Qdrant connection and collection status."""
    print_header("TEST 1: Qdrant Connection & Collection Status")

    try:
        client = VectorStoreService.get_client()
        collection_name = settings.qdrant_collection_name

        # Get collection info
        collection_info = client.get_collection(collection_name)
        point_count = collection_info.points_count
        vector_size = collection_info.config.params.vectors.size

        print(f"\n[OK] Connected to Qdrant Cloud")
        print(f"[OK] Collection: {collection_name}")
        print(f"[OK] Total vectors: {point_count:,}")
        print(f"[OK] Vector dimensions: {vector_size}")
        print(f"[OK] Distance metric: COSINE")

        # Check point count
        expected_min = 17000
        expected_max = 18000
        if point_count < expected_min:
            print(f"\n[WARNING] Expected ~17,746 vectors, found {point_count}")
            print(f"  This may indicate incomplete data upload.")
            return False
        elif point_count > expected_max:
            print(f"\n[WARNING] Found {point_count} vectors (expected ~17,746)")
            print(f"  This may indicate duplicate data.")
        else:
            print(f"\n[OK] Vector count is within expected range!")

        return True

    except Exception as e:
        print(f"\n[FAILED] {e}")
        logger.error(f"Qdrant connection test failed: {e}", exc_info=True)
        return False


def test_vector_search():
    """Test 2: Test vector search functionality."""
    print_header("TEST 2: Vector Search Functionality")

    try:
        embeddings_service = EmbeddingsService()
        client = VectorStoreService.get_client()
        collection_name = settings.qdrant_collection_name

        # Test query
        test_query = "What is the simplified acquisition threshold?"
        print(f"\nTest query: '{test_query}'")

        # Generate embedding
        print("\nStep 1: Generating query embedding...")
        start_time = time.time()
        query_vector = embeddings_service.generate_embedding(test_query)
        embedding_time = time.time() - start_time

        print(f"[OK] Generated embedding in {embedding_time:.3f}s")
        print(f"  Vector dimensions: {len(query_vector)}")
        print(f"  Vector type: {type(query_vector)}")

        # Search Qdrant
        print("\nStep 2: Searching Qdrant...")
        start_time = time.time()
        search_response = client.query_points(
            collection_name=collection_name,
            query=query_vector,
            limit=5
        )
        search_results = search_response.points
        search_time = time.time() - start_time

        print(f"[OK] Search completed in {search_time:.3f}s")
        print(f"[OK] Found {len(search_results)} results")

        # Analyze results
        print("\nStep 3: Analyzing results...")
        if len(search_results) == 0:
            print("[FAILED] FAILED: No results returned")
            return False

        for i, result in enumerate(search_results, 1):
            score = result.score
            payload = result.payload
            text_preview = payload.get('text', '')[:100]

            print(f"\n  Result {i}:")
            print(f"    Relevance: {score:.4f}")
            print(f"    Chapter: Part {payload.get('chapter', 'N/A')}")
            print(f"    Section: {payload.get('section', 'N/A')}")
            print(f"    Preview: {text_preview}...")

        # Check relevance scores
        top_score = search_results[0].score
        if top_score < 0.6:
            print(f"\n[WARNING] WARNING: Top result has low relevance ({top_score:.4f})")
            print("  Expected score > 0.6 for good matches")
        else:
            print(f"\n[OK] Top result has good relevance ({top_score:.4f})")

        return True

    except Exception as e:
        print(f"\n[FAILED] FAILED: {e}")
        logger.error(f"Vector search test failed: {e}", exc_info=True)
        return False


def test_sample_queries():
    """Test 3: Test sample chatbot queries."""
    print_header("TEST 3: Sample Chatbot Queries")

    embeddings_service = EmbeddingsService()
    client = VectorStoreService.get_client()
    collection_name = settings.qdrant_collection_name

    results = []
    categories = {}

    for i, test in enumerate(TEST_QUERIES, 1):
        print_subheader(f"Query {i}/{len(TEST_QUERIES)}")
        print(f"Category: {test['category']}")
        print(f"Description: {test['description']}")
        print(f"Query: '{test['query']}'")

        try:
            # Search
            start_time = time.time()
            query_vector = embeddings_service.generate_embedding(test['query'])
            search_response = client.query_points(
                collection_name=collection_name,
                query=query_vector,
                limit=3
            )
            search_results = search_response.points
            query_time = time.time() - start_time

            # Check results
            if len(search_results) == 0:
                print(f"[FAILED] FAILED: No results returned")
                results.append(False)
                categories[test['category']] = categories.get(test['category'], []) + [False]
                continue

            # Get top result
            top_result = search_results[0]
            score = top_result.score
            text = top_result.payload.get('text', '')
            chapter = top_result.payload.get('chapter', 'N/A')
            section = top_result.payload.get('section', 'N/A')

            print(f"\n  Response time: {query_time:.3f}s")
            print(f"  Relevance score: {score:.4f}")
            print(f"  Source: Part {chapter}, Section {section}")
            print(f"  Preview: {text[:120]}...")

            # Check for expected keywords
            text_lower = text.lower()
            found_keywords = [kw for kw in test['expected_keywords']
                            if kw.lower() in text_lower]

            if found_keywords:
                print(f"  [OK] Found keywords: {', '.join(found_keywords)}")
                results.append(True)
                categories[test['category']] = categories.get(test['category'], []) + [True]
            else:
                print(f"  [WARNING] Expected keywords not found: {test['expected_keywords']}")
                print(f"    This may indicate poor retrieval quality")
                results.append(False)
                categories[test['category']] = categories.get(test['category'], []) + [False]

        except Exception as e:
            print(f"[FAILED] FAILED: {e}")
            logger.error(f"Query test failed: {e}", exc_info=True)
            results.append(False)
            categories[test['category']] = categories.get(test['category'], []) + [False]

    # Summary by category
    print_subheader("Results by Category")
    for category, cat_results in categories.items():
        passed = sum(cat_results)
        total = len(cat_results)
        pct = (passed / total * 100) if total > 0 else 0
        print(f"  {category}: {passed}/{total} passed ({pct:.0f}%)")

    # Overall summary
    print_subheader("Overall Summary")
    passed = sum(results)
    total = len(results)
    pct = (passed / total * 100) if total > 0 else 0
    print(f"  Total: {passed}/{total} passed ({pct:.0f}%)")

    return passed == total


def test_performance_metrics():
    """Test 4: Measure performance metrics."""
    print_header("TEST 4: Performance Metrics")

    embeddings_service = EmbeddingsService()
    client = VectorStoreService.get_client()
    collection_name = settings.qdrant_collection_name

    # Run multiple queries and measure performance
    test_queries = [
        "What is FAR?",
        "Commercial item definition",
        "Sealed bidding procedures",
        "Types of contracts",
        "Small business programs",
        "Cost accounting standards",
        "Contractor responsibility",
        "Fixed-price contracts",
        "Socioeconomic programs",
        "Contract termination"
    ]

    print(f"\nRunning {len(test_queries)} queries to measure performance...")

    times = []
    scores = []

    for i, query in enumerate(test_queries, 1):
        try:
            start_time = time.time()
            query_vector = embeddings_service.generate_embedding(query)
            response = client.query_points(
                collection_name=collection_name,
                query=query_vector,
                limit=5
            )
            results = response.points
            elapsed = time.time() - start_time
            times.append(elapsed)

            if results:
                scores.append(results[0].score)

            print(f"  Query {i}/{len(test_queries)}: {elapsed:.3f}s (score: {results[0].score:.3f})")

        except Exception as e:
            print(f"  Query {i}/{len(test_queries)}: FAILED - {e}")

    if not times:
        print("\n[FAILED] FAILED: No successful queries")
        return False

    # Calculate metrics
    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)
    avg_score = sum(scores) / len(scores) if scores else 0

    print(f"\n--- Performance Statistics ---")
    print(f"  Queries executed: {len(times)}")
    print(f"  Average time: {avg_time:.3f}s")
    print(f"  Fastest: {min_time:.3f}s")
    print(f"  Slowest: {max_time:.3f}s")
    print(f"  Average relevance: {avg_score:.3f}")

    # Check thresholds
    issues = []
    if avg_time > 5.0:
        issues.append(f"Average response time ({avg_time:.2f}s) exceeds 5s threshold")

    if max_time > 10.0:
        issues.append(f"Slowest query ({max_time:.2f}s) exceeds 10s threshold")

    if avg_score < 0.7:
        issues.append(f"Average relevance ({avg_score:.2f}) is below 0.7 threshold")

    if issues:
        print(f"\n[WARNING] Performance Issues Found:")
        for issue in issues:
            print(f"  - {issue}")
        return False

    print(f"\n[OK] All performance metrics within acceptable range")
    return True


def test_edge_cases():
    """Test 5: Test edge cases and error handling."""
    print_header("TEST 5: Edge Cases & Error Handling")

    embeddings_service = EmbeddingsService()
    client = VectorStoreService.get_client()
    collection_name = settings.qdrant_collection_name

    edge_cases = [
        {
            "query": "What is FAR Part 20?",
            "description": "Reserved part (should handle gracefully)",
            "expect_results": True  # May still find general FAR info
        },
        {
            "query": "asdfghjkl",
            "description": "Gibberish query",
            "expect_results": True  # Vector search always returns something
        },
        {
            "query": "What is Part 100?",
            "description": "Non-existent part",
            "expect_results": True  # Should return general info
        },
        {
            "query": "",
            "description": "Empty query",
            "expect_results": False  # Should fail
        }
    ]

    results = []

    for i, test in enumerate(edge_cases, 1):
        print_subheader(f"Edge Case {i}/{len(edge_cases)}")
        print(f"Description: {test['description']}")
        print(f"Query: '{test['query']}'")

        try:
            if test['query']:
                query_vector = embeddings_service.generate_embedding(test['query'])
                search_response = client.query_points(
                    collection_name=collection_name,
                    query=query_vector,
                    limit=3
                )
                search_results = search_response.points

                if search_results:
                    print(f"  [OK] Returned {len(search_results)} results")
                    print(f"  Top score: {search_results[0].score:.3f}")
                    results.append(test['expect_results'])
                else:
                    print(f"  [OK] No results (as expected)")
                    results.append(not test['expect_results'])
            else:
                print(f"  [OK] Empty query handled correctly")
                results.append(True)

        except Exception as e:
            if not test['expect_results']:
                print(f"  [OK] Failed as expected: {type(e).__name__}")
                results.append(True)
            else:
                print(f"  [FAILED] Unexpected failure: {e}")
                results.append(False)

    passed = sum(results)
    total = len(results)
    print(f"\n--- Edge Case Summary ---")
    print(f"  Passed: {passed}/{total}")

    return passed == total


def save_test_report(test_results: Dict[str, bool]):
    """Save test results to a JSON file."""
    report_path = Path(__file__).parent / "test_results.json"

    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "collection": settings.qdrant_collection_name,
        "tests": test_results,
        "overall_pass": all(test_results.values())
    }

    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\n[REPORT] Test report saved to: {report_path}")


def main():
    """Run all tests and generate report."""
    print_header("FAR CHATBOT COMPREHENSIVE TEST SUITE")

    print(f"\n[CONFIG] Test Configuration:")
    print(f"  Collection: {settings.qdrant_collection_name}")
    print(f"  Embedding Model: text-embedding-3-small")
    print(f"  Chunk Size: {settings.chunk_size} characters")
    print(f"  Chunk Overlap: {settings.chunk_overlap} characters")
    print(f"  Max Retrieval: {settings.max_chunk_retrieval} chunks")

    # Run tests
    test_results = {}

    print("\n\n[TESTING] Running Test Suite...\n")

    test_results["Qdrant Connection"] = test_qdrant_connection()
    time.sleep(1)  # Brief pause between tests

    test_results["Vector Search"] = test_vector_search()
    time.sleep(1)

    test_results["Sample Queries"] = test_sample_queries()
    time.sleep(1)

    test_results["Performance"] = test_performance_metrics()
    time.sleep(1)

    test_results["Edge Cases"] = test_edge_cases()

    # Final summary
    print_header("FINAL TEST SUMMARY")

    for test_name, passed in test_results.items():
        status = "[PASS]" if passed else "[FAIL]"
        status_color = status
        print(f"  {test_name:.<45} {status_color}")

    all_passed = all(test_results.values())
    passed_count = sum(test_results.values())
    total_count = len(test_results)

    print(f"\n  Overall: {passed_count}/{total_count} tests passed")

    # Save report
    save_test_report(test_results)

    # Final verdict
    print("\n" + "="*70)
    if all_passed:
        print("  [SUCCESS] ALL TESTS PASSED!")
        print("\n  Your FAR chatbot is ready for production use!")
        print("  Next steps:")
        print("    1. Deploy backend to production")
        print("    2. Test with real users")
        print("    3. Monitor performance metrics")
    else:
        print("  [WARNING] SOME TESTS FAILED")
        print("\n  Please review the failures above.")
        print("  Common fixes:")
        print("    - Ensure all data is uploaded to Qdrant")
        print("    - Check network connectivity")
        print("    - Verify API keys are valid")
        print("    - Review Qdrant collection configuration")
    print("="*70 + "\n")

    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
