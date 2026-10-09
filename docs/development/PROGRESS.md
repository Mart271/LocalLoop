# LocalLoop — Progress Log

| Field | Value |
|---|---|
| Current milestone | M1.0 Foundation and spikes (branch `feat/m1.0-foundation`) |
| Last updated | 2026-10-09 |
| Related | [Roadmap](ROADMAP.md) · [Backlog](BACKLOG.md) |

This file lets a new session resume work. It records what is done, how it was verified, decisions awaiting the owner's confirmation, deviations from the docs, and risks.

## Environment

| Item | Value |
|---|---|
| Development machine | ASUS TUF Gaming F15 (FX507ZC4), Intel Core i5-12500H, 16 GB RAM, NVIDIA RTX 3050 Laptop + Intel Iris Xe, NVMe SSD, Windows 11 Home build 26300 |
| Reference machines (A-14) | **Not available.** The development machine is 16 GB, not an 8 GB reference machine. Reference-machine measurements are *pending*. |
| macOS | No Mac available; macOS builds and tests run on GitHub Actions `macos-latest` only. On-device macOS checks are *pending*. |
| Toolchain | Rust 1.99.0 (stable-x86_64-pc-windows-msvc), Node 24.20.0 LTS, pnpm 12.10.1 (corepack), Python 3.14.3, Git 2.51.2, Visual Studio Community 2026 C++ workload with Windows SDK 10.0.26100.0, WebView2 154.0.4258.62 |

## Owner decisions (2026-10-09)

- M1.0 plan approved, including dev-time downloads (crates, npm packages, prebuilt PDFium, OCR models, ONNX Runtime). Product code still makes no network calls.
- **D-02:** browser automation deferred to Phase 2 (EV-09 / LL-009 skipped).
- Pushing `feat/m1.0-foundation` to `origin` for CI is allowed; no pull requests.
- cargo-deny licence allowlist: permissive licences plus MPL-2.0; GPL, LGPL, AGPL denied.
- LL-006 (EV-01) moves to M1.5; LL-009 (EV-09) deferred.

## M1.0 status

| Item | Status | Notes |
|---|---|---|
| CLAUDE.md | Done | |
| LL-001 | Not started | |
| LL-004 | Not started | |
| LL-012 | Not started | |
| LL-002 | Not started | |
| LL-005 | Not started | |
| LL-003 | Not started | |
| LL-011 | Not started | |
| LL-010 | Not started | |
| LL-007 | Not started | |
| LL-008 | Not started | |
| LL-013 | Not started | |
