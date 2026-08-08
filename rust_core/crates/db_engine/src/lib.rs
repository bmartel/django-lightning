pub mod models;

use models::UserRow;
use sqlx::sqlite::SqlitePool;
use std::collections::HashMap;
use std::sync::{Mutex, OnceLock};

static TOKIO_RUNTIME: OnceLock<tokio::runtime::Runtime> = OnceLock::new();

// Connection pools are cached per database URL and reused across calls. Building a fresh
// pool on every query paid full connection-setup cost and leaked file handles under load.
static DB_POOLS: OnceLock<Mutex<HashMap<String, SqlitePool>>> = OnceLock::new();

// Explicit, non-sensitive column list. Never `SELECT *`: the underlying table has a
// `password` hash column that must never be serialized back to a caller. This is a
// single static literal (no runtime formatting) so sqlx can prove it is injection-safe.
const USER_QUERY: &str = "SELECT id, last_login, is_superuser, username, first_name, \
    last_name, email, is_staff, is_active, date_joined, bio, avatar_url, created_at, \
    updated_at FROM app_user LIMIT ?";

fn get_tokio_runtime() -> &'static tokio::runtime::Runtime {
    TOKIO_RUNTIME.get_or_init(|| {
        tokio::runtime::Builder::new_multi_thread()
            .enable_all()
            .build()
            .expect("Failed to build Tokio runtime")
    })
}

async fn get_pool(db_url: &str) -> Result<SqlitePool, String> {
    let pools = DB_POOLS.get_or_init(|| Mutex::new(HashMap::new()));
    if let Some(pool) = pools.lock().unwrap().get(db_url) {
        return Ok(pool.clone());
    }
    // sqlx pools are cheap to clone (Arc-backed); build once, then cache.
    let pool = SqlitePool::connect(db_url)
        .await
        .map_err(|e| e.to_string())?;
    pools
        .lock()
        .unwrap()
        .insert(db_url.to_string(), pool.clone());
    Ok(pool)
}

/// Run high-speed SQL query returning raw JSON bytes of user models
pub fn db_query_users_json_impl(db_url: &str, limit: i64) -> Result<Vec<u8>, String> {
    let rt = get_tokio_runtime();
    rt.block_on(async {
        let pool = get_pool(db_url).await?;
        let users = sqlx::query_as::<_, UserRow>(USER_QUERY)
            .bind(limit)
            .fetch_all(&pool)
            .await
            .map_err(|e| e.to_string())?;
        serde_json::to_vec(&users).map_err(|e| e.to_string())
    })
}
