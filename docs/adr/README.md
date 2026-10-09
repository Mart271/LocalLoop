# Architecture Decision Records

Architecture decisions are recorded as short documents using the format in [`template.md`](template.md) (context → decision → consequences → alternatives).

## Status values

| Status | Meaning |
|---|---|
| **Proposed** | Written and open for review; not yet binding |
| **Accepted** | Agreed; implementation must follow it |
| **Superseded** | Replaced by a later ADR (linked) |
| **Rejected** | Considered and declined; kept for the record |

Technical choices remain **Proposed** until the project owner reviews them and the named spike or evaluation is complete (`EV-nn`, see [SRS §18.5](../requirements/SRS.md#185-planned-evaluations-and-spikes)). ADR-0010 records the owner's explicit Windows-first instruction and is **Accepted**.

## Index

| ADR | Title | Status | Depends on |
|---|---|---|---|
| [0001](0001-initial-architecture.md) | Initial architecture: layered core with AI outside the trusted execution path | Proposed | — |
| [0002](0002-closed-operation-catalog.md) | Closed operation catalog; no arbitrary command execution | Proposed | — |
| [0003](0003-local-inference-sidecar.md) | Local inference through an on-demand llama.cpp sidecar | Proposed | EV-01 |
| [0004](0004-browser-automation-bridge.md) | Browser automation through a Playwright bridge process | Proposed | EV-09 |
| [0005](0005-workflow-definition-format.md) | JSON workflow definition with JSON Schema and symbolic locations | Proposed | — |
| [0006](0006-windows-ocr.md) | Initial Windows OCR engine: Tesseract | Proposed | EV-06 report |
| [0007](0007-xlsx-fidelity-policy.md) | Constrained XLSX edits and unsupported-workbook policy | Proposed | EV-04 report |
| [0008](0008-encryption-at-rest.md) | Encryption at rest | Proposed | D-07 report |
| [0009](0009-ipc-type-generation.md) | Generate IPC TypeScript types from Rust with ts-rs | Proposed | — |
| [0010](0010-windows-first-validation.md) | Prioritize Windows and defer macOS validation | Accepted | Owner instruction, 2026-10-10 |

## Decisions still to record

| Topic | Decision ID | Expected |
|---|---|---|
| Software licence | D-03 | Before first public release |

## Writing a new ADR

1. Copy `template.md` to `NNNN-short-title.md` using the next number.
2. Fill in every section; link the requirements it serves.
3. Request owner review at the milestone boundary; set status to *Accepted* only after review. Pushes and pull requests require the owner's explicit authorization under AGENTS.md.
