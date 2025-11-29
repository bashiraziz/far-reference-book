"""
Chat endpoints for RAG-powered question answering.

Handles sending messages and receiving AI-generated responses with source citations.
"""

from fastapi import APIRouter, HTTPException
from uuid import UUID

from backend.api.models.chat import SendMessageRequest, ChatResponse, MessageResponse
from backend.services.conversation_service import ConversationService
from backend.services.rag_service import RAGService
from backend.api.middleware.rate_limiter import rate_limiter

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/{conversation_id}/messages/simple", status_code=201)
async def send_message_simple(conversation_id: UUID, request: SendMessageRequest):
    """
    Simplified endpoint that returns plain dicts instead of Pydantic models.
    Workaround for serialization issue.

    Rate limit: 20 messages per hour per conversation.
    """
    try:
        # Check rate limit (20 messages per hour)
        rate_limiter.check_rate_limit(
            conversation_id=str(conversation_id),
            max_requests=20,
            window_minutes=60
        )

        # Verify conversation exists
        conversation = await ConversationService.get_conversation(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        # Get conversation history for context
        history = await ConversationService.get_conversation_history(
            conversation_id=conversation_id,
            max_messages=6
        )

        # Format history for RAG service
        formatted_history = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in history
        ]

        # Store user message
        user_message = await ConversationService.create_message(
            conversation_id=conversation_id,
            role="user",
            content=request.content,
            selected_text=request.selected_text
        )

        # Process query with RAG
        rag_response = RAGService.process_query(
            query=request.content,
            conversation_history=formatted_history,
            selected_text=request.selected_text
        )

        # Store assistant message with sources
        assistant_message = await ConversationService.create_message(
            conversation_id=conversation_id,
            role="assistant",
            content=rag_response["content"],
            sources=rag_response["sources"],
            token_count=rag_response["token_count"],
            processing_time_ms=rag_response["processing_time_ms"]
        )

        # Convert datetime to ISO string for JSON serialization
        def serialize_message(msg):
            return {
                **msg,
                "created_at": msg["created_at"].isoformat() if msg.get("created_at") else None
            }

        # Return plain dicts
        return {
            "user_message": serialize_message(user_message),
            "assistant_message": serialize_message(assistant_message)
        }

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process message: {str(e)}"
        )


@router.post("/{conversation_id}/messages", response_model=ChatResponse, status_code=201)
async def send_message(conversation_id: UUID, request: SendMessageRequest):
    """
    Send a message and get AI response.

    This endpoint:
    1. Stores the user's message
    2. Retrieves relevant FAR content using RAG
    3. Generates AI response with OpenAI
    4. Stores the assistant's response with source citations
    5. Returns both messages

    Args:
        conversation_id: Conversation UUID
        request: Message request with content and optional selected_text

    Returns:
        Chat response with user message and assistant response
    """
    try:
        # Verify conversation exists
        conversation = await ConversationService.get_conversation(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        # Get conversation history for context
        history = await ConversationService.get_conversation_history(
            conversation_id=conversation_id,
            max_messages=6  # Last 3 exchanges
        )

        # Format history for RAG service
        formatted_history = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in history
        ]

        # Store user message
        user_message = await ConversationService.create_message(
            conversation_id=conversation_id,
            role="user",
            content=request.content,
            selected_text=request.selected_text
        )

        # Process query with RAG
        rag_response = RAGService.process_query(
            query=request.content,
            conversation_history=formatted_history,
            selected_text=request.selected_text
        )

        # Store assistant message with sources
        assistant_message = await ConversationService.create_message(
            conversation_id=conversation_id,
            role="assistant",
            content=rag_response["content"],
            sources=rag_response["sources"],
            token_count=rag_response["token_count"],
            processing_time_ms=rag_response["processing_time_ms"]
        )

        # Return both messages
        return ChatResponse(
            user_message=MessageResponse(**user_message),
            assistant_message=MessageResponse(**assistant_message)
        )

    except HTTPException:
        raise
    except Exception as e:
        # Log the error details
        import traceback
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=f"Failed to process message: {str(e)}"
        )
