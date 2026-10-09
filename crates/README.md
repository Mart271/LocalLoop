# Rust Crates

> **Skeleton only.** The Cargo workspace (root `Cargo.toml`) and an empty crate per folder were created in LL-001 (milestone M1.0). Browser and desktop adapters remain README-only until Phase 2 and Phase 3.

| Crate | Layer | Responsibility |
|---|---|---|
| [`workflow-engine`](workflow-engine/README.md) | 4 | Domain model and ports, compiler, planner, conditions and templates, mode recommender. No I/O |
| [`policy-engine`](policy-engine/README.md) | 4 | Permission manifest, grants, path canonicalization, taint rules, approvals. Sole issuer of `AuthorizedOperation` |
| [`execution-engine`](execution-engine/README.md) | 5 | Run orchestration, journal, pause and stop, approvals, decision points, budgets |
| [`verification-engine`](verification-engine/README.md) | 6 | Postconditions, outcome classification, recovery and rollback planning |
| [`local-ai`](local-ai/README.md) | 3 | Model registry, inference sidecar supervision, prompt templates, structured output validation |
| [`observation`](observation/README.md) | 2 | Recording sessions: consent, scope, redaction, file-event capture |
| [`storage`](storage/README.md) | 7 | SQLite, journal, audit hash chain, evidence store, backup and retention |
| [`adapters/*`](adapters/files/README.md) | 5 | Files, documents, spreadsheet (MVP); browser (Phase 2); desktop (Phase 3) |

The desktop app in [`apps/desktop`](../apps/desktop/README.md) is the only place that wires all crates together.

## Dependency rules (NFR-030)

Allowed dependencies point toward `workflow-engine`, which defines the domain types and ports and depends on no internal crate ([SYSTEM_ARCHITECTURE §6.1](../docs/architecture/SYSTEM_ARCHITECTURE.md#61-module-dependency-rules-nfr-030)).

**Forbidden**, to be enforced by a CI check (LL-004):

- `local-ai` → `policy-engine`, `execution-engine`, `adapters/*`, `storage`
- `adapters/*` → `local-ai`
- `observation` → `execution-engine`, `adapters/*`
- `workflow-engine` → any internal crate

Because `local-ai` cannot name adapter or policy types, model output cannot reach an adapter except through the compiler and the policy engine.

## Conventions (planned)

- Shared lints at the workspace root; `#![forbid(unsafe_code)]` unless an ADR justifies an exception (platform bindings in `adapters/desktop` are the expected exception).
- Typed errors per crate; no panics on untrusted input.
- Untrusted values travel as `Tainted<T>` until an explicit sanitizer accepts them (FR-106).
