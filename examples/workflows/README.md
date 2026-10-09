# Example Workflows

These files are **example workflow definitions** in the draft 0.1 format ([schema](../../schemas/workflow/0.1/workflow.schema.json), [ADR-0005](../../docs/adr/0005-workflow-definition-format.md)). They show what LocalLoop stores after a workflow has been created, reviewed, and compiled.

> **Nothing can run them yet.** No LocalLoop runtime exists. CI checks that they validate against the schema and pass a few compiler-style consistency checks (`scripts/validate_schemas.py`); it does not execute them.

## Files

| File | Mode | Capability level | What it shows |
|---|---|---|---|
| [`invoice-intake.exact-replay.workflow.json`](invoice-intake.exact-replay.workflow.json) | Exact Replay | Basic Automation (no model) | The MVP scenario when every invoice shares one layout: list → read text → rule-based extraction → validate → review or log to spreadsheet → file by vendor and month → report |
| [`invoice-intake.adaptive.workflow.json`](invoice-intake.adaptive.workflow.json) | Adaptive Execution | Lightweight Local AI | The same scenario with mixed layouts: one bounded `control.decide` step lets the local model choose between **declared** extraction options; uncertain choices go to the user |

Both cover the MVP flow **Receive documents → Extract information → Validate data → Update a local spreadsheet → Organize files → Generate execution report** ([MVP_SCOPE.md](../../docs/development/MVP_SCOPE.md)).

## What to notice

- **Same steps, different mode.** The adaptive example differs from the Exact Replay example in a single step. The model chooses only *which declared option* applies; it cannot add operations, widen permissions, or change where files go (FR-047, FR-048).
- **Closed operation set.** Every `op` comes from the operation catalog ([component-design.md §2](../../docs/architecture/component-design.md#2-operation-catalog)). `permissions.operations` lists exactly the operations the steps use (FR-102).
- **Named locations, not paths.** Steps refer to locations such as `inbox` and `finance`. The user binds them to real folders when granting permissions, so definitions stay portable and contain no personal paths.
- **Verification is declared.** Steps carry postconditions and the workflow has `successConditions`; a run is only reported as completed when these are verified (FR-033, FR-087).
- **Mode recommendation is recorded.** `modeRecommendation` stores the six assessment factors and the plain-language explanation (FR-035, FR-036, FR-041).
- **Limitations are explicit.** `knownLimitations` states what the workflow does not handle (FR-014).

## Rejected definitions

`tests/fixtures/schema/invalid/` holds definitions the schema **must reject**, for example a `shell.exec` operation or an absolute path in a location. They are negative tests for the format ([fixtures README](../../tests/fixtures/README.md)).

## Adding an example

1. Use synthetic data only (A-19). No real names, invoices, or paths.
2. Use only operations in the catalog for the schema version you declare.
3. Run `python3 scripts/validate_schemas.py` and `python3 scripts/check_docs.py`.
