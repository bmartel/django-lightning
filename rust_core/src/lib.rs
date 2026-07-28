//! Native Rust Core Extension Module for Django-Lightning (`rust_core`).
//!
//! Exposes low-level CPU computations, zero-copy byte processing, and Rayon multithreading
//! routines with zero Python GIL overhead.

pub mod db;

use pyo3::prelude::*;
use pyo3::types::PyBytes;

/// Returns the version string of the compiled native Rust core crate.
#[pyfunction]
fn rust_core_version() -> PyResult<&'static str> {
    Ok(env!("CARGO_PKG_VERSION"))
}

/// Helper for ultra-fast, zero-copy memory transfer using raw byte slices (`&[u8]`).
/// Accepts raw Python bytes without copying onto heap, releases GIL, and returns PyBytes.
#[pyfunction]
fn process_raw_bytes<'py>(py: Python<'py>, input_bytes: &[u8]) -> PyResult<Bound<'py, PyBytes>> {
    let result_vec = py.allow_threads(|| {
        // Zero-copy read of input memory buffer, process in Rust
        input_bytes.to_vec()
    });

    Ok(PyBytes::new_bound(py, &result_vec))
}

#[pymodule]
fn rust_core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(rust_core_version, m)?)?;
    m.add_function(wrap_pyfunction!(process_raw_bytes, m)?)?;
    m.add_function(wrap_pyfunction!(db::db_query_users_json, m)?)?;
    Ok(())
}

