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

### Step 3: Zero-Copy & High-Performance Data Transfer Strategies
To maximize throughput and minimize RAM allocations between Python and Rust:

1. **Zero-Copy Byte Slices (`&[u8]`)**:
   Pass raw Python `bytes` or `bytearray` directly into Rust using `&[u8]`. Rust inspects Python memory without copying bytes onto the Rust heap.
2. **Msgspec JSON Buffer FFI (`run_native_json`)**:
   Instead of converting large nested Python dictionaries into PyDict FFI objects (which creates millions of PyObjects and incurs heavy FFI overhead), serialize Structs with `msgspec.json.encode()`, pass raw UTF-8 bytes into Rust (`serde_json`), process, and return bytes.
   **Speedup**: Up to **10x–50x faster** than creating PyDict objects across the FFI boundary!

| Python Type | PyO3 Rust Input Type | PyO3 Rust Return Type | Notes |
| :--- | :--- | :--- | :--- |
| `bytes` / `bytearray` | `&[u8]` | `Bound<'py, PyBytes>` | **Zero-Copy Buffer View** |
| `msgspec.Struct` | `&[u8]` (via `msgspec.json`) | `Bound<'py, PyBytes>` | **10x-50x Faster JSON FFI** |
| `str` | `String` / `&str` | `String` / `PyResult<String>` | UTF-8 conversion |
| `list[T]` | `Vec<T>` | `Vec<T>` | Converts to Rust `Vec` |
| `dict[K, V]` | `HashMap<K, V>` | `HashMap<K, V>` | Converts to `HashMap` |

---

## 🐍 2. How to Manage & Expose Modules in Python (`app/native.py`)

All Python access to `rust_core` is managed through `app/native.py` to ensure clean fallback behavior and IDE type hints.

### Step 1: Type-Safe `@native_async` Decorator (`app/native.py`)
Pre-wrap PyO3 Rust functions with `@native_async` to preserve **100% exact type hints**, IDE autocomplete, docstrings, and automatic threadpool delegation:

```python
"""
High-Performance Native Rust Interop Module for Django-Lightning.
"""

from __future__ import annotations

import asyncio
import functools
from collections.abc import Awaitable, Callable
from typing import Any, ParamSpec, TypeVar
import msgspec

P = ParamSpec("P")
R = TypeVar("R")
T = TypeVar("T")

try:
    from app import rust_core

    HAS_RUST_CORE = True
except ImportError:
    rust_core = None
    HAS_RUST_CORE = False


def native_async(func: Callable[P, R]) -> Callable[P, Awaitable[R]]:
    """
    Decorator that wraps a synchronous PyO3 Rust function into a fully
    type-safe, non-blocking async function pre-configured for threadpool execution.
    """
    @functools.wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        if kwargs:
            return await asyncio.to_thread(func, *args, **kwargs)
        return await asyncio.to_thread(func, *args)

    return wrapper

# Export pre-wrapped, fully type-safe async native functions
if HAS_RUST_CORE:
    process_dataset_batch = native_async(rust_core.process_dataset_batch)
```

### Step 2: Add IDE Type Stubs (`app/native.pyi`)
Keep IDE autocomplete and mypy/ruff checks synchronized by declaring signature stubs in `app/native.pyi`:

```python
from collections.abc import Awaitable, Callable
from typing import Any, ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")
T = TypeVar("T")

def is_rust_available() -> bool: ...
def get_rust_core_version() -> str | None: ...
def native_async(func: Callable[P, R]) -> Callable[P, Awaitable[R]]: ...
async def run_native[R](func: Callable[..., R], *args: Any, **kwargs: Any) -> R: ...
async def run_native_json(
    native_func: Callable[[bytes], bytes], payload: Any, response_type: type[T]
) -> T: ...
```

---

## ⚡ 3. How to Run Native Rust Code in APIs & SAQ Workers

### Fully Type-Safe Pre-Wrapped Invocation
Because functions are pre-wrapped with `@native_async`, developers simply call them directly with full autocomplete and type safety:

```python
from django_bolt import BoltAPI
from app.native import is_rust_available, process_dataset_batch

@api.post("/api/v1/process-batch")
async def handle_process_batch(payload: BatchPayloadReq) -> BatchPayloadOut:
    if not is_rust_available():
        return BatchPayloadOut(results=[s.upper() for s in payload.records])

    # Direct, 100% type-safe, non-blocking async execution with IDE autocomplete!
    results = await process_dataset_batch(payload.records)
    return BatchPayloadOut(results=results)
```

### Zero-Copy JSON Byte FFI Invocation (`run_native_json`)
```python
from app.native import run_native_json
from app import rust_core

@api.post("/api/v1/fast-transform")
async def handle_fast_transform(payload: HeavyStruct) -> HeavyStructOut:
    # Serializes directly to UTF-8 bytes and decodes in msgspec for 50x speed gains
    return await run_native_json(rust_core.process_json_payload, payload, HeavyStructOut)
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
