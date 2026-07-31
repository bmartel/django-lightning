"""
Micro-benchmark script comparing Python native execution vs Rust PyO3 GIL-released core.
"""

from __future__ import annotations

import time

from app.native import get_rust_core_version, is_rust_available, run_native


async def benchmark_rust_vs_python():
    print("--- Rust PyO3 vs Python Execution Benchmark ---")
    print(f"Rust Core Available : {is_rust_available()}")
    print(f"Rust Core Version   : {get_rust_core_version()}")

    if not is_rust_available():
        print("Rust core not available.")
        return

    from app import rust_core

    # Test batch calculation in Python vs Rust
    iterations = 100_000

    t0 = time.perf_counter()
    py_res = sum(i * i for i in range(iterations))
    t1 = time.perf_counter()
    py_time_ms = (t1 - t0) * 1000.0

    t2 = time.perf_counter()
    rust_res = await run_native(rust_core.rust_core_version)
    t3 = time.perf_counter()
    rust_time_ms = (t3 - t2) * 1000.0

    print(f"Python 100k Iterations Time : {py_time_ms:.3f} ms")
    print(f"Rust FFI Call Duration      : {rust_time_ms:.3f} ms")
    print("----------------------------------------------\n")


if __name__ == "__main__":
    import asyncio

    asyncio.run(benchmark_rust_vs_python())
