"""Verify section 5.101 vectors can be retrieved and scored correctly."""
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
    """Verify 5.101 vectors."""
    logger.info("=== Verifying Section 5.101 Vectors ===\n")

    try:
        client = VectorStoreService.get_client()
        query = "method of dissemination of information"

        # Generate embedding
        logger.info(f"Query: '{query}'\n")
        embedding = EmbeddingsService.generate_embedding(query)

        # Get 5.101 chunks with filter
        logger.info("Step 1: Get section 5.101 chunks with filter...")
        filtered_results = client.query_points(
            collection_name=settings.qdrant_collection_name,
            query=embedding,
            query_filter=Filter(
                must=[FieldCondition(key='section', match=MatchValue(value='5.101'))]
            ),
            limit=3
        ).points

        logger.info(f"Got {len(filtered_results)} results\n")

        if filtered_results:
            # Get the best result
            best = filtered_results[0]
            logger.info(f"Best 5.101 result:")
            logger.info(f"  ID: {best.id}")
            logger.info(f"  Score: {best.score:.4f}")
            logger.info(f"  Section: {best.payload.get('section')}")
            logger.info(f"  Chunk: {best.payload.get('chunk_index')}")
            logger.info(f"  Text: {best.payload.get('text', '')[:100]}...")

            # Now retrieve this SAME point by ID
            logger.info(f"\nStep 2: Retrieve same point by ID...")
            point = client.retrieve(
                collection_name=settings.qdrant_collection_name,
                ids=[best.id],
                with_vectors=True
            )[0]

            logger.info(f"Retrieved point {point.id}")
            logger.info(f"  Has vector: {point.vector is not None}")
            if point.vector:
                logger.info(f"  Vector dimensions: {len(point.vector)}")

            # Manually compute cosine similarity
            if point.vector:
                import numpy as np
                vec1 = np.array(embedding)
                vec2 = np.array(point.vector)

                # Cosine similarity = dot product / (norm1 * norm2)
                dot_product = np.dot(vec1, vec2)
                norm1 = np.linalg.norm(vec1)
                norm2 = np.linalg.norm(vec2)
                manual_similarity = dot_product / (norm1 * norm2)

                logger.info(f"\nStep 3: Manual cosine similarity calculation:")
                logger.info(f"  Qdrant reported score: {best.score:.4f}")
                logger.info(f"  Manual calculation: {manual_similarity:.4f}")
                logger.info(f"  Difference: {abs(best.score - manual_similarity):.6f}")

                if abs(best.score - manual_similarity) < 0.001:
                    logger.info(f"  ✓ Scores match - vector is correct")
                else:
                    logger.warning(f"  ✗ Scores don't match - possible vector corruption")

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)

if __name__ == "__main__":
    main()
