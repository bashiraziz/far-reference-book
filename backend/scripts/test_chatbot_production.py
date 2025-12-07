"""Test chatbot functionality with production database."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.services.vector_store import VectorStoreService
from backend.services.embeddings import EmbeddingsService
from backend.config.settings import settings
from backend.config.logging import logger

def test_semantic_search(query: str, limit: int = 5):
    """Test semantic search with a query."""
    logger.info(f"\n{'='*60}")
    logger.info(f"Query: '{query}'")
    logger.info(f"{'='*60}")

    try:
        # Generate embedding for query
        query_embedding = EmbeddingsService.generate_embedding(query)

        # Search Qdrant using VectorStoreService
        results = VectorStoreService.search(
            query_vector=query_embedding,
            limit=limit,
            score_threshold=0.5
        )

        if not results:
            logger.warning("No results found!")
            return

        logger.info(f"\nFound {len(results)} results:\n")

        for i, result in enumerate(results, 1):
            logger.info(f"Result {i}:")
            logger.info(f"  Score: {result['score']:.4f}")
            logger.info(f"  Chapter: {result['payload'].get('chapter', 'N/A')}")
            logger.info(f"  Section: {result['payload'].get('section', 'N/A')}")
            logger.info(f"  Source: {result['payload'].get('source_file', 'N/A')}")
            logger.info(f"  Text preview: {result['payload'].get('text', '')[:150]}...")
            logger.info("")

    except Exception as e:
        logger.error(f"Search failed: {e}", exc_info=True)

def main():
    """Run test queries on production database."""
    logger.info("=== Testing Chatbot with Production Database ===\n")
    logger.info(f"Collection: {settings.qdrant_collection_name}")

    # Verify database status first
    try:
        client = VectorStoreService.get_client()
        info = client.get_collection(settings.qdrant_collection_name)
        logger.info(f"Total points: {info.points_count}")
        logger.info(f"Index status: {info.status}")
    except Exception as e:
        logger.error(f"Failed to get collection info: {e}")
        return

    # Test queries covering different parts
    test_queries = [
        # Part 30 - Cost Accounting Standards
        "What are the cost accounting standards requirements?",

        # Part 31 - Contract Cost Principles
        "What costs are allowable for government contracts?",

        # Part 42 - Contract Administration
        "How should contract administration be handled?",

        # Part 49 - Termination of Contracts
        "What happens when a contract is terminated for convenience?",

        # Part 52 - Solicitation Provisions and Contract Clauses
        "What contract clauses are required for government contracts?",
    ]

    for query in test_queries:
        test_semantic_search(query, limit=3)

    logger.info("\n=== Test Summary ===")
    logger.info("If you see relevant results above for each query, the chatbot is working correctly!")
    logger.info("Expected: Results should come from Parts 30-52 only")
    logger.info("No results from Parts 1-29 should appear (not loaded yet)")

if __name__ == "__main__":
    main()
