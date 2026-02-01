# =============================================================================
# Production Dockerfile - Multi-stage build
# =============================================================================
# Stage 1: Build dependencies
# Stage 2: Production runtime (non-root user)
# =============================================================================

# --- Stage 1: Builder ---
FROM python:3.10-slim-bookworm AS builder

WORKDIR /build

COPY requirements.txt .

RUN pip install --no-cache-dir --prefix=/install \
    -r requirements.txt && \
    pip install --no-cache-dir --prefix=/install \
    accelerate

# --- Stage 2: Production runtime ---
FROM python:3.10-slim-bookworm AS production

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser -d /app -s /sbin/nologin appuser

WORKDIR /app

# Copy installed Python packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY --chown=appuser:appuser . /app

# Create required directories
RUN mkdir -p /app/logs /app/artifacts && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose application port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Environment defaults
ENV APP_ENV=production \
    LOG_LEVEL=INFO \
    HOST=0.0.0.0 \
    PORT=8080

CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "2"]
