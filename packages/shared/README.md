# `packages/shared`

**Generated TypeScript types** for the data that crosses the IPC boundary between the React UI and the Rust core: command names, inputs, outputs, and errors (LL-005).

## Rules

- Files in `src/generated/` are **generated from the Rust definitions** in `apps/desktop/src-tauri/src/ipc/dto.rs` by ts-rs ([ADR-0009](../../docs/adr/0009-ipc-type-generation.md)). Never edit them by hand.
- Regenerate with `pnpm gen:types` from the repository root. CI regenerates them and fails if the result differs from what is committed.
- The command-name union `IpcCommand` is generated from a Rust enum, so the UI cannot name a command the core does not define.
- `src/index.ts` re-exports every generated file; a Rust test fails if one is missing.
- Workflow definition types must agree with the [workflow JSON Schema](../../schemas/workflow/0.1/workflow.schema.json) (added in M1.1).
- No runtime logic lives here; only types.
