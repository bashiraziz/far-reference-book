"""
Conversation management endpoints.
"""

from fastapi import APIRouter, HTTPException
from uuid import UUID
from typing import List

from backend.api.models.conversation import CreateConversationRequest, ConversationResponse
from backend.api.models.chat import MessageResponse
from backend.services.conversation_service import ConversationService

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.post("", response_model=ConversationResponse, status_code=201)
async def create_conversation(request: CreateConversationRequest):
    """
    Create a new conversation.

    Args:
        request: Conversation creation request

    Returns:
        Created conversation
    """
    conversation = await ConversationService.create_conversation(
        source=request.source or "web",
        metadata=request.metadata
    )
    return ConversationResponse(**conversation)


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(conversation_id: UUID):
    """
    Get a conversation by ID.

    Args:
        conversation_id: Conversation UUID

    Returns:
        Conversation data
    """
    conversation = await ConversationService.get_conversation(conversation_id)

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return ConversationResponse(**conversation)


@router.get("/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_messages(conversation_id: UUID, limit: int = 100):
    """
    Get all messages for a conversation.

    Args:
        conversation_id: Conversation UUID
        limit: Maximum number of messages to return

    Returns:
        List of messages
    """
    # Verify conversation exists
    conversation = await ConversationService.get_conversation(conversation_id)

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    messages = await ConversationService.get_messages(
        conversation_id=conversation_id,
        limit=limit
    )

    return [MessageResponse(**msg) for msg in messages]
