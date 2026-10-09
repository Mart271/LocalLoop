# Integration Tests

Cross-crate tests that exercise real adapters and child processes against fixtures. Planned groups:

| Group | Exercises | Requirements |
|---|---|---|
| Document pipeline | Document worker (text layer, OCR), rule extraction, validation | FR-054 to FR-061 |
| Spreadsheet safety | Backup, atomic replace, lock detection, formula neutralization, re-read verification | FR-062, FR-063 |
| File organization | Moves and renames, collision policy, sanitized names, undo journal | FR-064, FR-065, FR-090 |
| Policy at dispatch | Every adapter call carries an `AuthorizedOperation`; scope escapes are denied | FR-102 to FR-106 |
| Verification | Postconditions re-observe state instead of trusting adapter results | FR-085, FR-087 |
| Fault injection | Process kill, disk full, worker crash at each state-changing step | NFR-002, NFR-004 |
| Local inference | Sidecar lifecycle, structured output validation, behaviour without a model | FR-110 to FR-113 |

Tests run against copies of fixtures in a temporary folder and never touch the developer's real files.

Nothing is here yet. The first integration tests arrive with milestone M1.2 ([Roadmap](../../docs/development/ROADMAP.md)).
