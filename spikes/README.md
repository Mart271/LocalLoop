# Development-only spikes

These programs are standalone Cargo workspaces or Python/PowerShell/Node harnesses. They are never shipped, imported by product code or linked into the main workspace. They may parse synthetic fixtures and download development dependencies; product parsing remains isolated in the document worker and product code stays offline.

Install Python dependencies in `.venv` using [SETUP.md](../docs/development/SETUP.md). Store downloaded models, browsers and tools under ignored `.localloop-dev/`; do not commit them. Benchmark reports and non-sensitive JSON evidence live in [docs/development/spikes](../docs/development/spikes/README.md).

- `child-process`: bounded framing, Windows job objects, watchdog, checksum refusal and failure controls.
- `encryption`: SQLCipher versus column AEAD with a unique temporary database and credential per run; errors fail the command.
- `ocr`: offline comparison using explicit local Tesseract/ocrs assets; the upstream auto-downloading CLI is development-only.
- `xlsx`: generic Rust round-trip probe and narrow package-preserving cell edit, independently checked with openpyxl; no general upsert claim.
- `baseline`: actual Windows shell smoke test and process-memory samples. Build with Tauri's embedded-assets command first. Each run uses a separate WebView profile; close runs before rebuilding.

`capture.py` records the command, exit code, duration and machine/fixture metadata. Its output is evidence, not a substitute for reviewing whether a measurement demonstrates the claimed requirement.
