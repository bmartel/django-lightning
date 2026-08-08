pub mod models;
pub mod queries;

use models::UserRow;
use serde::Serialize;
use sqlx::postgres::{PgPool, PgPoolOptions};
use sqlx::sqlite::{SqlitePool, SqlitePoolOptions};
use std::collections::HashMap;
use std::sync::{OnceLock, RwLock};

static TOKIO_RUNTIME: OnceLock<tokio::runtime::Runtime> = OnceLock::new();

// Connection pools are cached per database URL and reused across calls. Building a fresh
// pool on every query pays full connection-setup cost and leaks file handles under load.
static POOLS: OnceLock<RwLock<HashMap<String, DbPool>>> = OnceLock::new();

/// Backend-agnostic connection pool. Selected automatically from the URL scheme:
/// `postgres://` / `postgresql://` -> Postgres, everything else -> SQLite.
#[derive(Clone)]
pub enum DbPool {
    Sqlite(SqlitePool),
    Postgres(PgPool),
}

fn get_tokio_runtime() -> &'static tokio::runtime::Runtime {
    TOKIO_RUNTIME.get_or_init(|| {
        tokio::runtime::Builder::new_multi_thread()
            .enable_all()
            .build()
            .expect("Failed to build Tokio runtime")
    })
}

fn default_max_connections() -> u32 {
    std::thread::available_parallelism()
        .map(|n| n.get() as u32 * 2)
        .unwrap_or(8)
}

/// Return a cached connection pool for `db_url`, creating it once on first use.
///
/// Reusing pools across calls keeps connections warm and lets sqlx reuse
/// prepared statements, instead of paying connection setup cost per query.
/// sqlx pools are cheap to clone (Arc-backed); build once, then cache.
pub async fn get_pool(db_url: &str) -> Result<DbPool, String> {
    let pools = POOLS.get_or_init(|| RwLock::new(HashMap::new()));

    if let Some(pool) = pools.read().unwrap().get(db_url) {
        return Ok(pool.clone());
    }

    let pool = if db_url.starts_with("postgres://") || db_url.starts_with("postgresql://") {
        DbPool::Postgres(
            PgPoolOptions::new()
                .max_connections(default_max_connections())
                .connect(db_url)
                .await
                .map_err(|e| e.to_string())?,
        )
    } else {
        DbPool::Sqlite(
            SqlitePoolOptions::new()
                .max_connections(default_max_connections())
                .connect(db_url)
                .await
                .map_err(|e| e.to_string())?,
        )
    };

    let mut guard = pools.write().unwrap();
    // Another task may have raced us; keep the first pool inserted.
    let pool = guard.entry(db_url.to_string()).or_insert(pool).clone();
    Ok(pool)
}

// SQL is assembled exclusively from codegen constants (`TABLE_NAME`, `COLUMNS`, `PK`)
// which mirror Django models and already exclude sensitive columns (password hashes,
// key hashes, secrets). User-controlled values only ever enter via bind parameters.
fn build_page_sql(
    table: &str,
    columns: &[&str],
    pk: &str,
    after_id: Option<i64>,
    postgres: bool,
) -> String {
    let cols = columns.join(", ");
    match (after_id, postgres) {
        (Some(_), true) => {
            format!("SELECT {cols} FROM {table} WHERE {pk} > $1 ORDER BY {pk} LIMIT $2")
        }
        (Some(_), false) => {
            format!("SELECT {cols} FROM {table} WHERE {pk} > ? ORDER BY {pk} LIMIT ?")
        }
        (None, true) => format!("SELECT {cols} FROM {table} ORDER BY {pk} LIMIT $1"),
        (None, false) => format!("SELECT {cols} FROM {table} ORDER BY {pk} LIMIT ?"),
    }
}

/// Fetch a keyset-paginated page of rows as raw JSON bytes.
///
/// Generic over any generated model row struct (see `models.rs` / `queries.rs`).
/// Uses `WHERE pk > after_id ORDER BY pk LIMIT n` (index-backed keyset pagination)
/// instead of `OFFSET`, so latency stays flat regardless of table size.
pub async fn fetch_page_json<T>(
    pool: &DbPool,
    table: &str,
    columns: &[&str],
    pk: &str,
    limit: i64,
    after_id: Option<i64>,
) -> Result<Vec<u8>, String>
where
    T: Serialize
        + Send
        + Unpin
        + for<'r> sqlx::FromRow<'r, sqlx::sqlite::SqliteRow>
        + for<'r> sqlx::FromRow<'r, sqlx::postgres::PgRow>,
{
    let rows: Vec<T> = match pool {
        DbPool::Sqlite(p) => {
            let sql = build_page_sql(table, columns, pk, after_id, false);
            let mut q = sqlx::query_as::<_, T>(sqlx::AssertSqlSafe(sql));
            if let Some(id) = after_id {
                q = q.bind(id);
            }
            q.bind(limit).fetch_all(p).await.map_err(|e| e.to_string())?
        }
        DbPool::Postgres(p) => {
            let sql = build_page_sql(table, columns, pk, after_id, true);
            let mut q = sqlx::query_as::<_, T>(sqlx::AssertSqlSafe(sql));
            if let Some(id) = after_id {
                q = q.bind(id);
            }
            q.bind(limit).fetch_all(p).await.map_err(|e| e.to_string())?
        }
    };
    serde_json::to_vec(&rows).map_err(|e| e.to_string())
}

/// Blocking entrypoint for the generic model fetch registry (called from PyO3).
pub fn db_fetch_model_json_impl(
    db_url: &str,
    model: &str,
    limit: i64,
    after_id: Option<i64>,
) -> Result<Vec<u8>, String> {
    let rt = get_tokio_runtime();
    rt.block_on(async {
        let pool = get_pool(db_url).await?;
        queries::fetch_model_page_json(&pool, model, limit, after_id).await
    })
}

/// Run high-speed SQL query returning raw JSON bytes of user models.
///
/// Retained for backwards compatibility; delegates to the generic engine.
pub fn db_query_users_json_impl(db_url: &str, limit: i64) -> Result<Vec<u8>, String> {
    let rt = get_tokio_runtime();
    rt.block_on(async {
        let pool = get_pool(db_url).await?;
        fetch_page_json::<UserRow>(
            &pool,
            UserRow::TABLE_NAME,
            UserRow::COLUMNS,
            UserRow::PK,
            limit,
            None,
        )
        .await
    })
}
