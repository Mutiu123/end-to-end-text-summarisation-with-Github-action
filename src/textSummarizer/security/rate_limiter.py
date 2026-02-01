"""
Token bucket rate limiter implementation.
Limits requests per client IP to prevent abuse.
"""

import time
from collections import defaultdict
from typing import Dict, Tuple

from fastapi import HTTPException, Request, status


class TokenBucketRateLimiter:
    """Rate limiter using the token bucket algorithm.

    Each client IP gets a bucket that fills with tokens at a fixed rate.
    Each request consumes one token. When the bucket is empty, requests
    are rejected until tokens replenish.
    """

    def __init__(self, max_tokens: int = 100, window_seconds: int = 60):
        """Initialize the rate limiter.

        Args:
            max_tokens: Maximum number of tokens (requests) per window.
            window_seconds: Time window in seconds for token replenishment.
        """
        self.max_tokens = max_tokens
        self.window_seconds = window_seconds
        self.refill_rate = max_tokens / window_seconds
        self._buckets: Dict[str, Tuple[float, float]] = defaultdict(
            lambda: (float(max_tokens), time.monotonic())
        )

    def _get_client_key(self, request: Request) -> str:
        """Extract client identifier from request.

        Args:
            request: The incoming FastAPI request.

        Returns:
            Client IP address as string.
        """
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    def _refill(self, tokens: float, last_time: float) -> Tuple[float, float]:
        """Calculate refilled tokens based on elapsed time.

        Args:
            tokens: Current token count.
            last_time: Timestamp of last refill.

        Returns:
            Tuple of (new_token_count, current_time).
        """
        now = time.monotonic()
        elapsed = now - last_time
        new_tokens = min(self.max_tokens, tokens + elapsed * self.refill_rate)
        return new_tokens, now

    def check(self, request: Request) -> bool:
        """Check if a request is allowed under the rate limit.

        Args:
            request: The incoming FastAPI request.

        Returns:
            True if the request is allowed.

        Raises:
            HTTPException: If rate limit is exceeded.
        """
        client_key = self._get_client_key(request)
        tokens, last_time = self._buckets[client_key]
        tokens, last_time = self._refill(tokens, last_time)

        if tokens < 1:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later.",
                headers={"Retry-After": str(int(self.window_seconds))},
            )

        self._buckets[client_key] = (tokens - 1, last_time)
        return True

    def reset(self) -> None:
        """Reset all rate limit buckets."""
        self._buckets.clear()


rate_limiter: TokenBucketRateLimiter = None


def get_rate_limiter() -> TokenBucketRateLimiter:
    """Get the global rate limiter instance."""
    global rate_limiter
    if rate_limiter is None:
        from textSummarizer.config.settings import get_settings

        settings = get_settings()
        rate_limiter = TokenBucketRateLimiter(
            max_tokens=settings.RATE_LIMIT_REQUESTS,
            window_seconds=settings.RATE_LIMIT_WINDOW_SECONDS,
        )
    return rate_limiter
