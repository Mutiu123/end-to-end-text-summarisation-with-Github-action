"""
Structured JSON logging with custom formatter.
Provides consistent, machine-parseable log output for production environments.
"""

import json
import logging
import sys
import traceback
from datetime import datetime, timezone
from typing import Any, Dict, Optional


class JSONFormatter(logging.Formatter):
    """Custom log formatter that outputs structured JSON lines."""

    def __init__(self, service_name: str = "text-summarizer", environment: str = "development"):
        super().__init__()
        self.service_name = service_name
        self.environment = environment

    def format(self, record: logging.LogRecord) -> str:
        log_entry: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "service": self.service_name,
            "environment": self.environment,
        }

        if hasattr(record, "request_id"):
            log_entry["request_id"] = record.request_id

        if hasattr(record, "user_id"):
            log_entry["user_id"] = record.user_id

        if hasattr(record, "extra_data"):
            log_entry["data"] = record.extra_data

        if record.exc_info and record.exc_info[0] is not None:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info),
            }

        return json.dumps(log_entry, default=str)


def setup_structured_logging(
    level: str = "INFO",
    service_name: str = "text-summarizer",
    environment: str = "development",
) -> logging.Logger:
    """Configure structured JSON logging for the application.

    Args:
        level: Log level string (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        service_name: Service name included in every log entry.
        environment: Environment name (development, staging, production).

    Returns:
        Configured root logger.
    """
    root_logger = logging.getLogger()

    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter(service_name=service_name, environment=environment))

    root_logger.addHandler(handler)
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.WARNING)

    return root_logger


class AuditLogger:
    """Audit logger for tracking predictions and security events."""

    def __init__(self, logger_name: str = "audit"):
        self._logger = logging.getLogger(logger_name)

    def log_prediction(
        self,
        request_id: str,
        input_length: int,
        output_length: int,
        duration_ms: float,
        status: str = "success",
        user_id: Optional[str] = None,
    ) -> None:
        """Log a prediction event.

        Args:
            request_id: Unique request identifier.
            input_length: Character count of input text.
            output_length: Character count of generated summary.
            duration_ms: Processing time in milliseconds.
            status: Outcome status (success/failure).
            user_id: Optional user identifier.
        """
        extra = {
            "extra_data": {
                "event_type": "prediction",
                "request_id": request_id,
                "input_length": input_length,
                "output_length": output_length,
                "duration_ms": round(duration_ms, 2),
                "status": status,
                "user_id": user_id,
            }
        }
        self._logger.info("Prediction completed", extra=extra)

    def log_auth_event(
        self,
        event: str,
        success: bool,
        client_ip: str,
        user_id: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> None:
        """Log an authentication event.

        Args:
            event: Event type (login, token_refresh, etc.).
            success: Whether authentication succeeded.
            client_ip: Client IP address.
            user_id: Optional user identifier.
            reason: Failure reason if applicable.
        """
        extra = {
            "extra_data": {
                "event_type": "auth",
                "event": event,
                "success": success,
                "client_ip": client_ip,
                "user_id": user_id,
                "reason": reason,
            }
        }
        level = logging.INFO if success else logging.WARNING
        self._logger.log(level, f"Auth event: {event}", extra=extra)

    def log_rate_limit(self, client_ip: str, endpoint: str) -> None:
        """Log a rate limit event.

        Args:
            client_ip: Client IP that was rate limited.
            endpoint: The endpoint that was accessed.
        """
        extra = {
            "extra_data": {
                "event_type": "rate_limit",
                "client_ip": client_ip,
                "endpoint": endpoint,
            }
        }
        self._logger.warning("Rate limit exceeded", extra=extra)


def get_audit_logger() -> AuditLogger:
    """Get the audit logger instance."""
    return AuditLogger()
