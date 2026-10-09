//! LocalLoop desktop application: the composition root (component-design §3.10).
//!
//! Command handlers are thin: validate the DTO, call a core service, map errors to user-facing
//! messages. Only the commands in [`ipc::IpcCommand`] exist; each also needs a permission in
//! `capabilities/main.json` (NFR-014).
#![forbid(unsafe_code)]

pub mod ipc;

/// Registers the allowlisted command handlers on a builder.
pub fn builder_with<R: tauri::Runtime>(builder: tauri::Builder<R>) -> tauri::Builder<R> {
    builder.invoke_handler(tauri::generate_handler![ipc::commands::ping])
}

/// Runs the desktop application until the user quits.
///
/// # Errors
/// Returns an error when the window or runtime cannot be created.
pub fn run() -> Result<(), tauri::Error> {
    builder_with(tauri::Builder::default()).run(tauri::generate_context!())
}
