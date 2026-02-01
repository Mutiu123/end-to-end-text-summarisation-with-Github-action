"""
Prometheus metrics collection module.
Defines application-level metrics for monitoring and alerting.
"""

from prometheus_client import Counter, Gauge, Histogram, Info, Summary


class AppMetrics:
    """Container for all application Prometheus metrics."""

    def __init__(self, prefix: str = "textsummarizer"):
        # --- Request metrics ---
        self.requests_total = Counter(
            f"{prefix}_requests_total",
            "Total number of HTTP requests",
            ["method", "endpoint", "status_code"],
        )
        self.requests_in_progress = Gauge(
            f"{prefix}_requests_in_progress",
            "Number of requests currently being processed",
            ["method", "endpoint"],
        )
        self.request_duration_seconds = Histogram(
            f"{prefix}_request_duration_seconds",
            "HTTP request duration in seconds",
            ["method", "endpoint"],
            buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
        )

        # --- Prediction metrics ---
        self.predictions_total = Counter(
            f"{prefix}_predictions_total",
            "Total number of prediction requests",
            ["status"],
        )
        self.prediction_duration_seconds = Histogram(
            f"{prefix}_prediction_duration_seconds",
            "Model prediction latency in seconds",
            buckets=(0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0),
        )
        self.prediction_input_length = Histogram(
            f"{prefix}_prediction_input_length_chars",
            "Input text length in characters",
            buckets=(50, 100, 250, 500, 1000, 2500, 5000, 10000),
        )
        self.prediction_output_length = Histogram(
            f"{prefix}_prediction_output_length_chars",
            "Output summary length in characters",
            buckets=(10, 25, 50, 100, 250, 500),
        )

        # --- Authentication metrics ---
        self.auth_attempts_total = Counter(
            f"{prefix}_auth_attempts_total",
            "Total authentication attempts",
            ["result"],
        )

        # --- Rate limiting metrics ---
        self.rate_limit_hits_total = Counter(
            f"{prefix}_rate_limit_hits_total",
            "Total number of rate-limited requests",
        )

        # --- Database metrics ---
        self.db_operations_total = Counter(
            f"{prefix}_db_operations_total",
            "Total database operations",
            ["operation", "status"],
        )
        self.db_operation_duration_seconds = Summary(
            f"{prefix}_db_operation_duration_seconds",
            "Database operation duration in seconds",
            ["operation"],
        )

        # --- System metrics ---
        self.model_loaded = Gauge(
            f"{prefix}_model_loaded",
            "Whether the ML model is currently loaded (1=yes, 0=no)",
        )

        # --- Application info ---
        self.app_info = Info(
            f"{prefix}_app",
            "Application metadata",
        )


_metrics_instance: AppMetrics = None


def get_metrics(prefix: str = "textsummarizer") -> AppMetrics:
    """Get or create the singleton metrics instance.

    Args:
        prefix: Metric name prefix.

    Returns:
        The AppMetrics singleton.
    """
    global _metrics_instance
    if _metrics_instance is None:
        _metrics_instance = AppMetrics(prefix=prefix)
    return _metrics_instance
