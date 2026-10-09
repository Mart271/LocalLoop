# `packages/shared`

> **Planned — no code yet.** Created in backlog item LL-005 (milestone M1.0).

**Generated TypeScript types** for the data that crosses the IPC boundary between the React UI and the Rust core: command inputs and outputs, events, and the workflow definition format.

## Rules

- Types are **generated from the Rust definitions**, never written by hand, so the UI and the core cannot drift apart. CI regenerates them and fails if the result differs from what is committed.
- The workflow definition types must agree with the [workflow JSON Schema](../../schemas/workflow/0.1/workflow.schema.json).
- No runtime logic lives here; only types and constants.

The generator tool is chosen in LL-005.
