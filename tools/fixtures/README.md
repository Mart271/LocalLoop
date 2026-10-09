# Synthetic fixture generator (LL-012)

Generates the fixture sets in [MVP_SCOPE §9](../../docs/development/MVP_SCOPE.md#9-reference-dataset-synthetic) from a seed. **Every name, address, and amount is invented** (A-19); no real company's documents or branding are used. Dev-only: nothing here ships in the product.

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r tools\fixtures\requirements.txt
.venv\Scripts\python tools\fixtures\generate.py            # -> tests\fixtures\generated (git-ignored)
.venv\Scripts\python tools\fixtures\generate.py --check    # byte-for-byte against tests\fixtures\manifest.json
```

| Set | Folder | Contents |
|---|---|---|
| F1 | `F1-consistent/` | 3 fictitious vendors × 20 text-layer PDF invoices; one layout per vendor, same labels as the [example workflow](../../examples/workflows/invoice-intake.exact-replay.workflow.json) |
| F2 | `F2-scanned/` | 15 F1 invoices rasterized at clean, medium, and poor quality (noise, skew, blur, JPEG); PNG, JPEG, TIFF, and image-only PDF |
| F3 | `F3-variable/` | 10 layout variants per vendor: label synonyms, values below labels, five date formats (for EV-02) |
| F4 | `F4-invalid/` | Wrong totals, missing fields, future dates, duplicate invoice numbers, byte-identical duplicate, unsupported files |
| F5 | `F5-adversarial/` | Prompt-injection text (visible, white, metadata, file name), path-traversal and reserved vendor names, formula payloads, encrypted, truncated, garbage, mislabelled, 120-page, and 12000×12000 px files |
| F6 | `F6-spreadsheets/` | Plain and richly formatted `Invoices.xlsx`, a macro-enabled `.xlsm` (placeholder part, no code), wrong-structure workbooks, CSV with and without BOM |

Each folder has a `truth.json` with the expected result for every file (the ground truth). The "locked spreadsheet" scenario of F6 is created by tests at run time by holding the file open, not by a file.

**Reproducibility:** reportlab runs in invariant mode, workbook zips get fixed timestamps, and noise comes from seeded random streams, one per set. Changing a pinned library version may change bytes: regenerate with `--update-manifest` and review the diff. Known limits: openpyxl cannot author pivot tables, external links, or real VBA, so those F6 cases are not covered yet.
