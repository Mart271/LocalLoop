//! The IPC command surface (component-design §11). DTOs here are exported to TypeScript by ts-rs
//! into `packages/shared` (LL-005); never write those types by hand.

pub mod commands;
pub mod dto;

pub use dto::{IpcCommand, IpcError, IpcErrorCode, PingRequest, PingResponse};
