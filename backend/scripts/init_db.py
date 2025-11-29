"""
Database initialization script.

Creates the necessary tables for conversations and messages.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.services.database import DatabaseService
from backend.config.logging import logger


async def create_tables():
    """Create database tables."""

    # Create conversations table
    conversations_table = """
        CREATE TABLE IF NOT EXISTS conversations (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            metadata JSONB DEFAULT '{}'::jsonb
        );
    """

    # Create messages table
    messages_table = """
        CREATE TABLE IF NOT EXISTS messages (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
            role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
            content TEXT NOT NULL,
            selected_text TEXT,
            sources JSONB,
            token_count INTEGER,
            processing_time_ms INTEGER,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
    """

    # Create index on conversation_id for faster queries
    messages_index = """
        CREATE INDEX IF NOT EXISTS idx_messages_conversation_id
        ON messages(conversation_id);
    """

    # Create index on created_at for sorting
    messages_created_index = """
        CREATE INDEX IF NOT EXISTS idx_messages_created_at
        ON messages(created_at);
    """

    try:
        logger.info("Creating conversations table...")
        await DatabaseService.execute(conversations_table)

        logger.info("Creating messages table...")
        await DatabaseService.execute(messages_table)

        logger.info("Creating indexes...")
        await DatabaseService.execute(messages_index)
        await DatabaseService.execute(messages_created_index)

        logger.info("✓ Database tables created successfully!")

    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        raise
    finally:
        await DatabaseService.close_pool()


if __name__ == "__main__":
    asyncio.run(create_tables())
