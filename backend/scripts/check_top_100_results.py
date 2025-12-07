"""Check top 100 results to see if 5.101 appears anywhere."""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.services.vector_store import VectorStoreService
from backend.services.embeddings import EmbeddingsService
from backend.config.settings import settings
from backend.config.logging import logger

def main():
    """Check top 100 results for the query."""
    logger.info("=== Checking Top 100 Results ===\n")

    try:
        query = "method of dissemination of information"
        logger.info(f"Query: '{query}'\n")

        # Generate embedding
        embedding = EmbeddingsService.generate_embedding(query)

        # Get top 100 results
        logger.info("Fetching top 100 results...")
        client = VectorStoreService.get_client()
        results = client.query_points(
            collection_name=settings.qdrant_collection_name,
            query=embedding,
            limit=100,
            score_threshold=0.0
        ).points

        logger.info(f"Retrieved {len(results)} results\n")

        # Find section 5.101 in results
        sections_found = {}
        section_5101_positions = []

        for i, result in enumerate(results, 1):
            section = result.payload.get('section', 'unknown')
            score = result.score

            if section not in sections_found:
                sections_found[section] = {'first_pos': i, 'best_score': score, 'count': 0}

            sections_found[section]['count'] += 1
            if score > sections_found[section]['best_score']:
                sections_found[section]['best_score'] = score

            if section == '5.101':
                section_5101_positions.append((i, score))

        logger.info(f"Total unique sections in top 100: {len(sections_found)}\n")

        # Show section 5.101 info
        if '5.101' in sections_found:
            info = sections_found['5.101']
            logger.info(f"✓ Section 5.101 FOUND in results!")
            logger.info(f"  First appearance: position {info['first_pos']}")
            logger.info(f"  Best score: {info['best_score']:.4f}")
            logger.info(f"  Total occurrences: {info['count']}")
            logger.info(f"  All positions: {section_5101_positions[:10]}")
        else:
            logger.warning(f"✗ Section 5.101 NOT in top 100 results")

        # Show top 10 sections
        logger.info(f"\nTop 10 sections by first appearance:")
        sorted_sections = sorted(sections_found.items(), key=lambda x: x[1]['first_pos'])
        for section, info in sorted_sections[:10]:
            logger.info(f"  {info['first_pos']:3d}. Section {section} (score: {info['best_score']:.4f}, count: {info['count']})")

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)

if __name__ == "__main__":
    main()
