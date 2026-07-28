//! High-Performance Native Rust Core Extension for Django-Lightning.
//!
//! Designed for CPU-bound computations, parallel data transformations,
//! and low-level routines with zero Python GIL contention.

use pyo3::prelude::*;
use rayon::prelude::*;

/// Executes a list of string processing operations in parallel across CPU cores,
/// explicitly releasing the Python Global Interpreter Lock (GIL).
#[pyfunction]
fn parallel_transform_strings(py: Python<'_>, items: Vec<String>) -> PyResult<Vec<String>> {
    py.allow_threads(|| {
        Ok(items
            .into_par_iter()
            .map(|s| s.trim().to_uppercase())
            .collect())
    })
}

/// Executes parallel vector math metrics, releasing the Python GIL.
#[pyfunction]
fn parallel_sum_floats(py: Python<'_>, values: Vec<f64>) -> PyResult<f64> {
    let sum = py.allow_threads(|| values.par_iter().sum::<f64>());
    Ok(sum)
}

/// PyO3 Native Extension Module Entrypoint
#[pymodule]
fn rust_core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(parallel_transform_strings, m)?)?;
    m.add_function(wrap_pyfunction!(parallel_sum_floats, m)?)?;
    Ok(())
}
