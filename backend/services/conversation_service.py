"""
Conversation service for managing chat conversations and messages.

Handles CRUD operations for conversations and messages in PostgreSQL.
"""

from typing import List, Dict, Any, Optional
from uuid import UUID, uuid4
from datetime import datetime
import json

from backend.services.database import DatabaseService
from backend.config.logging import logger


class ConversationService:
    """Manages conversation and message persistence."""

    @classmethod
    async def create_conversation(
        cls,
        source: str = "unknown",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new conversation.

        Args:
            source: Source of conversation (e.g., 'web', 'api')
            metadata: Optional metadata dictionary

        Returns:
            Created conversation dictionary
        """
        conversation_id = uuid4()
        metadata_json = json.dumps(metadata) if metadata else '{}'

        query = """
            INSERT INTO conversations (id, metadata)
            VALUES ($1, $2)
            RETURNING id, created_at, updated_at, metadata
        """

        row = await DatabaseService.fetchrow(query, conversation_id, metadata_json)

        return {
            "id": str(row["id"]),  # Convert UUID to string
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
            "metadata": json.loads(row["metadata"]) if isinstance(row["metadata"], str) else row["metadata"]
        }

    @classmethod
    async def get_conversation(cls, conversation_id: UUID) -> Optional[Dict[str, Any]]:
        """
        Get a conversation by ID.

        Args:
            conversation_id: Conversation UUID

        Returns:
            Conversation dictionary or None if not found
        """
        query = """
            SELECT id, created_at, updated_at, metadata
            FROM conversations
            WHERE id = $1
        """

        row = await DatabaseService.fetchrow(query, conversation_id)

        if not row:
            return None

        return {
            "id": str(row["id"]),  # Convert UUID to string
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
            "metadata": json.loads(row["metadata"]) if isinstance(row["metadata"], str) else row["metadata"]
        }

    @classmethod
    async def create_message(
        cls,
        conversation_id: UUID,
        role: str,
        content: str,
        selected_text: Optional[str] = None,
        sources: Optional[List[Dict[str, Any]]] = None,
        token_count: Optional[int] = None,
        processing_time_ms: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Create a new message in a conversation.

        Args:
            conversation_id: Parent conversation UUID
            role: Message role ('user' or 'assistant')
            content: Message content
            selected_text: Optional selected text context
            sources: Optional list of source citations
            token_count: Optional token usage count
            processing_time_ms: Optional processing time in milliseconds

        Returns:
            Created message dictionary
        """
        message_id = uuid4()

        query = """
            INSERT INTO messages (
                id, conversation_id, role, content, selected_text,
                sources, token_count, processing_time_ms
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            RETURNING id, conversation_id, role, content, selected_text,
                      sources, token_count, processing_time_ms, created_at
        """

        row = await DatabaseService.fetchrow(
            query,
            message_id,
            conversation_id,
            role,
            content,
            selected_text,
            json.dumps(sources) if sources else None,  # Encode sources as JSON string
            token_count,
            processing_time_ms
        )

        return {
            "id": str(row["id"]),  # Convert UUID to string
            "conversation_id": str(row["conversation_id"]),  # Convert UUID to string
            "role": row["role"],
            "content": row["content"],
            "selected_text": row["selected_text"],
            "sources": json.loads(row["sources"]) if row["sources"] else None,  # Decode JSON string
            "token_count": row["token_count"],
            "processing_time_ms": row["processing_time_ms"],
            "created_at": row["created_at"]
        }

    @classmethod
    async def get_messages(
        cls,
        conversation_id: UUID,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all messages for a conversation.

        Args:
            conversation_id: Conversation UUID
            limit: Optional limit on number of messages

        Returns:
            List of message dictionaries
        """
        if limit:
            query = """
                SELECT id, conversation_id, role, content, selected_text,
                       sources, token_count, processing_time_ms, created_at
                FROM messages
                WHERE conversation_id = $1
                ORDER BY created_at ASC
                LIMIT $2
            """
            rows = await DatabaseService.fetch(query, conversation_id, limit)
        else:
            query = """
                SELECT id, conversation_id, role, content, selected_text,
                       sources, token_count, processing_time_ms, created_at
                FROM messages
                WHERE conversation_id = $1
                ORDER BY created_at ASC
            """
            rows = await DatabaseService.fetch(query, conversation_id)

        messages = []
        for row in rows:
            messages.append({
                "id": str(row["id"]),  # Convert UUID to string
                "conversation_id": str(row["conversation_id"]),  # Convert UUID to string
                "role": row["role"],
                "content": row["content"],
                "selected_text": row["selected_text"],
                "sources": json.loads(row["sources"]) if row["sources"] else None,  # Decode JSON string
                "token_count": row["token_count"],
                "processing_time_ms": row["processing_time_ms"],
                "created_at": row["created_at"]
            })

        return messages

    @classmethod
    async def get_conversation_history(
        cls,
        conversation_id: UUID,
        max_messages: int = 10
    ) -> List[Dict[str, str]]:
        """
        Get conversation history formatted for RAG context.

        Args:
            conversation_id: Conversation UUID
            max_messages: Maximum messages to retrieve

        Returns:
            List of {role, content} dictionaries
        """
        query = """
            SELECT role, content
            FROM messages
            WHERE conversation_id = $1
            ORDER BY created_at DESC
            LIMIT $2
        """

        rows = await DatabaseService.fetch(query, conversation_id, max_messages)

        # Reverse to get chronological order
        history = []
        for row in reversed(rows):
            history.append({
                "role": row["role"],
                "content": row["content"]
            })

        return history
