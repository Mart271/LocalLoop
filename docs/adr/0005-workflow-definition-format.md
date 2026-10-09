# ADR-0005: JSON workflow definition with JSON Schema and symbolic locations

| Field | Value |
|---|---|
| Status | Proposed |
| Date | 2026-10-09 |
| Deciders | Project owner (pending review) |
| Related requirements | FR-002, FR-003, FR-007, FR-008, FR-102, FR-103, NFR-029, D-06 |

## Context

Workflows must use "a portable, documented format where feasible, allowing inspection and backup without relying on the product's cloud infrastructure" (P§4.8). They are shared between machines, where folder paths differ, and they are an input from untrusted sources when imported.

## Decision

1. The canonical workflow format is **JSON** validated by a published **JSON Schema** (draft 2020-12), versioned by `schemaVersion`. Draft 0.1 lives at [`schemas/workflow/0.1/workflow.schema.json`](../../schemas/workflow/0.1/workflow.schema.json).
2. Workflows declare **symbolic locations** (for example `inbox`, `processed`) with required access. Real folders are bound on each machine at grant time and are never stored in the portable file.
3. The schema is strict (`additionalProperties: false`) so unknown fields are rejected, not ignored.
4. Version history, grants, and run records are stored in the database, not in the file.
5. Content hashes for versions are computed over a canonical JSON serialization (sorted keys, no insignificant whitespace).

## Consequences

- Positive: portable and inspectable; schema validation catches malformed or malicious imports early; symbolic locations make sharing safe and require a fresh grant on every machine.
- Negative: JSON is less pleasant to hand-edit than YAML; strict schemas require migrations for every change (NFR-029).
- Follow-up: publish the operation catalog alongside the schema; write migration rules when 0.2 is introduced; consider YAML as an authoring format later (D-06), always compiled to canonical JSON.

## Alternatives considered

| Option | Why not chosen |
|---|---|
| YAML as canonical format | Ambiguities (implicit typing) and more complex parsers for untrusted input |
| Database-only storage | Not portable; conflicts with P§4.8 |
| Absolute paths in the file | Not portable; importing a file would silently target the original author's paths |

## Validation

CI validates every example workflow against the schema (see `scripts/validate_schemas.py`). Import tests cover invalid files, unsupported versions, and unknown fields (EXC-27).
