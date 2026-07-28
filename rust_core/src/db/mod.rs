pub mod models;

use models::UserRow;
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::PyBytes;

use std::sync::OnceLock;

static TOKIO_RUNTIME: OnceLock<tokio::runtime::Runtime> = OnceLock::new();

fn get_tokio_runtime() -> &'static tokio::runtime::Runtime {
    TOKIO_RUNTIME.get_or_init(|| {
        tokio::runtime::Builder::new_multi_thread()
            .enable_all()
            .build()
            .expect("Failed to build global Tokio runtime")
    })
}

/// High-performance database query execution using Sqlx and Tokio runtime.
/// Releases Python GIL during database I/O and returns serialized JSON bytes.
#[pyfunction]
pub fn db_query_users_json<'py>(
    py: Python<'py>,
    db_url: String,
    limit: i64,
) -> PyResult<Bound<'py, PyBytes>> {
    let json_bytes = py.allow_threads(|| {
        let rt = get_tokio_runtime();
        rt.block_on(async {

            if db_url.starts_with("postgres://") || db_url.starts_with("postgresql://") {

                use sqlx::postgres::PgPoolOptions;
                let pool = PgPoolOptions::new()
                    .max_connections(5)
                    .connect(&db_url)
                    .await
                    .map_err(|e| format!("PgPool connect error: {}", e))?;

                let users = sqlx::query_as::<_, UserRow>(
                    "SELECT id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined, bio, avatar_url, created_at, updated_at FROM app_user ORDER BY date_joined DESC LIMIT $1"
                )
                .bind(limit)
                .fetch_all(&pool)
                .await
                .map_err(|e| format!("Query error: {}", e))?;

                serde_json::to_vec(&users).map_err(|e| format!("Serialization error: {}", e))
            } else {
                use sqlx::sqlite::SqlitePoolOptions;
                let pool = SqlitePoolOptions::new()
                    .max_connections(5)
                    .connect(&db_url)
                    .await
                    .map_err(|e| format!("SqlitePool connect error: {}", e))?;

                let users = sqlx::query_as::<_, UserRow>(
                    "SELECT id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined, bio, avatar_url, created_at, updated_at FROM app_user ORDER BY date_joined DESC LIMIT ?"
                )
                .bind(limit)
                .fetch_all(&pool)
                .await
                .map_err(|e| format!("Query error: {}", e))?;

                serde_json::to_vec(&users).map_err(|e| format!("Serialization error: {}", e))
            }
        })
    }).map_err(PyValueError::new_err)?;

    Ok(PyBytes::new_bound(py, &json_bytes))
}
