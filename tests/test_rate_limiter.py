"""
Tests for the token bucket rate limiter.
"""

import time
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException, Request

from textSummarizer.security.rate_limiter import TokenBucketRateLimiter


class TestTokenBucketRateLimiter:
    """Test suite for TokenBucketRateLimiter class."""

    def test_allows_requests_within_limit(self):
        """Test that requests within the limit are allowed."""
        limiter = TokenBucketRateLimiter(max_tokens=5, window_seconds=60)
        request = self._create_mock_request("192.168.1.1")

        # Should allow 5 requests
        for _ in range(5):
            result = limiter.check(request)
            assert result is True

    def test_blocks_requests_exceeding_limit(self):
        """Test that requests exceeding the limit are blocked."""
        limiter = TokenBucketRateLimiter(max_tokens=3, window_seconds=60)
        request = self._create_mock_request("192.168.1.1")

        # First 3 requests should succeed
        for _ in range(3):
            limiter.check(request)

        # 4th request should fail
        with pytest.raises(HTTPException) as exc_info:
            limiter.check(request)

        assert exc_info.value.status_code == 429
        assert "Rate limit exceeded" in exc_info.value.detail
        assert "Retry-After" in exc_info.value.headers

    def test_refills_tokens_over_time(self):
        """Test that tokens refill at the correct rate over time."""
        limiter = TokenBucketRateLimiter(max_tokens=10, window_seconds=10)
        request = self._create_mock_request("192.168.1.1")

        # Use all tokens
        for _ in range(10):
            limiter.check(request)

        # Should fail immediately
        with pytest.raises(HTTPException):
            limiter.check(request)

        # Wait for 1 second to refill 1 token (rate = 10 tokens / 10 seconds = 1/second)
        time.sleep(1.1)

        # Should allow 1 request now
        result = limiter.check(request)
        assert result is True

        # Should fail again
        with pytest.raises(HTTPException):
            limiter.check(request)

    def test_reset_clears_all_buckets(self):
        """Test that reset method clears all rate limit buckets."""
        limiter = TokenBucketRateLimiter(max_tokens=2, window_seconds=60)
        request = self._create_mock_request("192.168.1.1")

        # Use all tokens
        for _ in range(2):
            limiter.check(request)

        # Should fail
        with pytest.raises(HTTPException):
            limiter.check(request)

        # Reset
        limiter.reset()

        # Should succeed after reset
        result = limiter.check(request)
        assert result is True

    def test_different_clients_have_separate_buckets(self):
        """Test that different client IPs have separate rate limit buckets."""
        limiter = TokenBucketRateLimiter(max_tokens=2, window_seconds=60)

        request1 = self._create_mock_request("192.168.1.1")
        request2 = self._create_mock_request("192.168.1.2")

        # Exhaust client 1's tokens
        for _ in range(2):
            limiter.check(request1)

        # Client 1 should be blocked
        with pytest.raises(HTTPException):
            limiter.check(request1)

        # Client 2 should still have tokens
        result = limiter.check(request2)
        assert result is True

    def test_x_forwarded_for_header_priority(self):
        """Test that X-Forwarded-For header takes priority for client identification."""
        limiter = TokenBucketRateLimiter(max_tokens=2, window_seconds=60)

        # Request with X-Forwarded-For header
        request = MagicMock(spec=Request)
        request.headers.get.return_value = "203.0.113.1, 198.51.100.1"
        request.client.host = "192.168.1.1"

        # Use tokens
        for _ in range(2):
            limiter.check(request)

        # Should be blocked (using X-Forwarded-For IP)
        with pytest.raises(HTTPException):
            limiter.check(request)

        # Different client should have tokens
        request2 = self._create_mock_request("192.168.1.1")
        result = limiter.check(request2)
        assert result is True

    def test_handles_missing_client_info(self):
        """Test that limiter handles requests with missing client info."""
        limiter = TokenBucketRateLimiter(max_tokens=2, window_seconds=60)

        request = MagicMock(spec=Request)
        request.headers.get.return_value = None
        request.client = None

        # Should use "unknown" as key
        result = limiter.check(request)
        assert result is True

    def _create_mock_request(self, client_ip: str) -> Request:
        """Helper method to create a mock request with specified client IP.

        Args:
            client_ip: The IP address to use for the mock client.

        Returns:
            Mocked Request object.
        """
        request = MagicMock(spec=Request)
        request.headers.get.return_value = None
        request.client.host = client_ip
        return request
