"""
Text Summarizer API - Production FastAPI Application

Enterprise-grade REST API for text summarization using the PEGASUS model.
Features JWT authentication, rate limiting, Prometheus metrics,
structured logging, MongoDB audit logging, and comprehensive health checks.
"""

import logging
import os
import time
from contextlib import asynccontextmanager

import uvicorn
from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app
from starlette.responses import RedirectResponse

from textSummarizer.config.settings import Settings, get_settings
from textSummarizer.database.mongodb import get_db_manager
from textSummarizer.exceptions import (
    InputValidationError,
    ModelInferenceError,
    ModelNotFoundError,
    register_exception_handlers,
)
from textSummarizer.monitoring.metrics import get_metrics
from textSummarizer.monitoring.middleware import RequestTrackingMiddleware
from textSummarizer.monitoring.structured_logging import (
    get_audit_logger,
    setup_structured_logging,
)
from textSummarizer.schemas.requests import PredictRequest, TokenRequest
from textSummarizer.schemas.responses import (
    ErrorResponse,
    HealthResponse,
    PredictResponse,
    StatusResponse,
    TokenResponse,
)
from textSummarizer.security.auth import (
    create_access_token,
    get_current_user,
    validate_api_key,
)
from textSummarizer.security.rate_limiter import get_rate_limiter
from textSummarizer.security.sanitizer import (
    contains_suspicious_patterns,
    sanitize_text,
    validate_text_length,
)

logger = logging.getLogger(__name__)

# Global model reference
_prediction_pipeline = None


def _load_model(settings: Settings) -> None:
    """Load the ML model into memory."""
    global _prediction_pipeline
    try:
        from textSummarizer.pipeline.prediction import PredictionPipeline

        _prediction_pipeline = PredictionPipeline()
        metrics = get_metrics(settings.METRICS_PREFIX)
        metrics.model_loaded.set(1)
        logger.info("ML model loaded successfully")
    except Exception as e:
        logger.error("Failed to load ML model: %s", str(e))
        metrics = get_metrics(settings.METRICS_PREFIX)
        metrics.model_loaded.set(0)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup and shutdown events."""
    settings = get_settings()

    setup_structured_logging(
        level=settings.LOG_LEVEL,
        service_name=settings.APP_NAME,
        environment=settings.APP_ENV,
    )

    metrics = get_metrics(settings.METRICS_PREFIX)
    metrics.app_info.info(
        {
            "version": settings.APP_VERSION,
            "environment": settings.APP_ENV,
        }
    )

    db = get_db_manager()
    await db.connect(settings)

    _load_model(settings)

    logger.info(
        "Application started: %s v%s [%s]",
        settings.APP_NAME,
        settings.APP_VERSION,
        settings.APP_ENV,
    )

    yield

    await db.close()
    logger.info("Application shutdown complete")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance.

    Returns:
        Fully configured FastAPI application.
    """
    settings = get_settings()

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=(
            "Enterprise-grade text summarization API powered by PEGASUS. "
            "Provides abstractive summarization of dialogue and text content."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # --- CORS ---
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins_list,
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )

    # --- Request tracking and metrics middleware ---
    app.add_middleware(RequestTrackingMiddleware)

    # --- Exception handlers ---
    register_exception_handlers(app)

    # --- Prometheus metrics endpoint ---
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)

    return app


app = create_app()


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.get("/", include_in_schema=False)
async def index():
    """Redirect root to API documentation."""
    return RedirectResponse(url="/docs")


@app.get(
    "/status",
    response_model=StatusResponse,
    tags=["health"],
    summary="API status",
)
async def get_status(settings: Settings = Depends(get_settings)):
    """Return current API status and version information."""
    return StatusResponse(
        status="operational",
        version=settings.APP_VERSION,
        environment=settings.APP_ENV,
        model_loaded=_prediction_pipeline is not None,
    )


@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["health"],
    summary="Health check",
)
async def health_check():
    """Comprehensive health check covering API, database, and model."""
    db = get_db_manager()
    db_health = await db.health_check()
    model_status = "healthy" if _prediction_pipeline is not None else "not_loaded"

    overall = "healthy"
    if model_status != "healthy":
        overall = "degraded"
    if db_health.get("status") == "error":
        overall = "degraded"

    return HealthResponse(
        status=overall,
        api="healthy",
        database=db_health,
        model=model_status,
    )


@app.post(
    "/auth/token",
    response_model=TokenResponse,
    tags=["authentication"],
    summary="Generate access token",
)
async def generate_token(
    request: TokenRequest,
    settings: Settings = Depends(get_settings),
):
    """Generate a JWT access token for API authentication.

    In production, replace this with your identity provider integration.
    """
    audit = get_audit_logger()

    token = create_access_token(
        data={"sub": request.username, "type": "access"},
        settings=settings,
    )

    audit.log_auth_event(
        event="token_generated",
        success=True,
        client_ip="internal",
        user_id=request.username,
    )

    metrics = get_metrics(settings.METRICS_PREFIX)
    metrics.auth_attempts_total.labels(result="success").inc()

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=settings.JWT_EXPIRATION_MINUTES * 60,
    )


@app.post(
    "/predict",
    response_model=PredictResponse,
    responses={
        422: {"model": ErrorResponse, "description": "Validation error"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
        503: {"model": ErrorResponse, "description": "Model not available"},
    },
    tags=["prediction"],
    summary="Summarize text",
)
async def predict(
    body: PredictRequest,
    request: Request,
    settings: Settings = Depends(get_settings),
):
    """Generate an abstractive summary of the provided text.

    The input text is sanitized and validated before being passed to the
    PEGASUS summarization model. Results are logged for audit purposes.
    """
    limiter = get_rate_limiter()
    limiter.check(request)

    request_id = getattr(request.state, "request_id", "unknown")
    metrics = get_metrics(settings.METRICS_PREFIX)
    audit = get_audit_logger()

    # --- Input sanitization ---
    cleaned_text = sanitize_text(body.text, max_length=settings.MAX_INPUT_LENGTH * 10)

    if contains_suspicious_patterns(body.text):
        raise InputValidationError("Input contains disallowed patterns")

    length_error = validate_text_length(cleaned_text, min_length=10, max_length=10000)
    if length_error:
        raise InputValidationError(length_error)

    # --- Model check ---
    if _prediction_pipeline is None:
        raise ModelNotFoundError(settings.MODEL_PATH)

    # --- Prediction ---
    metrics.prediction_input_length.observe(len(cleaned_text))
    start = time.perf_counter()

    try:
        summary = _prediction_pipeline.predict(cleaned_text)
        duration = (time.perf_counter() - start) * 1000
    except Exception as e:
        metrics.predictions_total.labels(status="error").inc()
        logger.error("Prediction failed: %s", str(e))
        raise ModelInferenceError(f"Summarization failed: {str(e)}")

    metrics.predictions_total.labels(status="success").inc()
    metrics.prediction_duration_seconds.observe(duration / 1000)
    metrics.prediction_output_length.observe(len(summary))

    audit.log_prediction(
        request_id=request_id,
        input_length=len(cleaned_text),
        output_length=len(summary),
        duration_ms=duration,
    )

    # --- Async DB logging (fire and forget) ---
    db = get_db_manager()
    if db.is_connected:
        await db.log_prediction(
            request_id=request_id,
            input_text=cleaned_text,
            output_summary=summary,
            duration_ms=duration,
        )

    return PredictResponse(
        summary=summary,
        input_length=len(cleaned_text),
        output_length=len(summary),
        processing_time_ms=round(duration, 2),
        request_id=request_id,
    )


@app.get(
    "/train",
    tags=["training"],
    summary="Trigger model training",
    responses={
        200: {"description": "Training completed successfully"},
        500: {"model": ErrorResponse, "description": "Training failed"},
    },
)
async def training():
    """Trigger the full training pipeline.

    This endpoint runs the complete model training pipeline synchronously.
    In production, consider offloading this to a background task queue.
    """
    try:
        os.system("python main.py")
        return {"status": "success", "message": "Training completed"}
    except Exception as e:
        raise ModelInferenceError(f"Training failed: {str(e)}")


if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "app:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.is_development,
        log_level=settings.LOG_LEVEL.lower(),
    )
