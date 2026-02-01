"""
FastAPI middleware for request tracking, metrics collection, and logging.
"""

import time
import uuid

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from textSummarizer.monitoring.metrics import get_metrics
from textSummarizer.monitoring.structured_logging import get_audit_logger

import logging

logger = logging.getLogger(__name__)


class RequestTrackingMiddleware(BaseHTTPMiddleware):
    """Middleware that assigns a unique request ID to every request
    and collects Prometheus metrics for request duration and counts."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id

        metrics = get_metrics()
        method = request.method
        path = request.url.path

        metrics.requests_in_progress.labels(method=method, endpoint=path).inc()
        start_time = time.perf_counter()

        try:
            response = await call_next(request)
        except Exception:
            metrics.requests_in_progress.labels(method=method, endpoint=path).dec()
            metrics.requests_total.labels(
                method=method, endpoint=path, status_code=500
            ).inc()
            raise

        duration = time.perf_counter() - start_time

        metrics.requests_in_progress.labels(method=method, endpoint=path).dec()
        metrics.requests_total.labels(
            method=method, endpoint=path, status_code=response.status_code
        ).inc()
        metrics.request_duration_seconds.labels(method=method, endpoint=path).observe(
            duration
        )

        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{duration:.4f}"

        logger.info(
            "%s %s %d %.4fs",
            method,
            path,
            response.status_code,
            duration,
            extra={"request_id": request_id},
        )

        return response
