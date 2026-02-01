"""Pydantic v2 response models."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class PredictResponse(BaseModel):
    """Response schema for the text summarization endpoint."""

    summary: str = Field(..., description="The generated text summary.")
    input_length: int = Field(..., description="Character count of the input text.")
    output_length: int = Field(..., description="Character count of the generated summary.")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds.")
    request_id: str = Field(..., description="Unique request tracking identifier.")
    model: str = Field(default="pegasus-samsum", description="Model used for summarization.")


class StatusResponse(BaseModel):
    """Response schema for the API status endpoint."""

    status: str = Field(..., description="API operational status.")
    version: str = Field(..., description="API version string.")
    environment: str = Field(..., description="Current deployment environment.")
    model_loaded: bool = Field(..., description="Whether the ML model is loaded and ready.")


class HealthResponse(BaseModel):
    """Response schema for the health check endpoint."""

    status: str = Field(..., description="Overall health status.")
    api: str = Field(default="healthy", description="API server health.")
    database: Dict[str, Any] = Field(
        default_factory=dict, description="Database connection health."
    )
    model: str = Field(default="unknown", description="ML model health status.")


class TokenResponse(BaseModel):
    """Response schema for JWT token generation."""

    access_token: str = Field(..., description="JWT access token.")
    token_type: str = Field(default="bearer", description="Token type.")
    expires_in: int = Field(..., description="Token expiration time in seconds.")


class ErrorResponse(BaseModel):
    """Standardized error response schema."""

    error: bool = Field(default=True)
    status_code: int = Field(..., description="HTTP status code.")
    message: str = Field(..., description="Error description.")
    request_id: Optional[str] = Field(default=None, description="Request tracking ID.")
    detail: Optional[Dict[str, Any]] = Field(default=None, description="Additional error context.")
