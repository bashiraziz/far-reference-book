"""Test searching for section 5.101 - Method of dissemination of information."""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.services.rag_service import RAGService
from backend.config.logging import logger

def main():
    """Test the exact user query that was failing."""
    logger.info("=== Testing Section 5.101 Query ===\n")

    query = "tell me about methods of dissemination of information"
    logger.info(f"Query: '{query}'\n")

    try:
        # Use the RAG service to search and generate response
        logger.info("Retrieving context from Qdrant (threshold=0.3)...")
        retrieval = RAGService.retrieve_context(
            query=query,
            max_chunks=5,
            score_threshold=0.3
        )
        context_chunks = retrieval["chunks"]
        logger.info(f"Fallback used: {retrieval['fallback_used']}")

        logger.info(f"\nRetrieved {len(context_chunks)} context chunks:")
        for i, chunk in enumerate(context_chunks, 1):
            payload = chunk.get('payload', {})
            logger.info(f"\n  Chunk {i}:")
            logger.info(f"    Chapter: {payload.get('chapter', 'N/A')}")
            logger.info(f"    Section: {payload.get('section', 'N/A')}")
            logger.info(f"    Score: {chunk.get('score', 'N/A')}")
            logger.info(f"    Text preview: {payload.get('text', '')[:150]}...")

        # Check if we found section 5.101
        has_5_101 = any(chunk.get('payload', {}).get('section') == '5.101' for chunk in context_chunks)
        logger.info(f"\nSection 5.101 found: {has_5_101}")

        if context_chunks:
            logger.info("\n" + "="*70)
            logger.info("Generating full RAG response...")
            logger.info("="*70 + "\n")

            response = RAGService.generate_response(
                query=query,
                context=RAGService.format_context(context_chunks)
            )

            logger.info("RESPONSE:")
            logger.info("-" * 70)
            logger.info(response)
            logger.info("-" * 70)
        else:
            logger.warning("\nNo context chunks retrieved - this is the original error!")

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)

if __name__ == "__main__":
    main()
