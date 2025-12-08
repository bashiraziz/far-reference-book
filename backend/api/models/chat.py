"""
Chat-related Pydantic models.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class Source(BaseModel):
    """Source citation for a message."""
    chunk_id: str  # Changed from UUID to str
    chapter: int = Field(ge=1, le=53)  # FAR has 53 parts
    section: str
    page: Optional[int] = None
    relevance_score: float = Field(ge=0.0, le=1.0)
    excerpt: str  # Removed max_length constraint


class SendMessageRequest(BaseModel):
    """Request model for sending a chat message."""
    content: str = Field(min_length=1)
    selected_text: Optional[str] = None


class MessageResponse(BaseModel):
    """Response model for a single message."""
    id: str  # Changed from UUID to str
    conversation_id: str  # Changed from UUID to str
    role: str = Field(pattern="^(user|assistant)$")
    content: str
    selected_text: Optional[str] = None
    sources: Optional[List[Source]] = None
    token_count: Optional[int] = None
    processing_time_ms: Optional[int] = None
    created_at: datetime


class ChatResponse(BaseModel):
    """Response model for a chat interaction."""
    user_message: MessageResponse
    assistant_message: MessageResponse
