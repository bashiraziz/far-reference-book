"""
Vector store service using Qdrant Cloud.

Handles storage and retrieval of embedded FAR content.
"""

from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
)

from backend.config.settings import settings
from backend.config.logging import logger


class VectorStoreService:
    """Manages Qdrant vector database operations."""

    _client: Optional[QdrantClient] = None

    @classmethod
    def get_client(cls) -> QdrantClient:
        """Get or create Qdrant client."""
        if cls._client is None:
            cls._client = QdrantClient(
                url=settings.qdrant_url,
                api_key=settings.qdrant_api_key,
            )
            logger.info("Qdrant client initialized")
        return cls._client

    @classmethod
    def create_collection(cls, collection_name: str = None):
        """
        Create a new collection in Qdrant.

        Args:
            collection_name: Name of collection (default from settings)
        """
        if collection_name is None:
            collection_name = settings.qdrant_collection_name

        client = cls.get_client()

        # Check if collection exists
        collections = client.get_collections().collections
        exists = any(c.name == collection_name for c in collections)

        if exists:
            logger.info(f"Collection '{collection_name}' already exists")
        else:
            # Create collection
            client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=settings.embedding_dimensions,
                    distance=Distance.COSINE
                )
            )
            logger.info(f"Created collection '{collection_name}'")

        # Ensure useful payload indexes exist
        cls.ensure_payload_indexes(collection_name)

    @classmethod
    def ensure_payload_indexes(cls, collection_name: Optional[str] = None):
        """Create payload indexes needed for filtering."""
        if collection_name is None:
            collection_name = settings.qdrant_collection_name

        client = cls.get_client()
        for field_name, schema in [("file", "keyword"), ("section", "keyword")]:
            try:
                client.create_payload_index(
                    collection_name=collection_name,
                    field_name=field_name,
                    field_schema=schema,
                )
                logger.info(f"Created payload index for '{field_name}'")
            except Exception as exc:
                message = str(exc)
                if "already exists" not in message:
                    logger.warning(
                        f"Failed to create payload index for '{field_name}': {message}"
                    )

    @classmethod
    def upsert_points(
        cls,
        points: List[PointStruct],
        collection_name: str = None
    ):
        """
        Upsert points (vectors with payloads) into collection.

        Args:
            points: List of PointStruct objects
            collection_name: Target collection (default from settings)
        """
        if collection_name is None:
            collection_name = settings.qdrant_collection_name

        client = cls.get_client()
        client.upsert(
            collection_name=collection_name,
            points=points
        )

    @classmethod
    def search(
        cls,
        query_vector: List[float],
        limit: int = 5,
        chapter_filter: Optional[int] = None,
        file_name: Optional[str] = None,
        score_threshold: float = 0.5,
        collection_name: str = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors.

        Args:
            query_vector: Query embedding
            limit: Maximum number of results
            chapter_filter: Optional chapter number filter (1-3)
            file_name: Optional FAR section file name filter (e.g., "1.102-1")
            score_threshold: Minimum similarity score
            collection_name: Target collection (default from settings)

        Returns:
            List of search results with scores and payloads
        """
        if collection_name is None:
            collection_name = settings.qdrant_collection_name

        client = cls.get_client()

        # Build filter if chapter or file specified
        must_conditions = []
        if chapter_filter is not None:
            must_conditions.append(
                FieldCondition(
                    key="chapter",
                    match=MatchValue(value=chapter_filter)
                )
            )
        if file_name:
            cls.ensure_payload_indexes(collection_name)
            normalized = file_name if file_name.endswith(".md") else f"{file_name}.md"
            must_conditions.append(
                FieldCondition(
                    key="file",
                    match=MatchValue(value=normalized)
                )
            )

        query_filter = Filter(must=must_conditions) if must_conditions else None

        # Search using query_points (newer Qdrant API)
        results = client.query_points(
            collection_name=collection_name,
            query=query_vector,
            limit=limit,
            query_filter=query_filter,
            score_threshold=score_threshold
        ).points

        # Format results
        formatted_results = []
        for result in results:
            formatted_results.append({
                "id": result.id,
                "score": result.score,
                "payload": result.payload
            })

        return formatted_results

    @classmethod
    def delete_collection(cls, collection_name: str = None):
        """
        Delete a collection.

        Args:
            collection_name: Collection to delete (default from settings)
        """
        if collection_name is None:
            collection_name = settings.qdrant_collection_name

        client = cls.get_client()
        client.delete_collection(collection_name=collection_name)
        logger.info(f"Deleted collection '{collection_name}'")
