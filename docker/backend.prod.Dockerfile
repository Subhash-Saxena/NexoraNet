# ==============================================================================
# NexoraNet - Production Backend Dockerfile
# Multi-stage, Non-root, Minimal Attack Surface
# ==============================================================================

# -----------------------------
# Stage 1: Build Dependencies
# -----------------------------
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /install

# Install build dependencies required for compiling C-extensions (psycopg2, scapy, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# -----------------------------
# Stage 2: Production Runtime
# -----------------------------
FROM python:3.12-slim AS runner

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    ENVIRONMENT=production \
    DEBUG=False

WORKDIR /app

# Install runtime shared libraries and curl for health checks
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create dedicated non-root application user and group
RUN groupadd -r -g 10001 appgroup && \
    useradd -r -u 10001 -g appgroup -s /sbin/nologin -d /app appuser

# Copy installed Python packages from builder stage
COPY --from=builder /install /usr/local

# Copy backend application source code
COPY --chown=appuser:appgroup . /app

# Switch to unprivileged non-root user
USER appuser:appgroup

# Expose backend service port
EXPOSE 8000

# Container healthcheck probe
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Production command: Run Uvicorn with multiple workers and no reload
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
