# `storage`

> **Skeleton only (LL-001):** the crate builds but has no public API yet. Design: [component-design.md §3.7](../../docs/architecture/component-design.md#37-storage--persistence-journal-audit-chain-evidence-backup) and [§9](../../docs/architecture/component-design.md#9-storage-design).

**Layer 7: Local Storage.** Everything LocalLoop keeps stays on the device, in a location the user can see.

## Responsibilities

- SQLite database (WAL mode), migrations with a backup taken first, and repositories for workflows, versions, grants, runs, steps, approvals, and models.
- Append-only journal used for crash recovery (NFR-004).
- Tamper-evident audit hash chain with a verification command (FR-094). It is tamper-*evident*, not tamper-proof: a user with full control of the machine can rewrite local files, but the change will be detected.
- Evidence store for snapshots and reports, with encryption at rest for sensitive data (NFR-017; approach decided in D-07).
- Backup and restore of the library, offline (FR-119).
- Retention and purge of evidence and recordings (FR-120, NFR-023).

## Must not

- Hold credentials. Secrets live in the OS credential store and are referenced by name only (FR-075, NFR-016).

## First backlog items

LL-010 (encryption spike), LL-024 (database and migrations), LL-025 (journal), LL-026 (audit chain), LL-027 (encryption at rest), LL-034 (provenance and evidence).
