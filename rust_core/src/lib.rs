//! Native Rust Core Extension Module for Django-Lightning (`rust_core`).
//!
//! Add custom high-performance PyO3 functions here for low-level CPU computations,
//! image/crypto processing, or data transformations with zero Python GIL overhead.

use pyo3::prelude::*;

/// Returns the version string of the compiled native Rust core crate.
#[pyfunction]
fn rust_core_version() -> PyResult<&'static str> {
    Ok(env!("CARGO_PKG_VERSION"))
}

#[pymodule]
fn rust_core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(rust_core_version, m)?)?;
    Ok(())
}
