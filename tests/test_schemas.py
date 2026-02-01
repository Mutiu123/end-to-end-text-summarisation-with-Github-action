"""
Tests for Pydantic request and response schemas.
"""

import pytest
from pydantic import ValidationError

from textSummarizer.schemas.requests import PredictRequest, TokenRequest
from textSummarizer.schemas.responses import (
    ErrorResponse,
    HealthResponse,
    PredictResponse,
    StatusResponse,
    TokenResponse,
)


class TestRequestSchemas:
    """Test suite for request schemas."""

    def test_predict_request_valid(self):
        """Test valid PredictRequest creation."""
        request = PredictRequest(
            text="This is a test text that needs to be summarized properly.",
            max_length=128,
            num_beams=8,
            length_penalty=0.8,
        )
        assert request.text == "This is a test text that needs to be summarized properly."
        assert request.max_length == 128
        assert request.num_beams == 8
        assert request.length_penalty == 0.8

    def test_predict_request_defaults(self):
        """Test PredictRequest uses correct default values."""
        request = PredictRequest(text="This is a test text for summarization.")
        assert request.max_length == 128
        assert request.num_beams == 8
        assert request.length_penalty == 0.8

    def test_predict_request_text_too_short(self):
        """Test PredictRequest validation fails for text too short."""
        with pytest.raises(ValidationError) as exc_info:
            PredictRequest(text="Short")

        errors = exc_info.value.errors()
        assert any("at least 10 characters" in str(e) for e in errors)

    def test_predict_request_text_too_long(self):
        """Test PredictRequest validation fails for text too long."""
        long_text = "a" * 10001
        with pytest.raises(ValidationError) as exc_info:
            PredictRequest(text=long_text)

        errors = exc_info.value.errors()
        assert any("at most 10000 characters" in str(e) for e in errors)

    def test_predict_request_blank_text(self):
        """Test PredictRequest validation fails for blank text."""
        with pytest.raises(ValidationError) as exc_info:
            PredictRequest(text="          ")

        errors = exc_info.value.errors()
        assert any("blank" in str(e).lower() or "whitespace" in str(e).lower() for e in errors)

    def test_predict_request_max_length_constraints(self):
        """Test PredictRequest max_length field constraints."""
        text = "Valid text for testing constraints."

        # Valid range
        request = PredictRequest(text=text, max_length=50)
        assert request.max_length == 50

        # Below minimum
        with pytest.raises(ValidationError):
            PredictRequest(text=text, max_length=5)

        # Above maximum
        with pytest.raises(ValidationError):
            PredictRequest(text=text, max_length=600)

    def test_predict_request_num_beams_constraints(self):
        """Test PredictRequest num_beams field constraints."""
        text = "Valid text for testing constraints."

        # Valid range
        request = PredictRequest(text=text, num_beams=4)
        assert request.num_beams == 4

        # Below minimum
        with pytest.raises(ValidationError):
            PredictRequest(text=text, num_beams=0)

        # Above maximum
        with pytest.raises(ValidationError):
            PredictRequest(text=text, num_beams=20)

    def test_predict_request_length_penalty_constraints(self):
        """Test PredictRequest length_penalty field constraints."""
        text = "Valid text for testing constraints."

        # Valid range
        request = PredictRequest(text=text, length_penalty=1.5)
        assert request.length_penalty == 1.5

        # Below minimum
        with pytest.raises(ValidationError):
            PredictRequest(text=text, length_penalty=0.05)

        # Above maximum
        with pytest.raises(ValidationError):
            PredictRequest(text=text, length_penalty=3.0)

    def test_token_request_valid(self):
        """Test valid TokenRequest creation."""
        request = TokenRequest(username="testuser", password="securepass123")
        assert request.username == "testuser"
        assert request.password == "securepass123"

    def test_token_request_username_too_short(self):
        """Test TokenRequest validation fails for username too short."""
        with pytest.raises(ValidationError) as exc_info:
            TokenRequest(username="ab", password="securepass123")

        errors = exc_info.value.errors()
        assert any("at least 3 characters" in str(e) for e in errors)

    def test_token_request_password_too_short(self):
        """Test TokenRequest validation fails for password too short."""
        with pytest.raises(ValidationError) as exc_info:
            TokenRequest(username="testuser", password="short")

        errors = exc_info.value.errors()
        assert any("at least 8 characters" in str(e) for e in errors)


class TestResponseSchemas:
    """Test suite for response schemas."""

    def test_predict_response_creation(self):
        """Test PredictResponse creation with all fields."""
        response = PredictResponse(
            summary="This is a summary.",
            input_length=100,
            output_length=20,
            processing_time_ms=150.5,
            request_id="test-req-123",
        )
        assert response.summary == "This is a summary."
        assert response.input_length == 100
        assert response.output_length == 20
        assert response.processing_time_ms == 150.5
        assert response.request_id == "test-req-123"
        assert response.model == "pegasus-samsum"

    def test_status_response_creation(self):
        """Test StatusResponse creation."""
        response = StatusResponse(
            status="operational",
            version="1.0.0",
            environment="testing",
            model_loaded=True,
        )
        assert response.status == "operational"
        assert response.version == "1.0.0"
        assert response.environment == "testing"
        assert response.model_loaded is True

    def test_health_response_creation(self):
        """Test HealthResponse creation."""
        db_health = {"status": "healthy", "connected": True}
        response = HealthResponse(
            status="healthy",
            api="healthy",
            database=db_health,
            model="healthy",
        )
        assert response.status == "healthy"
        assert response.api == "healthy"
        assert response.database == db_health
        assert response.model == "healthy"

    def test_token_response_creation(self):
        """Test TokenResponse creation."""
        response = TokenResponse(
            access_token="jwt.token.here",
            token_type="bearer",
            expires_in=1800,
        )
        assert response.access_token == "jwt.token.here"
        assert response.token_type == "bearer"
        assert response.expires_in == 1800

    def test_error_response_creation(self):
        """Test ErrorResponse creation."""
        detail = {"field": "text", "issue": "too short"}
        response = ErrorResponse(
            status_code=422,
            message="Validation failed",
            request_id="req-456",
            detail=detail,
        )
        assert response.error is True
        assert response.status_code == 422
        assert response.message == "Validation failed"
        assert response.request_id == "req-456"
        assert response.detail == detail
