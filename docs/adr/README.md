# Architecture Decision Records

Architecture decisions are recorded as short documents using the format in [`template.md`](template.md) (context → decision → consequences → alternatives).

## Status values

| Status | Meaning |
|---|---|
| **Proposed** | Written and open for review; not yet binding |
| **Accepted** | Agreed; implementation must follow it |
| **Superseded** | Replaced by a later ADR (linked) |
| **Rejected** | Considered and declined; kept for the record |

All current ADRs are **Proposed**. They become *Accepted* after review by the project owner, and, where listed, after the named spike or evaluation (`EV-nn`, see [SRS §18.5](../requirements/SRS.md#185-planned-evaluations-and-spikes)).

## Index

| ADR | Title | Status | Depends on |
|---|---|---|---|
| [0001](0001-initial-architecture.md) | Initial architecture: layered core with AI outside the trusted execution path | Proposed | — |
| [0002](0002-closed-operation-catalog.md) | Closed operation catalog; no arbitrary command execution | Proposed | — |
| [0003](0003-local-inference-sidecar.md) | Local inference through an on-demand llama.cpp sidecar | Proposed | EV-01 |
| [0004](0004-browser-automation-bridge.md) | Browser automation through a Playwright bridge process | Proposed | EV-09 |
| [0005](0005-workflow-definition-format.md) | JSON workflow definition with JSON Schema and symbolic locations | Proposed | — |
| [0009](0009-ipc-type-generation.md) | Generate IPC TypeScript types from Rust with ts-rs | Proposed | — |

## Decisions still to record

| Topic | Decision ID | Expected |
|---|---|---|
| OCR engine | D-04 | After EV-06 (Phase 1) |
| Encryption at rest (SQLCipher vs. application-level) | D-07 | Phase 1 |
| XLSX library and unsupported-workbook policy | A-05 | After EV-04 (Phase 1) |
| Software licence | D-03 | Before first public release |

## Writing a new ADR

1. Copy `template.md` to `NNNN-short-title.md` using the next number.
2. Fill in every section; link the requirements it serves.
3. Open a pull request; set status to *Accepted* only after review.
