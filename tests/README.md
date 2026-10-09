# Tests

> **Status:** no application code exists, so no application tests exist yet. What runs today is the documentation and schema checks in `scripts/`, plus the negative schema fixtures in [`fixtures/schema/invalid/`](fixtures/schema/invalid/). Test cases are **planned** and catalogued in the [traceability document §5](../docs/requirements/requirements-traceability.md#5-test-case-catalogue).

## Test strategy

LocalLoop's main promise is that it never claims success it cannot verify, and that AI output never becomes permission. The test strategy is built around those two promises.

| Level | Code | Purpose | Where it lives |
|---|---|---|---|
| Unit | U | Pure logic: compiler, planner, mode recommender, policy decisions, postcondition evaluation, outcome classification | Next to the code (`#[cfg(test)]` in each crate; `*.test.ts` in the UI). [`unit/`](unit/README.md) holds shared, table-driven cases |
| Integration | I | One crate plus real adapters against fixture folders and spreadsheets; worker and sidecar protocols | [`integration/`](integration/README.md) and each crate's `tests/` folder |
| End-to-end | E2E | Full workflows through the desktop UI | [`e2e/`](e2e/README.md) |
| System | S | Reference machines or clean VMs: offline suite, 8 GB runs, installers, platform matrix | Run from `e2e/` harnesses on the target machines |
| Evaluation | EV | Model quality and calibration studies (`EV-01` … `EV-09`) | Protocols in [SRS §18.5](../docs/requirements/SRS.md#185-planned-evaluations-and-spikes) |
| Usability | UX | Comprehension of recommendations, permissions, approvals | Study protocols (EV-07, EV-08) |
| Review | R | Inspection of configuration, dependencies, catalog | Pull request review and CI checks |

## Suites that must exist before the MVP release

These suites back the MVP acceptance criteria ([SRS §19.2](../docs/requirements/SRS.md#192-mvp-release-acceptance-criteria)):

| Suite | Backs | Notes |
|---|---|---|
| Deterministic replay suite | NFR-001 | Repeated runs of validated Exact Replay workflows; target ≥ 99% success |
| Fault-injection suite | NFR-002, NFR-004 | Kill the process, fill the disk, lock files, crash the worker at every state-changing step; source files must never be silently damaged |
| Mismatch-injection suite | NFR-003 | Wrong totals, missing rows, wrong destinations; none may be reported as completed |
| Offline suite | NFR-006, NFR-007 | All core features with every network interface disabled; traffic capture shows no unexpected connections |
| Prompt-injection corpus | NFR-020, FR-106 | Documents and pages with embedded instructions; zero policy bypasses |
| Low-resource runs | NFR-008 | MVP scenario on both 8 GB reference machines |

## Rules for test data

- **Synthetic documents only** (A-19). Never commit real invoices, customer data, credentials, screenshots of real accounts, or model files.
- Fixtures carry their expected results (ground truth) next to them, so tests compare against known answers rather than against previous output.
- Fault and injection fixtures are labelled with what they are meant to break.

See [`fixtures/`](fixtures/README.md).

## Adding a test

1. Find the requirement's test case ID in the [traceability matrix](../docs/requirements/requirements-traceability.md).
2. Implement the test at the level the catalogue gives.
3. Add the test's path next to its test case ID in the catalogue (maintenance rule 3 of the traceability document).
