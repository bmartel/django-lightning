# Multi-stage Dockerfile for django-lightning powered by django-bolt and uv

# ==============================================================================
# Stage 1: Base Builder Stage
# ==============================================================================
FROM python:3.12-slim-bookworm AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY --from=rust:1-slim /usr/local/cargo /usr/local/cargo
COPY --from=rust:1-slim /usr/local/rustup /usr/local/rustup

ENV RUSTUP_HOME=/usr/local/rustup \
    CARGO_HOME=/usr/local/cargo \
    PATH="/usr/local/cargo/bin:$PATH"


WORKDIR /app


# Copy dependency definition, rust crate, and source code for installation
COPY pyproject.toml README.md ./
COPY rust_core/ ./rust_core/
COPY app/ ./app/
COPY config/ ./config/
COPY manage.py .

# Build production virtual environment, Rust native extension, and install bytecode
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=cache,target=/root/.cargo/registry \
    --mount=type=cache,target=/app/rust_core/target \
    uv venv /app/.venv && \
    uv pip install maturin && \
    uv run maturin build --release --manifest-path rust_core/crates/rust_core_pyo3/Cargo.toml --out /tmp/wheels && \
    uv pip install /tmp/wheels/*.whl && \
    uv pip install --compile-bytecode .



# ==============================================================================
# Stage 2: Development Stage (Target: dev)
# Includes dev dependencies (pytest, ruff) and uv binary for dev workflows
# ==============================================================================
FROM builder AS dev

RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --compile-bytecode -e ".[dev]"

COPY . /app

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=config.settings

EXPOSE 8000

CMD ["uv", "run", "manage.py", "runbolt", "--host", "0.0.0.0", "--port", "8000", "--dev"]

# ==============================================================================
# Stage 3: Production Runtime (Target: runner - Default)
# Ultra-fast, minimal footprint image stripped of uv binary and dev tools
# ==============================================================================
FROM python:3.12-slim-bookworm AS runner

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd -r django && useradd -r -g django django

WORKDIR /app

# Copy production virtualenv and application code
COPY --from=builder /app/.venv /app/.venv
COPY . /app

# Collect static files for Django Admin using virtualenv python directly
RUN mkdir -p /app/staticfiles && \
    chown -R django:django /app && \
    SECRET_KEY=build-dummy-key-12345 /app/.venv/bin/python manage.py collectstatic --noinput

USER django

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONOPTIMIZE=1 \
    DJANGO_SETTINGS_MODULE=config.settings

EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Execute python manage.py runbolt directly for maximum performance & zero wrapper overhead
CMD ["python", "manage.py", "runbolt", "--host", "0.0.0.0", "--port", "8000", "--processes", "4"]
