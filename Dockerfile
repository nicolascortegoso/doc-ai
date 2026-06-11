# =============================================================================
# BASE
# Shared foundation for all stages. Installs system dependencies and uv.
# =============================================================================
FROM python:3.12-slim AS base

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml .
COPY uv.lock* .

# =============================================================================
# DEV
# Development stage. Installs all dependencies including dev/test tooling.
# Source code is mounted at runtime via docker-compose volume.
# =============================================================================
FROM base AS dev

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_SYSTEM_PYTHON=1

RUN uv sync --all-extras

# =============================================================================
# PROD
# Production stage. Installs runtime dependencies only.
# =============================================================================
FROM base AS prod

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_SYSTEM_PYTHON=1

RUN uv sync --no-dev

COPY . .

# =============================================================================
# CI
# CI stage. Installs all dependencies and copies source for linting and tests.
# =============================================================================
FROM base AS ci

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_SYSTEM_PYTHON=1

RUN uv sync --all-extras

COPY . .

CMD ["sh", "-c", "ruff check . && pytest --cov=libs --cov-report=term-missing"]
