# `adapters/files`

> **Skeleton only (LL-001):** the crate builds but has no public API yet. Design: [component-design.md §3.8](../../../docs/architecture/component-design.md#38-adapters). Milestone M1.2, backlog LL-029.

**Layer 5 adapter (MVP).** Performs file operations inside granted locations and observes file state for verification.

| Operation | Effect class | Undo |
|---|---|---|
| `files.list` | read | — |
| `files.copy` | write_reversible | Remove the copy only if its hash still matches what LocalLoop wrote |
| `files.move` | write_reversible | Move back |
| `files.rename` | write_reversible | Rename back |
| `report.write` | write_reversible | Remove the written report files |

## Rules

- Accepts only `AuthorizedOperation` and re-checks every opened handle against the granted location (FR-105).
- Never overwrites. Name collisions follow the workflow's collision policy (FR-064).
- File names built from document values arrive already sanitized; the adapter still rejects any path that leaves the location (FR-065).
- Uses an atomic rename on the same volume; across volumes it copies, verifies the hash, then removes the source.
- Skips files that are still being written (size or modification time changing) and reports them as not ready (FR-054, EXC-30).
- There is no permanent delete operation (A-18).
- Implements `StateObserver` for `file.exists`, `file.absent`, and `file.hash_equals` postconditions (FR-085).
