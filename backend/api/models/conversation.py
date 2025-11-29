"""
Conversation-related Pydantic models.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class CreateConversationRequest(BaseModel):
    """Request model for creating a conversation."""
    source: Optional[str] = "web"
    metadata: Optional[Dict[str, Any]] = None


class ConversationResponse(BaseModel):
    """Response model for conversation data."""
    id: str
    created_at: datetime
    updated_at: datetime
    metadata: Optional[Dict[str, Any]] = None
