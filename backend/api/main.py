"""
FastAPI application for FAR Reference Book chatbot.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config.settings import settings
from backend.config.logging import logger
from backend.services.database import DatabaseService

from backend.api.routes import health, conversations, chat


# Create FastAPI app
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(conversations.router)
app.include_router(chat.router)


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    logger.info("Starting FAR Reference Book API...")
    # Database pool will be created on first use
    logger.info("API started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down FAR Reference Book API...")
    await DatabaseService.close_pool()
    logger.info("API shutdown complete")
