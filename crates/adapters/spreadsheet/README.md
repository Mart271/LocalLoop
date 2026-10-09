# `adapters/spreadsheet`

> **Skeleton only (LL-001):** the crate builds but has no public API yet. Design: [component-design.md §3.8](../../../docs/architecture/component-design.md#38-adapters). Milestone M1.2, backlog LL-036 and LL-037.

**Layer 5 adapter (MVP).** Updates local spreadsheets as files, not by driving a spreadsheet application (FR-077).

## Responsibilities

- `sheet.upsert_rows` for XLSX (without macros) and CSV, matching rows by the declared key columns so re-runs do not duplicate data (FR-062, FR-067).
- Write safety (FR-063):
  - detect a file that is open or locked in another application and stop with a clear message;
  - check that the expected sheet and columns exist before writing;
  - back up the file, write to a temporary file, then atomically replace the original;
  - re-read the result to verify it;
  - write values that start with `=`, `+`, `-`, `@`, tab, or carriage return as text, so a document cannot inject a formula.
- Undo by restoring the backup, but only if the file still has the hash LocalLoop wrote; otherwise report a conflict rather than overwrite someone else's changes.
- Implements `StateObserver` for `sheet.row_present` and `sheet.row_count_delta` (FR-085).

## Known limits (A-05)

Workbooks with macros, pivot tables, or external links may not survive a library round trip. Spike EV-04 measures fidelity. Until then, such workbooks are rejected or written through a separate output sheet or file.
