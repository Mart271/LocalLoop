# Test Fixtures

Inputs with known expected results.

## Present today

| Folder | Contents | Used by |
|---|---|---|
| [`schema/invalid/`](schema/invalid/) | Workflow definitions that the draft schema **must reject**: unknown fields, a `shell.exec` operation, an absolute path in a location, a decision with only one option | `scripts/validate_schemas.py` (runs in CI) |

| `generated/` (git-ignored) | Sets F1–F6 with a `truth.json` per set, produced by [`tools/fixtures/generate.py`](../../tools/fixtures/README.md) | Spikes now; adapter and end-to-end tests from M1.2 |
| [`manifest.json`](manifest.json) | Seed and SHA-256 of every generated file; `generate.py --check` proves reproducibility in CI | CI |

## Rules

- Synthetic data only (A-19). Names, companies, amounts, and addresses are invented.
- Every fixture states its purpose: a valid case, an edge case, a fault, or an attack.
- Keep binary fixtures small. Generate large sets with a script rather than committing them.
