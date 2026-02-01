"""
Pytest configuration and shared fixtures for the test suite.
"""

import os
import sys
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import AsyncClient

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from textSummarizer.config.settings import Settings, get_settings


@pytest.fixture(scope="function")
def test_settings() -> Generator[Settings, None, None]:
    """Provide test settings with environment variables configured for testing.

    Yields:
        Settings instance configured for testing.
    """
    # Store original env vars
    original_env = {
        "APP_ENV": os.environ.get("APP_ENV"),
        "SECRET_KEY": os.environ.get("SECRET_KEY"),
        "MONGODB_URL": os.environ.get("MONGODB_URL"),
        "RATE_LIMIT_REQUESTS": os.environ.get("RATE_LIMIT_REQUESTS"),
        "RATE_LIMIT_WINDOW_SECONDS": os.environ.get("RATE_LIMIT_WINDOW_SECONDS"),
        "API_KEYS": os.environ.get("API_KEYS"),
        "JWT_EXPIRATION_MINUTES": os.environ.get("JWT_EXPIRATION_MINUTES"),
    }

    # Set test environment variables
    os.environ["APP_ENV"] = "testing"
    os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only-not-secure"
    os.environ["MONGODB_URL"] = "mongodb://localhost:27017/test_db"
    os.environ["RATE_LIMIT_REQUESTS"] = "10"
    os.environ["RATE_LIMIT_WINDOW_SECONDS"] = "60"
    os.environ["API_KEYS"] = "test-api-key-1,test-api-key-2"
    os.environ["JWT_EXPIRATION_MINUTES"] = "30"

    # Clear the lru_cache on get_settings
    get_settings.cache_clear()

    # Yield the new settings
    yield get_settings()

    # Restore original environment
    for key, value in original_env.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value

    # Clear cache again after test
    get_settings.cache_clear()


@pytest.fixture(scope="function")
async def test_app(test_settings: Settings) -> AsyncGenerator[AsyncClient, None]:
    """Provide async test client for FastAPI app.

    Args:
        test_settings: Test settings fixture.

    Yields:
        AsyncClient configured for testing.
    """
    from app import app

    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture(scope="function")
def mock_prediction_pipeline() -> MagicMock:
    """Provide a mocked PredictionPipeline for testing.

    Returns:
        Mocked PredictionPipeline instance.
    """
    mock_pipeline = MagicMock()
    mock_pipeline.predict.return_value = "This is a mocked summary of the input text."
    return mock_pipeline


@pytest.fixture(scope="function")
def mock_db_manager() -> AsyncMock:
    """Provide a mocked MongoDBManager for testing.

    Returns:
        Mocked MongoDBManager instance.
    """
    mock_db = AsyncMock()
    mock_db.is_connected = True
    mock_db.connect.return_value = None
    mock_db.close.return_value = None
    mock_db.health_check.return_value = {
        "status": "healthy",
        "connected": True,
        "latency_ms": 5.2,
    }
    mock_db.log_prediction.return_value = None
    return mock_db


@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset singleton instances between tests."""
    # Reset rate limiter singleton
    from textSummarizer.security import rate_limiter
    rate_limiter.rate_limiter = None

    yield

    # Cleanup after test
    rate_limiter.rate_limiter = None
