pub mod models;

use models::UserRow;
use std::sync::OnceLock;

static TOKIO_RUNTIME: OnceLock<tokio::runtime::Runtime> = OnceLock::new();

fn get_tokio_runtime() -> &'static tokio::runtime::Runtime {
    TOKIO_RUNTIME.get_or_init(|| {
        tokio::runtime::Builder::new_multi_thread()
            .enable_all()
            .build()
            .expect("Failed to build Tokio runtime")
    })
}

/// Run high-speed SQL query returning raw JSON bytes of user models
pub fn db_query_users_json_impl(db_url: &str, limit: i64) -> Result<Vec<u8>, String> {
    let rt = get_tokio_runtime();
    rt.block_on(async {
        use sqlx::sqlite::SqlitePoolOptions;
        let pool = SqlitePoolOptions::new()
            .connect(db_url)
            .await
            .map_err(|e| e.to_string())?;
        let users = sqlx::query_as::<_, UserRow>("SELECT * FROM app_user LIMIT ?")
            .bind(limit)
            .fetch_all(&pool)
            .await
            .map_err(|e| e.to_string())?;
        serde_json::to_vec(&users).map_err(|e| e.to_string())
    })
}
