# Multi-stage Dockerfile for django-lightning powered by django-bolt and uv

# Stage 1: Build virtualenv with uv
FROM python:3.12-slim-bookworm AS builder

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv for ultra-fast dependency resolution and virtual environment creation
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy dependency manifests
COPY pyproject.toml .

# Sync dependencies using uv into virtualenv
RUN uv venv /app/.venv && \
    uv pip install .

# Stage 2: Final lightweight runtime image
FROM python:3.12-slim-bookworm AS runner

# Install runtime dependencies and uv
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Create non-root user for security
RUN groupadd -r django && useradd -r -g django django

WORKDIR /app

# Copy virtual environment and application code
COPY --from=builder /app/.venv /app/.venv
COPY . /app

# Ensure proper permissions and collect static files for Django Admin
RUN chown -R django:django /app && \
    SECRET_KEY=build-dummy-key-12345 uv run manage.py collectstatic --noinput

USER django

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=config.settings

EXPOSE 8000

# Healthcheck endpoint
HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run native django-bolt server with uv (runbolt is the sole server required)
CMD ["uv", "run", "manage.py", "runbolt", "--host", "0.0.0.0", "--port", "8000", "--processes", "4"]
