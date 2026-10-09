# EV-06 / LL-007: Windows OCR comparison

Date: 2026-10-10 (Asia/Manila). [Raw evidence](evidence/ev06-windows.json), [harness](../../../spikes/ocr/compare.py).

Measured machine: MSI MS-7A70, Intel Core i5-7500, 16 GB RAM, Windows 10 Pro build 19045, x64. Rust 1.99.0, Python 3.12.10; reportlab 5.0.1, PDFium through pypdfium2 5.14.0, Pillow 12.3.0. No LLM or quantization. This is not the ASUS laptop or an 8 GB reference machine. macOS is deferred.

## Method

Seed 20261009; 15 F1 invoices (five per vendor), rasterized at 200 DPI, and all 45 F2 variants. Both engines receive the same prepared PNG for each page. Each engine uses a fresh process per page, four CPU threads, no deskew or denoise, a 120-second timeout, and pre-downloaded local models. Runs occurred alongside development builds; timings are exploratory, not isolated performance claims.

Score: presence of the seven ground-truth field strings, ignoring case, whitespace and punctuation. This is **text recovery**, not field attribution, semantic extraction accuracy, or calibrated confidence. Amounts can occur elsewhere on a page. Sample sizes and per-field failures are retained in the evidence; no held-out user documents were used.

## Results

| Group (15 pages each) | Tesseract field text / 105 | All seven fields / 15 | ocrs field text / 105 | All seven fields / 15 |
|---|---|---|---|---|
| F1 rasterized | 105 | 15 | 96 | 10 |
| F2 clean | 105 | 15 | 94 | 9 |
| F2 medium | 103 | 13 | 103 | 13 |
| F2 poor | 97 | 7 | 100 | 10 |

No subprocess failed. Tesseract medians ranged from 1.46 to 1.85 seconds/page; ocrs from 3.05 to 3.82 seconds/page on this run. Overall text checks: Tesseract 410/420; ocrs 393/420. Neither engine reliably recovers every field on poor scans.

## Recommendation (D-04)

Use Tesseract 5.5.0 with English LSTM data as the initial Windows worker backend, with per-word confidence and bounding boxes retained for provenance. Apply deterministic validation and route uncertain scans to review. Do not equate an OCR confidence score with correctness. See [ADR-0006](../../adr/0006-windows-ocr.md).

- [Tesseract](https://github.com/tesseract-ocr/tesseract): Apache-2.0; installed Windows build 5.5.0.20241111, Leptonica 1.85.0. [Windows build source](https://github.com/UB-Mannheim/tesseract/wiki). The worker must call its library on supplied image bytes or invoke a separately restricted local backend; it must never fetch remote inputs.
- [ocrs](https://github.com/robertknight/ocrs): Apache-2.0 / MIT, Rust CLI 0.13.1 with RTen 0.26.0; currently Latin-alphabet recognition. Its upstream CLI can download models, so it is **development-only**. A product integration would use the library with explicit local model paths and verified hashes, never the auto-downloading CLI.
- [Measured payload sizes](evidence/ocr-payload-sizes.json): installed Tesseract tree 90,200,529 bytes (includes extra tools/languages), executable 86,152 bytes, English data 4,113,088 bytes. ocrs executable 8,584,192 bytes plus detection 2,499,479 and recognition 9,713,177 bytes. These are uncompressed installed sizes, not installer-size promises. Asset SHA-256 hashes are recorded in the evidence.

## Reproduce

```powershell
cargo install ocrs-cli --version 0.13.1 --locked --root .localloop-dev/ocr
# Download the detection and recognition models from the upstream project at development time.
# Place them in .localloop-dev/ocr; compare their hashes with the evidence.
.venv/Scripts/python.exe tools/fixtures/generate.py
.venv/Scripts/python.exe spikes/ocr/compare.py --ocrs .localloop-dev/ocr/bin/ocrs.exe --models .localloop-dev/ocr --output docs/development/spikes/evidence/ev06-windows.json
```

FR-056 / TC-046 product integration, no-network acceptance, confidence routing, worker quotas and Windows installer packaging remain M1.2/M1.6 work. This spike does not implement those features.
