FROM python:3.12-slim AS base

RUN apt-get update && apt-get install -y --no-install-recommends \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install uv

WORKDIR /app

COPY pyproject.toml .

# ── dev ────────────────────────────────────────────────────────────────────────
FROM base AS dev

RUN uv pip install --system -e ".[dev]"

COPY . .

CMD ["pytest"]

# ── prod ───────────────────────────────────────────────────────────────────────
FROM base AS prod

RUN uv pip install --system .

COPY libs/ libs/

# ── ci ─────────────────────────────────────────────────────────────────────────
FROM base AS ci

RUN uv pip install --system -e ".[dev]"

COPY . .

CMD ["pytest", "--cov=libs", "--cov-report=xml"]
