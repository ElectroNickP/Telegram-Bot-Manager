FROM python:3.11-slim as builder

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.7.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1

# Install system deps
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        curl \
        build-essential

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="$POETRY_HOME/bin:$PATH"

# Copy dependencies
COPY pyproject.toml poetry.lock* ./

# Install deps
RUN poetry install --no-root --only main

# Runtime stage
FROM python:3.11-slim as runtime

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"

# Install runtime deps (e.g. libpq for asyncpg if needed, though asyncpg is pure python mostly but might need deps)
# Actually asyncpg is binary, but wheel should work.
# Installing curl for healthchecks if needed
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy venv from builder
COPY --from=builder /app/.venv ./.venv

# Copy application code
COPY . .

# Default command (can be overridden)
CMD ["uvicorn", "src.web.app:app", "--host", "0.0.0.0", "--port", "8000"]
