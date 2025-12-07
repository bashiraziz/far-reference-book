"""Compare similarity scores for sections 5.101 vs 5.102."""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from qdrant_client.models import Filter, FieldCondition, MatchValue
from backend.services.vector_store import VectorStoreService
from backend.services.embeddings import EmbeddingsService
from backend.config.settings import settings
from backend.config.logging import logger

def main():
    """Compare scores for 5.101 vs 5.102."""
    logger.info("=== Comparing Section 5.101 vs 5.102 Similarity Scores ===\n")

    try:
        client = VectorStoreService.get_client()

        # Generate embedding for the query
        query = "method of dissemination of information"
        logger.info(f"Query: '{query}'\n")
        embedding = EmbeddingsService.generate_embedding(query)

        # Search specifically for 5.101 chunks
        logger.info("Searching section 5.101 chunks...")
        results_5101 = client.query_points(
            collection_name=settings.qdrant_collection_name,
            query=embedding,
            query_filter=Filter(
                must=[
                    FieldCondition(
                        key='section',
                        match=MatchValue(value='5.101')
                    )
                ]
            ),
            limit=5
        ).points

        logger.info(f"Top 5 results from section 5.101:")
        for i, result in enumerate(results_5101, 1):
            logger.info(f"  {i}. Score: {result.score:.4f} | Chunk {result.payload.get('chunk_index')}: {result.payload.get('text', '')[:80]}...")

        # Search specifically for 5.102 chunks
        logger.info("\nSearching section 5.102 chunks...")
        results_5102 = client.query_points(
            collection_name=settings.qdrant_collection_name,
            query=embedding,
            query_filter=Filter(
                must=[
                    FieldCondition(
                        key='section',
                        match=MatchValue(value='5.102')
                    )
                ]
            ),
            limit=5
        ).points

        logger.info(f"Top 5 results from section 5.102:")
        for i, result in enumerate(results_5102, 1):
            logger.info(f"  {i}. Score: {result.score:.4f} | Chunk {result.payload.get('chunk_index')}: {result.payload.get('text', '')[:80]}...")

        # Compare best scores
        best_5101 = max([r.score for r in results_5101]) if results_5101 else 0
        best_5102 = max([r.score for r in results_5102]) if results_5102 else 0

        logger.info(f"\n=== Summary ===")
        logger.info(f"Best score from 5.101: {best_5101:.4f}")
        logger.info(f"Best score from 5.102: {best_5102:.4f}")
        logger.info(f"Difference: {abs(best_5101 - best_5102):.4f}")

        if best_5101 > 0.3:
            logger.info(f"\nSection 5.101 scores ABOVE 0.3 threshold - should be retrievable!")
        else:
            logger.info(f"\nSection 5.101 scores BELOW 0.3 threshold - this is why it's not retrieved")

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)

if __name__ == "__main__":
    main()
