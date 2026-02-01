"""Pydantic v2 request models with validation."""

from typing import Optional

from pydantic import BaseModel, Field, field_validator


class PredictRequest(BaseModel):
    """Request schema for the text summarization endpoint."""

    text: str = Field(
        ...,
        min_length=10,
        max_length=10000,
        description="The text to summarize. Must be between 10 and 10,000 characters.",
        examples=["The quick brown fox jumps over the lazy dog. This is a sample text that needs summarization."],
    )
    max_length: Optional[int] = Field(
        default=128,
        ge=10,
        le=512,
        description="Maximum length of the generated summary in tokens.",
    )
    num_beams: Optional[int] = Field(
        default=8,
        ge=1,
        le=16,
        description="Number of beams for beam search.",
    )
    length_penalty: Optional[float] = Field(
        default=0.8,
        ge=0.1,
        le=2.0,
        description="Length penalty for generation. Values < 1.0 produce shorter summaries.",
    )

    @field_validator("text")
    @classmethod
    def text_must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Text must not be blank or contain only whitespace")
        return v


class TokenRequest(BaseModel):
    """Request schema for JWT token generation."""

    username: str = Field(
        ..., min_length=3, max_length=50, description="Username for authentication."
    )
    password: str = Field(
        ..., min_length=8, max_length=128, description="Password for authentication."
    )
