"""
Integration tests for FastAPI endpoints.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient

from textSummarizer.config.settings import Settings


class TestAPIEndpoints:
    """Test suite for API endpoints integration."""

    @pytest.mark.asyncio
    async def test_get_status_success(self, test_app: AsyncClient, test_settings: Settings):
        """Test GET /status endpoint returns correct status information."""
        response = await test_app.get("/status")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "operational"
        assert data["version"] == test_settings.APP_VERSION
        assert data["environment"] == test_settings.APP_ENV
        assert "model_loaded" in data

    @pytest.mark.asyncio
    async def test_get_health_success(self, test_app: AsyncClient):
        """Test GET /health endpoint returns health status."""
        with patch("app.get_db_manager") as mock_db_manager:
            mock_db = AsyncMock()
            mock_db.health_check.return_value = {
                "status": "healthy",
                "connected": True,
                "latency_ms": 5.2,
            }
            mock_db_manager.return_value = mock_db

            response = await test_app.get("/health")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] in ["healthy", "degraded"]
            assert data["api"] == "healthy"
            assert "database" in data
            assert "model" in data

    @pytest.mark.asyncio
    async def test_post_auth_token_success(self, test_app: AsyncClient):
        """Test POST /auth/token endpoint generates valid JWT token."""
        with patch("app.get_audit_logger") as mock_audit_logger:
            mock_audit = MagicMock()
            mock_audit_logger.return_value = mock_audit

            payload = {"username": "testuser", "password": "testpass123"}
            response = await test_app.post("/auth/token", json=payload)

            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            assert data["token_type"] == "bearer"
            assert "expires_in" in data
            assert data["expires_in"] > 0

    @pytest.mark.asyncio
    async def test_post_auth_token_validation_error(self, test_app: AsyncClient):
        """Test POST /auth/token with invalid payload returns validation error."""
        payload = {"username": "ab", "password": "short"}
        response = await test_app.post("/auth/token", json=payload)

        assert response.status_code == 422
        data = response.json()
        assert data["error"] is True
        assert "validation" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_post_predict_success(
        self, test_app: AsyncClient, mock_prediction_pipeline: MagicMock
    ):
        """Test POST /predict endpoint with valid input returns summary."""
        with patch("app._prediction_pipeline", mock_prediction_pipeline), \
             patch("app.get_db_manager") as mock_db_manager, \
             patch("app.get_audit_logger") as mock_audit_logger:

            mock_db = AsyncMock()
            mock_db.is_connected = True
            mock_db.log_prediction.return_value = None
            mock_db_manager.return_value = mock_db

            mock_audit = MagicMock()
            mock_audit_logger.return_value = mock_audit

            payload = {
                "text": "This is a test text that needs to be summarized. " * 10,
                "max_length": 128,
                "num_beams": 8,
                "length_penalty": 0.8,
            }
            response = await test_app.post("/predict", json=payload)

            assert response.status_code == 200
            data = response.json()
            assert "summary" in data
            assert data["summary"] == "This is a mocked summary of the input text."
            assert "input_length" in data
            assert "output_length" in data
            assert "processing_time_ms" in data
            assert "request_id" in data
            assert data["input_length"] > 0
            assert data["output_length"] > 0

    @pytest.mark.asyncio
    async def test_post_predict_model_not_loaded(self, test_app: AsyncClient):
        """Test POST /predict returns 503 when model is not loaded."""
        with patch("app._prediction_pipeline", None):
            payload = {
                "text": "This is a test text that needs summarization.",
            }
            response = await test_app.post("/predict", json=payload)

            assert response.status_code == 503
            data = response.json()
            assert data["error"] is True
            assert "model" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_post_predict_validation_error_text_too_short(self, test_app: AsyncClient):
        """Test POST /predict with text too short returns validation error."""
        payload = {"text": "Short"}
        response = await test_app.post("/predict", json=payload)

        assert response.status_code == 422
        data = response.json()
        assert data["error"] is True

    @pytest.mark.asyncio
    async def test_post_predict_suspicious_patterns(
        self, test_app: AsyncClient, mock_prediction_pipeline: MagicMock
    ):
        """Test POST /predict rejects input with suspicious patterns."""
        with patch("app._prediction_pipeline", mock_prediction_pipeline):
            payload = {
                "text": "This text contains <script>alert('XSS')</script> malicious content.",
            }
            response = await test_app.post("/predict", json=payload)

            assert response.status_code == 422
            data = response.json()
            assert data["error"] is True
            assert "disallowed patterns" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_post_predict_rate_limit_exceeded(
        self, test_app: AsyncClient, mock_prediction_pipeline: MagicMock, test_settings: Settings
    ):
        """Test POST /predict rate limiting blocks excessive requests."""
        with patch("app._prediction_pipeline", mock_prediction_pipeline), \
             patch("app.get_db_manager") as mock_db_manager, \
             patch("app.get_audit_logger") as mock_audit_logger:

            mock_db = AsyncMock()
            mock_db.is_connected = True
            mock_db.log_prediction.return_value = None
            mock_db_manager.return_value = mock_db

            mock_audit = MagicMock()
            mock_audit_logger.return_value = mock_audit

            payload = {
                "text": "This is a test text for rate limit testing. " * 5,
            }

            # Make requests up to the limit
            for _ in range(test_settings.RATE_LIMIT_REQUESTS):
                response = await test_app.post("/predict", json=payload)
                if response.status_code == 429:
                    break

            # Next request should be rate limited
            response = await test_app.post("/predict", json=payload)
            assert response.status_code == 429
            data = response.json()
            assert data["error"] is True
            assert "rate limit" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_post_predict_inference_error(
        self, test_app: AsyncClient, mock_prediction_pipeline: MagicMock
    ):
        """Test POST /predict handles model inference errors gracefully."""
        mock_prediction_pipeline.predict.side_effect = Exception("Model inference failed")

        with patch("app._prediction_pipeline", mock_prediction_pipeline), \
             patch("app.get_audit_logger") as mock_audit_logger:

            mock_audit = MagicMock()
            mock_audit_logger.return_value = mock_audit

            payload = {
                "text": "This is a test text that will cause inference error.",
            }
            response = await test_app.post("/predict", json=payload)

            assert response.status_code == 500
            data = response.json()
            assert data["error"] is True
            assert "summarization failed" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_get_train_endpoint(self, test_app: AsyncClient):
        """Test GET /train endpoint triggers training pipeline."""
        with patch("os.system") as mock_system:
            mock_system.return_value = 0

            response = await test_app.get("/train")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert "training" in data["message"].lower()
            mock_system.assert_called_once_with("python main.py")

    @pytest.mark.asyncio
    async def test_root_redirects_to_docs(self, test_app: AsyncClient):
        """Test that root path redirects to API documentation."""
        response = await test_app.get("/", follow_redirects=False)

        assert response.status_code == 307
        assert response.headers["location"] == "/docs"

    @pytest.mark.asyncio
    async def test_predict_with_custom_parameters(
        self, test_app: AsyncClient, mock_prediction_pipeline: MagicMock
    ):
        """Test POST /predict accepts custom generation parameters."""
        with patch("app._prediction_pipeline", mock_prediction_pipeline), \
             patch("app.get_db_manager") as mock_db_manager, \
             patch("app.get_audit_logger") as mock_audit_logger:

            mock_db = AsyncMock()
            mock_db.is_connected = True
            mock_db.log_prediction.return_value = None
            mock_db_manager.return_value = mock_db

            mock_audit = MagicMock()
            mock_audit_logger.return_value = mock_audit

            payload = {
                "text": "Custom parameters test text. " * 20,
                "max_length": 256,
                "num_beams": 12,
                "length_penalty": 1.2,
            }
            response = await test_app.post("/predict", json=payload)

            assert response.status_code == 200
            data = response.json()
            assert "summary" in data

    @pytest.mark.asyncio
    async def test_predict_database_logging(
        self, test_app: AsyncClient, mock_prediction_pipeline: MagicMock
    ):
        """Test POST /predict logs predictions to database when connected."""
        with patch("app._prediction_pipeline", mock_prediction_pipeline), \
             patch("app.get_db_manager") as mock_db_manager, \
             patch("app.get_audit_logger") as mock_audit_logger:

            mock_db = AsyncMock()
            mock_db.is_connected = True
            mock_db.log_prediction = AsyncMock()
            mock_db_manager.return_value = mock_db

            mock_audit = MagicMock()
            mock_audit_logger.return_value = mock_audit

            payload = {
                "text": "Test text for database logging verification.",
            }
            response = await test_app.post("/predict", json=payload)

            assert response.status_code == 200
            mock_db.log_prediction.assert_called_once()
            call_args = mock_db.log_prediction.call_args[1]
            assert "request_id" in call_args
            assert "input_text" in call_args
            assert "output_summary" in call_args
            assert "duration_ms" in call_args
