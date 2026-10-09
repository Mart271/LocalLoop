//! Tauri command handlers. Thin: validate, call the core, map errors.

use super::dto::{IpcError, PingRequest, PingResponse};

/// Health check: proves the UI can reach the core through the allowlisted IPC surface.
///
/// # Errors
/// Returns an [`IpcError`] when the request fails validation.
#[tauri::command]
pub fn ping(request: PingRequest) -> Result<PingResponse, IpcError> {
    request.validate()?;
    Ok(PingResponse {
        nonce: request.nonce,
        core_version: env!("CARGO_PKG_VERSION").to_owned(),
    })
}
