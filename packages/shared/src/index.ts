// Re-exports of the ts-rs generated IPC types. Every file in ./generated must be listed here;
// a Rust test (`shared_index_exports_every_generated_type`) fails otherwise.
export type { IpcCommand } from "./generated/IpcCommand";
export type { IpcError } from "./generated/IpcError";
export type { IpcErrorCode } from "./generated/IpcErrorCode";
export type { PingRequest } from "./generated/PingRequest";
export type { PingResponse } from "./generated/PingResponse";
