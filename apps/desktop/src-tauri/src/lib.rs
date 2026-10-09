//! LocalLoop desktop application: the composition root (component-design §3.10).
//!
//! Command handlers are thin: validate the DTO, call a core service, map errors to user-facing
//! messages. Only the commands in [`ipc::IpcCommand`] exist; each also needs a permission in
//! `capabilities/main.json` (NFR-014).
#![forbid(unsafe_code)]

pub mod ipc;

/// Builds the Tauri application with the allowlisted command handlers.
pub fn builder<R: tauri::Runtime>() -> tauri::Builder<R> {
    tauri::Builder::<R>::new().invoke_handler(tauri::generate_handler![ipc::commands::ping])
}

/// Runs the desktop application until the user quits.
///
/// # Errors
/// Returns an error when the window or runtime cannot be created.
pub fn run() -> Result<(), tauri::Error> {
    builder().run(tauri::generate_context!())
}
