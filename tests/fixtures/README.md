# Test Fixtures

Inputs with known expected results.

## Present today

| Folder | Contents | Used by |
|---|---|---|
| [`schema/invalid/`](schema/invalid/) | Workflow definitions that the draft schema **must reject**: unknown fields, a `shell.exec` operation, an absolute path in a location, a decision with only one option | `scripts/validate_schemas.py` (runs in CI) |

## Planned

| Folder | Contents |
|---|---|
| `documents/` | Synthetic invoices: text-layer PDFs, scanned PDFs at several qualities, PNG/JPEG/TIFF, two or more layout families, plus documents with embedded prompt-injection text |
| `spreadsheets/` | XLSX and CSV ledgers, including ones with formulas, several sheets, and formatting to check round-trip fidelity (EV-04) |
| `expected/` | Ground-truth extracted records and expected spreadsheet and folder states for each document set |

## Rules

- Synthetic data only (A-19). Names, companies, amounts, and addresses are invented.
- Every fixture states its purpose: a valid case, an edge case, a fault, or an attack.
- Keep binary fixtures small. Generate large sets with a script rather than committing them.
