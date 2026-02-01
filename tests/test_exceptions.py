"""
Tests for custom exception classes and error handling.
"""

import pytest
from fastapi import status

from textSummarizer.exceptions import (
    AppException,
    AuthenticationError,
    DatabaseConnectionError,
    InputValidationError,
    ModelInferenceError,
    ModelNotFoundError,
    RateLimitError,
)


class TestExceptions:
    """Test suite for custom exception classes."""

    def test_app_exception_defaults(self):
        """Test AppException with default values."""
        exc = AppException()
        assert exc.message == "An unexpected error occurred"
        assert exc.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert exc.detail == {}
        assert str(exc) == exc.message

    def test_app_exception_custom_values(self):
        """Test AppException with custom values."""
        detail = {"error_type": "custom_error", "field": "username"}
        exc = AppException(
            message="Custom error message",
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )
        assert exc.message == "Custom error message"
        assert exc.status_code == 400
        assert exc.detail == detail

    def test_model_not_found_error(self):
        """Test ModelNotFoundError exception."""
        exc = ModelNotFoundError("/path/to/model")
        assert "Model not found at path: /path/to/model" in exc.message
        assert exc.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert exc.detail["error_type"] == "model_not_found"
        assert exc.detail["model_path"] == "/path/to/model"

    def test_model_not_found_error_without_path(self):
        """Test ModelNotFoundError without path specified."""
        exc = ModelNotFoundError()
        assert "Model not found" in exc.message
        assert exc.status_code == status.HTTP_503_SERVICE_UNAVAILABLE

    def test_model_inference_error(self):
        """Test ModelInferenceError exception."""
        exc = ModelInferenceError("Inference timeout")
        assert exc.message == "Inference timeout"
        assert exc.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert exc.detail["error_type"] == "inference_error"

    def test_input_validation_error(self):
        """Test InputValidationError exception."""
        exc = InputValidationError("Invalid text format")
        assert exc.message == "Invalid text format"
        assert exc.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert exc.detail["error_type"] == "input_validation_error"

    def test_database_connection_error(self):
        """Test DatabaseConnectionError exception."""
        exc = DatabaseConnectionError("Connection timeout")
        assert exc.message == "Connection timeout"
        assert exc.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert exc.detail["error_type"] == "database_error"

    def test_authentication_error(self):
        """Test AuthenticationError exception."""
        exc = AuthenticationError("Invalid credentials")
        assert exc.message == "Invalid credentials"
        assert exc.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc.detail["error_type"] == "authentication_error"

    def test_rate_limit_error(self):
        """Test RateLimitError exception."""
        exc = RateLimitError("Too many requests")
        assert exc.message == "Too many requests"
        assert exc.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert exc.detail["error_type"] == "rate_limit_exceeded"

    def test_exception_inheritance(self):
        """Test that custom exceptions inherit from AppException."""
        assert issubclass(ModelNotFoundError, AppException)
        assert issubclass(ModelInferenceError, AppException)
        assert issubclass(InputValidationError, AppException)
        assert issubclass(DatabaseConnectionError, AppException)
        assert issubclass(AuthenticationError, AppException)
        assert issubclass(RateLimitError, AppException)

    def test_exception_status_codes(self):
        """Test that exceptions have correct HTTP status codes."""
        assert ModelNotFoundError().status_code == 503
        assert ModelInferenceError().status_code == 500
        assert InputValidationError().status_code == 422
        assert DatabaseConnectionError().status_code == 503
        assert AuthenticationError().status_code == 401
        assert RateLimitError().status_code == 429
