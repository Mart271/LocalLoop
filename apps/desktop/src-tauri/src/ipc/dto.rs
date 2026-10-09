//! Typed, validated data transfer objects for IPC.

use serde::{Deserialize, Serialize};
use ts_rs::TS;

/// Every command the UI may invoke. The TypeScript union generated from this enum is the only
/// way the UI names a command, so names cannot drift between Rust and TypeScript.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize, TS)]
#[serde(rename_all = "snake_case")]
#[ts(export, export_to = "IpcCommand.ts")]
pub enum IpcCommand {
    /// Health check of the core.
    Ping,
}

impl IpcCommand {
    /// All commands, in the order they are registered.
    pub const ALL: [Self; 1] = [Self::Ping];

    /// The Tauri command name.
    #[must_use]
    pub const fn name(self) -> &'static str {
        match self {
            Self::Ping => "ping",
        }
    }
}

/// Maximum length of the ping nonce.
pub const MAX_NONCE_LEN: usize = 64;

/// Request for [`IpcCommand::Ping`].
#[derive(Debug, Clone, PartialEq, Eq, Deserialize, TS)]
#[serde(deny_unknown_fields, rename_all = "camelCase")]
#[ts(export, export_to = "PingRequest.ts")]
pub struct PingRequest {
    /// Caller-chosen token echoed back, 1 to 64 ASCII letters, digits, or `-`.
    pub nonce: String,
}

impl PingRequest {
    /// Validates the request at the IPC boundary.
    ///
    /// # Errors
    /// Returns [`IpcErrorCode::InvalidArgument`] when the nonce is empty, too long, or contains
    /// characters other than ASCII letters, digits, and `-`.
    pub fn validate(&self) -> Result<(), IpcError> {
        let ok_len = !self.nonce.is_empty() && self.nonce.len() <= MAX_NONCE_LEN;
        let ok_chars = self.nonce.bytes().all(|b| b.is_ascii_alphanumeric() || b == b'-');
        if ok_len && ok_chars {
            Ok(())
        } else {
            Err(IpcError::new(
                IpcErrorCode::InvalidArgument,
                "The request was not accepted because its nonce is not 1 to 64 letters, digits, or dashes.",
            ))
        }
    }
}

/// Response for [`IpcCommand::Ping`].
#[derive(Debug, Clone, PartialEq, Eq, Serialize, TS)]
#[serde(rename_all = "camelCase")]
#[ts(export, export_to = "PingResponse.ts")]
pub struct PingResponse {
    /// The nonce from the request.
    pub nonce: String,
    /// Version of the LocalLoop core that answered.
    pub core_version: String,
}

/// Error categories shown to the UI. Messages are plain language (NFR-027).
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, TS)]
#[serde(rename_all = "snake_case")]
#[ts(export, export_to = "IpcErrorCode.ts")]
pub enum IpcErrorCode {
    /// The arguments failed validation.
    InvalidArgument,
}

/// Error returned by any IPC command.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, TS, thiserror::Error)]
#[serde(rename_all = "camelCase")]
#[ts(export, export_to = "IpcError.ts")]
#[error("{message}")]
pub struct IpcError {
    /// Machine-readable category.
    pub code: IpcErrorCode,
    /// What happened and what the user can do next.
    pub message: String,
}

impl IpcError {
    /// Creates an error.
    #[must_use]
    pub fn new(code: IpcErrorCode, message: impl Into<String>) -> Self {
        Self {
            code,
            message: message.into(),
        }
    }
}
