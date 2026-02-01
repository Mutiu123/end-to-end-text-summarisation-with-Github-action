"""
Custom exception classes and global exception handlers for the application.
Provides structured error responses with proper HTTP status codes.
"""

from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class AppException(Exception):
    """Base application exception."""

    def __init__(
        self,
        message: str = "An unexpected error occurred",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.detail = detail or {}
        super().__init__(self.message)


class ModelNotFoundError(AppException):
    """Raised when the ML model files cannot be found."""

    def __init__(self, model_path: str = ""):
        super().__init__(
            message=f"Model not found at path: {model_path}" if model_path else "Model not found",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"error_type": "model_not_found", "model_path": model_path},
        )


class ModelInferenceError(AppException):
    """Raised when model inference fails."""

    def __init__(self, message: str = "Model inference failed"):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_type": "inference_error"},
        )


class InputValidationError(AppException):
    """Raised for input validation failures beyond Pydantic."""

    def __init__(self, message: str = "Invalid input"):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"error_type": "input_validation_error"},
        )


class DatabaseConnectionError(AppException):
    """Raised when database connection fails."""

    def __init__(self, message: str = "Database connection failed"):
        super().__init__(
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"error_type": "database_error"},
        )


class AuthenticationError(AppException):
    """Raised for authentication failures."""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error_type": "authentication_error"},
        )


class RateLimitError(AppException):
    """Raised when rate limit is exceeded."""

    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(
            message=message,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={"error_type": "rate_limit_exceeded"},
        )


def _build_error_response(
    request_id: str,
    status_code: int,
    message: str,
    detail: Optional[Dict[str, Any]] = None,
) -> JSONResponse:
    """Build a standardized error JSON response.

    Args:
        request_id: The unique request tracking ID.
        status_code: HTTP status code.
        message: Human-readable error message.
        detail: Additional error context.

    Returns:
        JSONResponse with structured error body.
    """
    body = {
        "error": True,
        "status_code": status_code,
        "message": message,
        "request_id": request_id,
    }
    if detail:
        body["detail"] = detail
    return JSONResponse(status_code=status_code, content=body)


def register_exception_handlers(app: FastAPI) -> None:
    """Register global exception handlers on the FastAPI application.

    Args:
        app: The FastAPI application instance.
    """

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        request_id = getattr(request.state, "request_id", "unknown")
        return _build_error_response(
            request_id=request_id,
            status_code=exc.status_code,
            message=exc.message,
            detail=exc.detail,
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        request_id = getattr(request.state, "request_id", "unknown")
        return _build_error_response(
            request_id=request_id,
            status_code=exc.status_code,
            message=str(exc.detail),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        request_id = getattr(request.state, "request_id", "unknown")
        errors = []
        for error in exc.errors():
            errors.append(
                {
                    "field": " -> ".join(str(loc) for loc in error["loc"]),
                    "message": error["msg"],
                    "type": error["type"],
                }
            )
        return _build_error_response(
            request_id=request_id,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message="Request validation failed",
            detail={"validation_errors": errors},
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        request_id = getattr(request.state, "request_id", "unknown")
        return _build_error_response(
            request_id=request_id,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An internal server error occurred",
        )
