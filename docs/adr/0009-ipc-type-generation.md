# ADR-0009: Generate IPC TypeScript types from Rust with ts-rs

| Field | Value |
|---|---|
| Status | Proposed |
| Date | 2026-10-09 |
| Deciders | Project owner (pending review) |
| Related requirements | NFR-014, NFR-033 |

## Context

The UI and the core exchange typed DTOs over Tauri IPC. LL-005 requires these types to be generated from the Rust definitions, never written by hand, so the UI and the allowlisted command surface (component-design §11) cannot drift apart. The two candidates named in SYSTEM_ARCHITECTURE §7.1 are `ts-rs` and `tauri-specta`.

## Decision

Use **ts-rs** (MIT) to export every IPC DTO, error type, and the `IpcCommand` enum from `apps/desktop/src-tauri/src/ipc/dto.rs` into `packages/shared/src/generated`.

- The command *names* are generated too: `IpcCommand` becomes a TypeScript string union, and the UI's typed `call()` wrapper only accepts members of it. A compile-time check in `apps/desktop/src/ipc.ts` fails if the wrapper's command map and the union differ.
- A Rust test checks that the command list agrees in `build.rs` (Tauri app manifest), the single capability file, and the isolation hook.
- `pnpm gen:types` regenerates the files; CI regenerates them and fails on any difference (LL-005).

## Consequences

- Positive: stable, widely used crate with semver releases; generated files are plain types reviewed in diffs; no runtime code in `packages/shared`.
- Negative: ts-rs does not generate the `invoke` wrappers, so `ipc.ts` holds a small hand-written command map. It is checked at compile time against the generated union, so drift is still caught.
- Follow-up: workflow-definition types are added in M1.1 and must agree with the JSON Schema.

## Alternatives considered

| Option | Why not chosen |
|---|---|
| tauri-specta 2 | Generates typed `invoke` wrappers, but its Tauri 2 line is still a release candidate (2.0.0-rc.25 at the time of writing); a pre-release in the security-relevant IPC path is avoidable |
| Hand-written TypeScript types | Drift between UI and core is exactly what LL-005 forbids |
| JSON Schema → TypeScript | Adds a second source of truth for IPC types |

## Validation

`cargo test -p localloop-desktop` (allowlist agreement, index exports), the UI typecheck, and the CI drift check. Revisit if tauri-specta publishes a stable 2.x release and the hand-written command map grows large.
