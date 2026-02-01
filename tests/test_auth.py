"""
Tests for the JWT authentication module.
"""

import time
from unittest.mock import MagicMock

import jwt
import pytest
from fastapi import HTTPException

from textSummarizer.config.settings import Settings
from textSummarizer.security.auth import (
    create_access_token,
    validate_api_key,
    verify_token,
)


class TestAuthModule:
    """Test suite for authentication functions."""

    def test_create_access_token_success(self, test_settings: Settings):
        """Test successful JWT token creation."""
        data = {"sub": "testuser", "type": "access"}
        token = create_access_token(data, test_settings)

        assert isinstance(token, str)
        assert len(token) > 0

        # Decode to verify structure
        decoded = jwt.decode(
            token,
            test_settings.SECRET_KEY,
            algorithms=[test_settings.JWT_ALGORITHM]
        )
        assert decoded["sub"] == "testuser"
        assert decoded["type"] == "access"
        assert "exp" in decoded
        assert "iat" in decoded

    def test_create_access_token_with_expiration(self, test_settings: Settings):
        """Test that created tokens have correct expiration time."""
        data = {"sub": "testuser"}
        token = create_access_token(data, test_settings)

        decoded = jwt.decode(
            token,
            test_settings.SECRET_KEY,
            algorithms=[test_settings.JWT_ALGORITHM]
        )

        # Check expiration is approximately JWT_EXPIRATION_MINUTES in the future
        expected_exp = time.time() + (test_settings.JWT_EXPIRATION_MINUTES * 60)
        assert abs(decoded["exp"] - expected_exp) < 5  # Within 5 seconds

    def test_verify_token_success(self, test_settings: Settings):
        """Test successful token verification."""
        data = {"sub": "testuser", "role": "admin"}
        token = create_access_token(data, test_settings)

        payload = verify_token(token, test_settings)
        assert payload["sub"] == "testuser"
        assert payload["role"] == "admin"

    def test_verify_token_invalid(self, test_settings: Settings):
        """Test that invalid tokens raise HTTPException."""
        invalid_token = "invalid.token.string"

        with pytest.raises(HTTPException) as exc_info:
            verify_token(invalid_token, test_settings)

        assert exc_info.value.status_code == 401
        assert "Invalid token" in exc_info.value.detail

    def test_verify_token_expired(self, test_settings: Settings):
        """Test that expired tokens raise HTTPException."""
        # Create token with negative expiration (already expired)
        data = {"sub": "testuser"}
        expired_payload = {
            **data,
            "exp": time.time() - 100,  # 100 seconds ago
            "iat": time.time() - 200,
        }
        expired_token = jwt.encode(
            expired_payload,
            test_settings.SECRET_KEY,
            algorithm=test_settings.JWT_ALGORITHM
        )

        with pytest.raises(HTTPException) as exc_info:
            verify_token(expired_token, test_settings)

        assert exc_info.value.status_code == 401
        assert "expired" in exc_info.value.detail.lower()

    def test_verify_token_wrong_secret(self, test_settings: Settings):
        """Test that tokens signed with wrong secret are rejected."""
        data = {"sub": "testuser"}
        wrong_token = jwt.encode(
            {**data, "exp": time.time() + 3600, "iat": time.time()},
            "wrong-secret-key",
            algorithm=test_settings.JWT_ALGORITHM
        )

        with pytest.raises(HTTPException) as exc_info:
            verify_token(wrong_token, test_settings)

        assert exc_info.value.status_code == 401

    def test_validate_api_key_success(self, test_settings: Settings):
        """Test successful API key validation."""
        valid_key = "test-api-key-1"
        assert validate_api_key(valid_key, test_settings) is True

    def test_validate_api_key_invalid(self, test_settings: Settings):
        """Test invalid API key rejection."""
        invalid_key = "invalid-key"
        assert validate_api_key(invalid_key, test_settings) is False

    def test_validate_api_key_no_keys_configured(self):
        """Test that validation passes when no API keys are configured."""
        settings = Settings(API_KEYS="")
        assert validate_api_key("any-key", settings) is True

    def test_create_access_token_without_settings(self):
        """Test token creation uses default settings when not provided."""
        data = {"sub": "testuser"}
        token = create_access_token(data)

        assert isinstance(token, str)
        assert len(token) > 0
