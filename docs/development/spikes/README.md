# M1.0 spike reports

Windows is the current milestone gate ([ADR-0010](../../adr/0010-windows-first-validation.md)). These reports contain synthetic development evidence; no spike is linked into the product workspace. All dates are 2026-10-10 in Asia/Manila; raw timestamps are UTC.

| Item | Report | Reproducible harness |
|---|---|---|
| EV-06 / LL-007 OCR | [OCR comparison](EV-06-ocr.md) | [compare.py](../../../spikes/ocr/compare.py) |
| EV-04 / LL-008 XLSX | [Fidelity and locks](EV-04-xlsx.md) | [Rust probe](../../../spikes/xlsx/src/main.rs), [independent observer](../../../spikes/xlsx/compare.py) |
| D-07 / LL-010 encryption | [Encryption at rest](D-07-encryption.md) | [Rust probe](../../../spikes/encryption/src/main.rs) |
| LL-011 child lifecycle | [Containment and checksums](LL-011-child-processes.md) | [lifecycle tests](../../../spikes/child-process/tests/lifecycle.rs) |
| LL-013 baseline | [Windows shell baseline](LL-013-windows-baseline.md) | [measurement](../../../spikes/baseline/measure.ps1), [real WebView smoke](../../../spikes/baseline/smoke.mjs) |

EV-01 / LL-006 is deferred to M1.5; EV-09 / LL-009 is deferred to Phase 2. macOS, 8 GB reference-machine acceptance, full document-worker/sidecar installer packaging and end-to-end workflow benchmarks remain pending.
