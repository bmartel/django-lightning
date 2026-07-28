---
name: django-bolt-rust-interop
description: Comprehensive guide on writing, managing, compiling, and running native PyO3 Rust extension modules with GIL releasing (py.allow_threads), Rayon parallel processing, Python fallback layer, optional scaffolding, and Docker multi-stage packaging in django-lightning.
compatibility: Agentic coding assistants extending django-lightning applications with native Rust acceleration.
metadata:
  category: rust-interop
  tags: [django, django-bolt, rust, pyo3, maturin, rayon, gil-release, native-extensions]
---

# Django-Bolt Native Rust Module Interop Guide

## Overview & Architecture

While `django-bolt` speeds up HTTP request routing and JSON serialization using Rust under the hood (~60k+ RPS), application-level logic (e.g. data processing, vector computations, cryptography, token parsing, image/media transformations) executes within Python's runtime and Global Interpreter Lock (GIL).

When lower-level, high-throughput, or CPU-bound operations are required in API handlers or background worker jobs, `django-lightning` provides an in-process **PyO3 + Maturin Native Extension Architecture** via the `rust_core` crate.

---

## 🛠 1. How to Write Native Rust Functions (`rust_core/src/`)

All native Rust code resides in `rust_core/src/lib.rs` (or sub-modules under `rust_core/src/`).

### Step 1: Define `#[pyfunction]` with GIL Releasing
Always wrap CPU-bound operations in `py.allow_threads(|| { ... })`. Releasing the GIL guarantees that Rust's multithreaded parallel loops (`rayon`) execute across all CPU cores without blocking `django-bolt`'s async event loop or `SAQ` worker process.

```rust
use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use rayon::prelude::*;

/// Example: High-speed parallel data processing releasing Python GIL.
#[pyfunction]
fn process_dataset_batch(py: Python<'_>, records: Vec<String>) -> PyResult<Vec<String>> {
    if records.is_empty() {
        return Err(PyValueError::new_err("Record batch cannot be empty"));
    }

    // Release GIL: Runs across all CPU cores in parallel via Rayon
    let results = py.allow_threads(|| {
        records
            .into_par_iter()
            .map(|s| s.trim().to_uppercase())
            .collect()
    });

    Ok(results)
}
```

### Step 2: Register Function in `#[pymodule]`
Expose your new Rust function to Python inside the module initializer:

```rust
#[pymodule]
fn rust_core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(process_dataset_batch, m)?)?;
    Ok(())
}
```

### Step 3: Data Type Interop Rules
| Python Type | PyO3 Rust Input Type | PyO3 Rust Return Type | Notes |
| :--- | :--- | :--- | :--- |
| `str` | `String` / `&str` | `String` / `PyResult<String>` | UTF-8 conversion |
| `bytes` | `Vec<u8>` / `&[u8]` | `Vec<u8>` | Zero-copy byte slices where applicable |
| `list[T]` | `Vec<T>` | `Vec<T>` | Converts to Rust `Vec` |
| `dict[K, V]` | `HashMap<K, V>` | `HashMap<K, V>` | Converts to `std::collections::HashMap` |
| `int` | `i64` / `u64` / `usize` | `i64` / `usize` | Fixed-size integers |
| `float` | `f64` | `f64` | Double-precision floats |

---

## 🐍 2. How to Manage & Expose Modules in Python (`app/native.py`)

All Python access to `rust_core` is managed through `app/native.py` to ensure clean fallback behavior and IDE type hints.

### Step 1: Import with Graceful Fallback (`app/native.py`)
```python
"""
High-Performance Native Rust Interop Module for Django-Lightning.
"""

from __future__ import annotations

import asyncio
from typing import Any, Callable, TypeVar

R = TypeVar("R")

try:
    from app import rust_core

    HAS_RUST_CORE = True
except ImportError:
    rust_core = None
    HAS_RUST_CORE = False


def is_rust_available() -> bool:
    """Check if compiled native Rust core is available in the current environment."""
    return HAS_RUST_CORE


async def run_native(func: Callable[..., R], *args: Any, **kwargs: Any) -> R:
    """
    Execute a native PyO3 Rust function asynchronously in a background thread.
    Prevents event-loop stalls when invoking GIL-releasing C-extensions.
    """
    if kwargs:
        return await asyncio.to_thread(func, *args, **kwargs)
    return await asyncio.to_thread(func, *args)
```

### Step 2: Add IDE Type Stubs (`app/native.pyi`)
Keep IDE autocomplete and mypy/ruff checks synchronized by declaring signature stubs in `app/native.pyi`:

```python
from typing import Any, Callable, TypeVar

R = TypeVar("R")


def is_rust_available() -> bool: ...
def get_rust_core_version() -> str | None: ...
async def run_native(func: Callable[..., R], *args: Any, **kwargs: Any) -> R: ...
```

---

## ⚡ 3. How to Run Native Rust Code in APIs & SAQ Workers

### In Async API Routes (`django-bolt`)
Use `run_native` to offload computation cleanly without blocking `django-bolt`'s async worker thread:

```python
from django_bolt import BoltAPI
import msgspec
from app.native import is_rust_available, run_native
from app import rust_core


@api.post("/api/v1/process-batch")
async def handle_process_batch(payload: BatchPayloadReq) -> BatchPayloadOut:
    if not is_rust_available():
        # Fallback Python logic or degraded response
        return BatchPayloadOut(results=[s.upper() for s in payload.records])

    # Run native Rust function in thread pool (GIL released inside Rust)
    results = await run_native(rust_core.process_dataset_batch, payload.records)
    return BatchPayloadOut(results=results)
```

### In SAQ Background Worker Tasks (`app/tasks.py`)
```python
from app.native import is_rust_available, run_native
from app import rust_core


async def process_heavy_worker_job(ctx: dict, records: list[str]) -> dict:
    """SAQ background task processing large dataset via Rust multithreading."""
    if not is_rust_available():
        return {"status": "error", "message": "Rust native core not available"}

    results = await run_native(rust_core.process_dataset_batch, records)
    return {"status": "success", "processed": len(results)}
```

---

## 💻 4. Developer Workflow & CLI Tooling

Execute all compilation and testing tasks using `just` / `uv`:

- **`just rust-dev`**: Runs `uv run maturin develop`. Compiles `rust_core` in debug mode and installs editable extension into `.venv`.
- **`just rust-build`**: Runs `uv run maturin develop --release`. Compiles optimized release build.
- **`just rust-test`**: Runs `cargo test --manifest-path rust_core/Cargo.toml`. Executes Rust-native unit tests directly.
- **`uv run pytest -v`**: Runs pytest suite verifying Python integration.

---

## 📦 5. Scaffolding & Docker Build Pipeline

### Optional Scaffolding (`--no-rust`)
When generating projects using `create-django-bolt` CLI or `scripts/create-project.py`:
- Pass `--no-rust` to generate pure Python applications stripped of `rust_core/`, `maturin`, and cargo build steps.
- `is_rust_available()` returns `False` cleanly without throwing errors.

### Production Multi-Stage Docker Build (`Dockerfile`)
```dockerfile
FROM python:3.12-slim-bookworm AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev curl cargo rustc && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
WORKDIR /app

COPY pyproject.toml README.md ./
COPY rust_core/ ./rust_core/
COPY app/ ./app/

# Build PyO3 wheel using cargo caching mounts
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=cache,target=/root/.cargo/registry \
    --mount=type=cache,target=/app/rust_core/target \
    uv venv /app/.venv && \
    uv pip install maturin && \
    uv run maturin develop --release && \
    uv pip install --compile-bytecode .
```
