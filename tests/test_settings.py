"""
Tests for the Settings configuration module.
"""

import os

import pytest

from textSummarizer.config.settings import Settings, get_settings


class TestSettings:
    """Test suite for Settings configuration."""

    def test_settings_defaults(self):
        """Test that settings load with expected default values."""
        settings = Settings()
        assert settings.APP_NAME == "Text Summarizer API"
        assert settings.APP_VERSION == "1.0.0"
        assert settings.JWT_ALGORITHM == "HS256"
        assert settings.HOST == "0.0.0.0"
        assert settings.PORT == 8080

    def test_settings_from_environment(self, test_settings: Settings):
        """Test that settings load from environment variables."""
        assert test_settings.APP_ENV == "testing"
        assert test_settings.SECRET_KEY == "test-secret-key-for-testing-only-not-secure"
        assert test_settings.MONGODB_URL == "mongodb://localhost:27017/test_db"

    def test_allowed_origins_list_property(self, test_settings: Settings):
        """Test the allowed_origins_list property parses correctly."""
        os.environ["ALLOWED_ORIGINS"] = "http://localhost,http://example.com,http://test.com"
        get_settings.cache_clear()
        settings = get_settings()

        origins = settings.allowed_origins_list
        assert len(origins) == 3
        assert "http://localhost" in origins
        assert "http://example.com" in origins
        assert "http://test.com" in origins

    def test_api_keys_list_property(self, test_settings: Settings):
        """Test the api_keys_list property parses correctly."""
        keys = test_settings.api_keys_list
        assert len(keys) == 2
        assert "test-api-key-1" in keys
        assert "test-api-key-2" in keys

    def test_api_keys_list_empty(self):
        """Test api_keys_list returns empty list when no keys configured."""
        os.environ["API_KEYS"] = ""
        get_settings.cache_clear()
        settings = get_settings()

        assert settings.api_keys_list == []

    def test_is_production_property(self, test_settings: Settings):
        """Test is_production property returns correct boolean."""
        assert test_settings.is_production is False

        os.environ["APP_ENV"] = "production"
        get_settings.cache_clear()
        prod_settings = get_settings()
        assert prod_settings.is_production is True

    def test_is_development_property(self):
        """Test is_development property returns correct boolean."""
        os.environ["APP_ENV"] = "development"
        get_settings.cache_clear()
        settings = get_settings()

        assert settings.is_development is True

    def test_environment_validation(self):
        """Test that invalid APP_ENV values are rejected."""
        os.environ["APP_ENV"] = "invalid_environment"
        get_settings.cache_clear()

        with pytest.raises(Exception):  # Pydantic validation error
            Settings()

    def test_settings_singleton_caching(self):
        """Test that get_settings returns the same cached instance."""
        settings1 = get_settings()
        settings2 = get_settings()
        assert settings1 is settings2
