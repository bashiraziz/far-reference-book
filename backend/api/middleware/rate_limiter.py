"""
Rate limiting middleware for API endpoints.

Implements simple in-memory rate limiting to control token usage.
"""

from typing import Dict, List
from datetime import datetime, timedelta
from fastapi import HTTPException, status


class RateLimiter:
    """Simple in-memory rate limiter."""

    def __init__(self):
        # Store: {conversation_id: [(timestamp, request_count), ...]}
        self._requests: Dict[str, List[datetime]] = {}

    def check_rate_limit(
        self,
        conversation_id: str,
        max_requests: int = 20,
        window_minutes: int = 60
    ) -> None:
        """
        Check if request is within rate limit.

        Args:
            conversation_id: Unique conversation identifier
            max_requests: Maximum requests allowed in time window
            window_minutes: Time window in minutes

        Raises:
            HTTPException: If rate limit exceeded
        """
        now = datetime.now()
        window_start = now - timedelta(minutes=window_minutes)

        # Get or create request history for this conversation
        if conversation_id not in self._requests:
            self._requests[conversation_id] = []

        # Clean up old requests outside the window
        self._requests[conversation_id] = [
            timestamp for timestamp in self._requests[conversation_id]
            if timestamp > window_start
        ]

        # Check if limit exceeded
        current_count = len(self._requests[conversation_id])

        if current_count >= max_requests:
            # Calculate when the limit will reset
            oldest_request = min(self._requests[conversation_id])
            reset_time = oldest_request + timedelta(minutes=window_minutes)
            minutes_until_reset = int((reset_time - now).total_seconds() / 60) + 1

            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "Rate limit exceeded",
                    "message": f"You've reached the limit of {max_requests} messages per {window_minutes} minutes. Please try again in {minutes_until_reset} minute(s).",
                    "retry_after_minutes": minutes_until_reset,
                    "limit": max_requests,
                    "window_minutes": window_minutes
                }
            )

        # Add current request
        self._requests[conversation_id].append(now)

    def get_remaining_requests(
        self,
        conversation_id: str,
        max_requests: int = 20,
        window_minutes: int = 60
    ) -> int:
        """
        Get number of remaining requests in current window.

        Args:
            conversation_id: Unique conversation identifier
            max_requests: Maximum requests allowed
            window_minutes: Time window in minutes

        Returns:
            Number of remaining requests
        """
        now = datetime.now()
        window_start = now - timedelta(minutes=window_minutes)

        if conversation_id not in self._requests:
            return max_requests

        # Count requests in current window
        recent_requests = [
            timestamp for timestamp in self._requests[conversation_id]
            if timestamp > window_start
        ]

        return max(0, max_requests - len(recent_requests))


# Global rate limiter instance
rate_limiter = RateLimiter()
