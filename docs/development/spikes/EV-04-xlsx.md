# EV-04 / LL-008: Windows XLSX fidelity and lock study

Date: 2026-10-10 (Asia/Manila). [Raw evidence](evidence/ev04-windows.json), [Rust probe](../../../spikes/xlsx/src/main.rs), [independent reader](../../../spikes/xlsx/compare.py).

Machine: MSI MS-7A70, Intel Core i5-7500, 16 GB RAM, Windows 10 Pro 19045, x64; Rust 1.99.0, Python 3.12.10, openpyxl 3.1.5. No AI model. Seed 20261009, synthetic F6; macOS deferred.

## Method and findings

Six cases: unchanged and edited round trips through umya-spreadsheet 3.1.0 (MIT), plus a narrowly targeted ZIP/XML edit, on plain and formatted workbooks. Outputs are new temporary files. An independent openpyxl re-read compares values/types, formulas, number formats, fonts/fills/borders/alignment, comments, column widths, freeze panes, table definitions, validation, conditional formatting, defined names, hidden sheets and chart count/type. Package parts are compared independently. The edit changes fixture H2 only.

- umya plain unchanged round trip: no checked semantic changes.
- umya plain edit: an unexpected H column-width change.
- umya formatted unchanged and edited round trips: the chart disappeared and the table XML changed. Some comment parts were renamed/reorganized; the re-read still preserved the checked cell comment. Removal of a package filename alone is not proof that its semantics were lost.
- Targeted ZIP/XML edits: only `xl/worksheets/sheet1.xml` changed; all other uncompressed parts remained byte-identical. Both intended cell edits re-read correctly; zero unexpected changes in the checked semantics and zero removed parts.
- The source files remained unchanged in all six cases.
- A Windows `CreateFileW` handle with sharing disabled blocked a write open; the file reopened after release. This is an exclusive-lock simulation, not an Excel-on-device test.

## Decision recommendation (A-05)

Do not use an unrestricted whole-workbook round trip to modify user files. Recommend ZIP + quick-xml for an explicitly supported simple XLSX subset, preserving untouched parts and verifying the changed cells with an independent reader. Reject unknown or advanced workbook structures **before** modifying anything. Offer a separate plain output file or CSV when the original is unsupported. [ADR-0007](../../adr/0007-xlsx-fidelity-policy.md).

This narrow one-cell spike is not a production upsert implementation. Macros, pivots, external links, charts/drawings, complex formatting, protection, signatures and unsupported relationships remain unsupported for in-place writes, even though a one-cell experiment preserved the formatted fixture. General row insertion, table/range expansion, Excel recalculation and visual rendering are not established.

The future adapter must enforce size/ZIP/XML quotas, authorized handles, exclusive locking, structure checks, backup, temporary file + atomic replacement, formula-neutralized text writes, independent re-read and mismatch classification (FR-063). Do not relax verification because a writer returned success.

## Reproduce

```powershell
.venv/Scripts/python.exe tools/fixtures/generate.py
cargo build --release --locked --manifest-path spikes/xlsx/Cargo.toml
.venv/Scripts/python.exe spikes/xlsx/compare.py --binary spikes/xlsx/target/release/spike-xlsx.exe --output docs/development/spikes/evidence/ev04-windows.json
```

Primary references: [umya-spreadsheet](https://github.com/MathNya/umya-spreadsheet), [quick-xml](https://github.com/tafia/quick-xml), [zip](https://github.com/zip-rs/zip2). Library support claims were tested against fixtures rather than assumed. FR-062 / TC-052 and the complete FR-063 / TC-053 safety suite remain M1.2 work.
