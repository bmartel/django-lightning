//! Native PyO3 FFI Binding for Django-Lightning (`rust_core`).
//!
//! Delegates function execution to workspace domain crates (`db_engine`, `core_utils`, etc.).

use pyo3::prelude::*;
use pyo3::types::PyBytes;

/// Returns the version string of the compiled native Rust core crate.
#[pyfunction]
fn rust_core_version() -> PyResult<&'static str> {
    Ok(env!("CARGO_PKG_VERSION"))
}

/// Helper for ultra-fast, zero-copy memory transfer using raw byte slices (`&[u8]`).
#[pyfunction]
fn process_raw_bytes<'py>(py: Python<'py>, input_bytes: &[u8]) -> PyResult<Bound<'py, PyBytes>> {
    let result_vec = py.allow_threads(|| core_utils::process_raw_bytes_impl(input_bytes));
    Ok(PyBytes::new_bound(py, &result_vec))
}

/// Native SQL query handler delegating execution to the `db_engine` workspace crate.
#[pyfunction]
fn db_query_users_json<'py>(
    py: Python<'py>,
    db_url: String,
    limit: i64,
) -> PyResult<Bound<'py, PyBytes>> {
    let json_bytes = py
        .allow_threads(|| db_engine::db_query_users_json_impl(&db_url, limit))
        .map_err(pyo3::exceptions::PyValueError::new_err)?;

    Ok(PyBytes::new_bound(py, &json_bytes))
}

#[pymodule]
fn rust_core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(rust_core_version, m)?)?;
    m.add_function(wrap_pyfunction!(process_raw_bytes, m)?)?;
    m.add_function(wrap_pyfunction!(db_query_users_json, m)?)?;
    Ok(())
}
