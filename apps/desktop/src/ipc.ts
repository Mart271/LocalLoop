// The only way the UI talks to the core. Command names and DTO types are generated from Rust
// (packages/shared, LL-005), so they cannot drift from the allowlisted command surface.
import { invoke } from "@tauri-apps/api/core";
import type { IpcCommand, IpcError, IpcErrorCode, PingRequest, PingResponse } from "@localloop/shared";

interface CommandMap {
  ping: { request: PingRequest; response: PingResponse };
}

// Compile-time check that every generated command has an entry above, and nothing else does.
type Exact<A, B> = [A] extends [B] ? ([B] extends [A] ? true : false) : false;
const commandMapIsComplete: Exact<keyof CommandMap, IpcCommand> = true;
void commandMapIsComplete;

export type IpcResult<T> = { ok: true; value: T } | { ok: false; error: IpcError };

const ERROR_CODES: readonly IpcErrorCode[] = ["invalid_argument"];

const FALLBACK_ERROR: IpcError = {
  code: "invalid_argument",
  message: "LocalLoop could not complete the request. Nothing was changed.",
};

export function isIpcError(value: unknown): value is IpcError {
  if (typeof value !== "object" || value === null) return false;
  const candidate = value as Record<string, unknown>;
  return (
    typeof candidate.message === "string" &&
    typeof candidate.code === "string" &&
    (ERROR_CODES as readonly string[]).includes(candidate.code)
  );
}

export async function call<C extends IpcCommand>(
  command: C,
  request: CommandMap[C]["request"],
): Promise<IpcResult<CommandMap[C]["response"]>> {
  try {
    const value = await invoke<CommandMap[C]["response"]>(command, { request });
    return { ok: true, value };
  } catch (raw: unknown) {
    return { ok: false, error: isIpcError(raw) ? raw : FALLBACK_ERROR };
  }
}
