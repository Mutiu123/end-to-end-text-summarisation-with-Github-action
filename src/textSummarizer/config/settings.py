"""
Centralized application settings using Pydantic BaseSettings.
Loads configuration from environment variables with type safety and validation.
"""

from functools import lru_cache
from typing import List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # --- Application ---
    APP_NAME: str = "Text Summarizer API"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = Field(default="development", pattern="^(development|staging|production)$")
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8080
    LOG_LEVEL: str = "INFO"

    # --- Security ---
    SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 30
    ALLOWED_ORIGINS: str = "http://localhost,http://localhost:3000"
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW_SECONDS: int = 60
    API_KEY_HEADER: str = "X-API-Key"
    API_KEYS: str = ""

    # --- Database (MongoDB) ---
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "text_summarizer"
    MONGODB_MIN_POOL_SIZE: int = 10
    MONGODB_MAX_POOL_SIZE: int = 50
    MONGODB_CONNECT_TIMEOUT_MS: int = 5000
    MONGODB_SERVER_SELECTION_TIMEOUT_MS: int = 5000

    # --- Monitoring ---
    ENABLE_METRICS: bool = True
    METRICS_PREFIX: str = "textsummarizer"

    # --- Model ---
    MODEL_PATH: str = "artifacts/model_trainer/pegasus-samsum-model"
    TOKENIZER_PATH: str = "artifacts/model_trainer/tokenizer"
    MAX_INPUT_LENGTH: int = 1024
    MAX_SUMMARY_LENGTH: int = 128
    NUM_BEAMS: int = 8
    LENGTH_PENALTY: float = 0.8

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_origins(cls, v: str) -> str:
        return v

    @property
    def allowed_origins_list(self) -> List[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]

    @property
    def api_keys_list(self) -> List[str]:
        if not self.API_KEYS:
            return []
        return [k.strip() for k in self.API_KEYS.split(",") if k.strip()]

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"

    @property
    def is_development(self) -> bool:
        return self.APP_ENV == "development"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }


@lru_cache()
def get_settings() -> Settings:
    """Return cached Settings instance. Use lru_cache for singleton behavior."""
    return Settings()
