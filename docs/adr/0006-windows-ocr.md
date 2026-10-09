# ADR-0006: Tesseract as the initial Windows document OCR backend

| Field | Value |
|---|---|
| Status | Proposed |
| Date | 2026-10-10 |
| Deciders | Project owner, pending milestone review |
| Related requirements | FR-056, FR-059, D-04, EXC-04 |

## Context

[EV-06](../development/spikes/EV-06-ocr.md) compared Tesseract and ocrs on 60 synthetic F1/F2 pages on the measured Windows machine. Tesseract recovered more ground-truth field text overall and exposes word confidence and boxes. ocrs performed better on the poor scans; neither engine handles every poor scan reliably.

## Decision

Recommend Tesseract 5.5.0 with local English LSTM data in the separate document worker for the initial Windows implementation. No downloads, external input URLs or backend auto-installation at runtime. Hash-check bundled assets and retain word confidence/boxes; deterministic validation and review remain mandatory. OCR confidence is not a probability of correct extracted data.

## Consequences

- Native DLLs and language data require licence notices and offline packaging.
- The core still sends bounded bytes to the worker; parsing and OCR never move into the UI or core process.
- Poor scans may require user review; preprocessing can be evaluated later against held-out fixtures.
- macOS backend validation is deferred under [ADR-0010](0010-windows-first-validation.md).

## Alternatives considered

| Option | Evidence / reason |
|---|---|
| ocrs 0.13.1 | Easier Rust integration and better poor-scan recovery, but lower aggregate recovery in this fixture run; upstream CLI auto-downloads, so it cannot ship unchanged |
| PaddleOCR or OS-native OCR | Not measured in this spike; no performance claim |

## Validation

Implement and test TC-046 in M1.2 with worker quotas, explicit local assets, confidence routing and network-denied execution. Revisit after poor-scan or language requirements expand. The current study measures normalized text presence, not end-to-end extraction accuracy.
