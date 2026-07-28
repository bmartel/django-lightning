---
name: django-bolt-rust-interop
description: Native Rust core integration, PyO3 bindings, GIL releasing (py.allow_threads), Rayon parallel processing, optional scaffolding, and packaging best practices for django-lightning applications.
compatibility: Agentic coding assistants extending django-lightning applications with native Rust acceleration.
metadata:
  category: rust-interop
  tags: [django, django-bolt, rust, pyo3, maturin, rayon, gil-release, native-extensions]
---

# Django-Bolt & Native Rust Interop Architecture

## Overview & Core Principles

While `django-bolt` speeds up request routing and serialization using Rust under the hood (~60k+ RPS), application logic (data processing, cryptography, heavy math, streaming batch transformations) still executes inside Python's runtime and Global Interpreter Lock (GIL).

Integrating a native Rust crate (`rust_core`) via **PyO3** and **Maturin** allows executing CPU-heavy algorithms in-process with **zero IPC overhead** while **explicitly releasing the GIL** (`py.allow_threads`) so that background workers and async API loops run at full speed without thread blocking.

---

## Critical Best Practices

1. **Mandatory GIL Releasing (`py.allow_threads`)**:
   Always wrap CPU-bound operations in `py.allow_threads(|| { ... })`. Releasing the GIL guarantees that Rust's multithreaded parallel loops (`rayon`) run across all CPU cores without blocking `django-bolt`'s async event loop or `SAQ` background worker tasks.

2. **Clean Fallback Architecture (`app/native.py`)**:
   Always provide a Python wrapper in `app/native.py` with fallback implementations or clear runtime error guards when `rust_core` is uncompiled or excluded.
   ```python
   try:
       from app import rust_core

       HAS_RUST_CORE = True
   except ImportError:
       rust_core = None
       HAS_RUST_CORE = False


   def is_rust_available() -> bool:
       return HAS_RUST_CORE
   ```

3. **Optional Scaffolding Support**:
   Rust core integration must remain optional in scaffolded projects. When using `create-django-bolt` CLI or `scripts/create-project.py`, users can specify `--no-rust` to generate pure Python applications stripped of `rust_core/`, `maturin`, and cargo build stages.

4. **Async Threadpool Delegation**:
   When invoking Rust functions from Python `async def` API routes or worker jobs, delegate execution to `asyncio.to_thread(...)` so the Python event loop delegates the GIL-releasing C call cleanly.

---

## Rust Core Crate Structure (`rust_core/`)

### 1. `rust_core/Cargo.toml`
```toml
[package]
name = "rust_core"
version = "0.1.0"
edition = "2021"

[lib]
name = "rust_core"
crate-type = ["cdylib"]

[dependencies]
pyo3 = { version = "0.22", features = ["extension-module", "abi3-py312"] }
rayon = "1.10"
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"
```

### 2. `rust_core/src/lib.rs`
```rust
use pyo3::prelude::*;
use rayon::prelude::*;

/// Parallel string transformation releasing Python GIL.
#[pyfunction]
fn parallel_transform_strings(py: Python<'_>, items: Vec<String>) -> PyResult<Vec<String>> {
    py.allow_threads(|| {
        Ok(items
            .into_par_iter()
            .map(|s| s.trim().to_uppercase())
            .collect())
    })
}

/// Parallel float sum releasing Python GIL.
#[pyfunction]
fn parallel_sum_floats(py: Python<'_>, values: Vec<f64>) -> PyResult<f64> {
    let sum = py.allow_threads(|| values.par_iter().sum::<f64>());
    Ok(sum)
}

#[pymodule]
fn rust_core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(parallel_transform_strings, m)?)?;
    m.add_function(wrap_pyfunction!(parallel_sum_floats, m)?)?;
    Ok(())
}
```

---

## Pyproject & Developer Loop Workflow

### 1. Build System (`pyproject.toml`)
```toml
[build-system]
requires = ["maturin>=1.5,<2.0"]
build-backend = "maturin"

[tool.maturin]
manifest-path = "rust_core/Cargo.toml"
python-packages = ["app"]
module-name = "app.rust_core"
```

### 2. Developer Commands (`justfile`)
- **`just rust-dev`**: `uv run maturin develop` (compiles in debug mode for rapid dev)
- **`just rust-build`**: `uv run maturin develop --release` (compiles optimized release build)
- **`just rust-test`**: `cargo test --manifest-path rust_core/Cargo.toml` (runs native cargo unit tests)

---

## Using Rust in API Routes & SAQ Workers

### API Route Example (`app/routes/rust_demo.py`)
```python
from django_bolt import BoltAPI
import msgspec
from app.native import aparallel_transform_strings, is_rust_available


class ItemsReq(msgspec.Struct):
    items: list[str]


@api.post("/api/rust/transform")
async def handle_transform(payload: ItemsReq):
    results = await aparallel_transform_strings(payload.items)
    return {
        "results": results,
        "engine": "Rayon Rust" if is_rust_available() else "Python Fallback",
    }
```

### SAQ Worker Task Example (`app/tasks.py`)
```python
@task
async def run_heavy_batch_job(ctx: dict, values: list[float]) -> dict:
    from app.native import aparallel_sum_floats

    total = await aparallel_sum_floats(values)
    return {"status": "success", "sum": total}
```
