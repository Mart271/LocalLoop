# `adapters/documents`

> **Planned — no code yet.** Design: [component-design.md §3.8–3.9](../../../docs/architecture/component-design.md#39-document-worker-binary-in-cratesadaptersdocuments) and the [worker protocol](../../../docs/architecture/component-design.md#101-core--document-worker). Milestone M1.2, backlog LL-030 to LL-032.

**Layer 5 adapter (MVP)** plus the **document worker**, a separate process that parses untrusted files.

## Why a separate process

PDFs and images come from outside and are parsed by complex libraries. Parsing them in a child process means a crash or hang cannot take down the app, and the core can kill and restart the worker (EXC-23). The adapter reads the file bytes itself, inside policy, and sends the bytes to the worker. The worker has no reason to open files or network connections. OS-level sandboxing of the worker is a Phase 4 hardening item (AR-05).

## Responsibilities

- `docs.read_text`: use the PDF text layer when present and run OCR only on pages that have no text layer (FR-055, FR-056).
- Return words with positions and a confidence value, so extracted fields can point back to where they came from (FR-059).
- Render pages for the annotation UI (FR-021).
- Enforce limits on size, page count, and time, and return typed errors (`encrypted_document`, `unsupported_format`, `limit_exceeded`, `ocr_unavailable`).

## Open decision

The OCR engine (Tesseract, ocrs, PaddleOCR via ONNX, or the OS's own OCR) is chosen from spike EV-06 (decision D-04).
