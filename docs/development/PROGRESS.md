# LocalLoop — Progress Log

| Field | Value |
|---|---|
| Current milestone | M1.0 Foundation and spikes — Windows completion review |
| Branch | `feat/m1.0-foundation` |
| Last updated | 2026-10-10 (Asia/Manila) |
| Related | [Roadmap](ROADMAP.md) · [Backlog](BACKLOG.md) · [Spike reports](spikes/README.md) |

Resume here. The foundation was merged into `main` in PR #4 at `9a345a9`; the old log incorrectly marked that work as unstarted. This session verifies the Windows foundation, records the missing spike reports, and corrects the documentation. M1.1 has not started. Stop at this milestone boundary for owner review.

## Observed environment

| Item | Value |
|---|---|
| Measured machine | MSI MS-7A70, Intel Core i5-7500 at 3.40 GHz, 17,104,429,056 physical RAM bytes (approximately 16 GB), Windows 10 Pro build 19045, x64 |
| Toolchain | Rust 1.99.0; Node 24.11.1 (CI pins 24.20.0); pnpm 12.10.1; Python 3.12.10 in `.venv`; Git 2.52.0.windows.1; Visual Studio 2022 MSVC 14.44.35207; WebView2 154.0.4258.62 |
| Reference machines (A-14) | Not available. **No 8 GB acceptance claim.** NFR-008 remains In Progress; full workflow and release measurements are pending. |
| macOS | Deferred by the owner on 2026-10-10. Removed from active CI matrices; no new macOS build, packaging, performance or on-device evidence. |

The earlier log described an ASUS i5-12500H / Windows 11 development laptop and different tool versions. Those are historical notes, not the hardware observed for these measurements. See [LL-013](spikes/LL-013-windows-baseline.md) and the raw report metadata. No LLM was installed or benchmarked.

## Owner decisions and authorization

- 2026-10-09: dev-time dependency/model downloads allowed; product runtime remains offline.
- D-02: browser automation / EV-09 / LL-009 deferred to Phase 2; inference EV-01 / LL-006 moves to M1.5.
- Pushing only `feat/m1.0-foundation` to `origin` for CI is authorized. No pull requests or issues are authorized.
- Licence allowlist: permissive licences plus MPL-2.0; GPL, LGPL and AGPL denied.
- 2026-10-10: prioritize Windows and set macOS aside ([accepted ADR-0010](../adr/0010-windows-first-validation.md)). Original cross-platform and reference-machine release requirements remain pending.

## M1.0 work items

| Item | Windows status | Evidence and remaining scope |
|---|---|---|
| AGENTS.md | Present, owner edit | Existing local replacement for CLAUDE.md; preserve the owner's change. |
| LL-001 | Done | Ten library crates plus the desktop composition root (eleven workspace members); workspace compilation, formatting and Clippy passed. |
| LL-002 | Done for Windows | Real embedded-assets Tauri/WebView2 shell connects and rechecks ping; strict CSP, isolation and ping-only capability. Full command surface is LL-052; macOS deferred. |
| LL-003 | Local checks passed; CI configuration updated | Windows Rust/TS/audit gates and Ubuntu doc/schema/diagram gates. Previous merged-main CI was green. New branch CI status must be checked separately; local results are not a remote pass. |
| LL-004 | Done | Forbidden-edge script and negative direct/transitive dependency tests passed; CI blocks violations. No test PR was opened. |
| LL-005 | Done | Rust ts-rs exports regenerated and formatted; generated-file drift check passed. |
| LL-006 | Deferred | EV-01 belongs to M1.5. |
| LL-007 | Done; ADR review pending | [EV-06](spikes/EV-06-ocr.md): 60 pages per engine; Tesseract 410/420 text checks, ocrs 393/420. Proposed ADR-0006; product OCR pending. |
| LL-008 | Done; ADR review pending | [EV-04](spikes/EV-04-xlsx.md): generic writer loses chart/changes width; constrained edit preserves observed semantics and untouched ZIP parts. Proposed ADR-0007; adapter and atomic-write tests pending. |
| LL-009 | Deferred | EV-09 belongs to Phase 2. |
| LL-010 | Done for Windows; ADR review pending | [D-07](spikes/D-07-encryption.md): both options passed; SQLCipher protected tested metadata as well as sensitive values. Proposed ADR-0008; product encryption is LL-027; macOS deferred. |
| LL-011 | Done for Windows | [Lifecycle report](spikes/LL-011-child-processes.md): one framing and nine lifecycle tests passed, including checksum refusal, crash/hang and descendant cleanup. Production worker/sidecar installer integration pending. |
| LL-012 | Done | Seeded synthetic F1–F6: 186 files, 45 rasterized variants; reproducibility check passed. No real documents. |
| LL-013 | Development baseline done | [Five shell process samples and real WebView smoke](spikes/LL-013-windows-baseline.md), with observed hardware and versions. Debug shell only; 8 GB, release/full workflow and macOS acceptance deferred. |

## Verification performed on Windows

- Rust: workspace fmt, Clippy with warnings denied, and tests passed, including the embedded `tauri/custom-protocol` configuration (14 desktop tests). The actual Tauri debug build with embedded assets passed and was launched in WebView2.
- UI: frozen-lockfile install, build, lint, strict typecheck, five unit tests, Prettier, generated DTO drift, and `pnpm audit --audit-level low` passed.
- Security/dependencies: forbidden crate-edge check, `cargo deny --locked check`, and `cargo audit --deny warnings` passed. Existing audit exceptions concern Linux-only dependencies outside the supported product build; no new exceptions were added.
- Repository: 20 script tests, schema/examples validation, requirements-checklist synchronization, fixture reproducibility, final documentation consistency, and 29/29 Mermaid blocks passed. [Doc check](spikes/evidence/docs-windows.json) and [schema check](spikes/evidence/schema-windows.json) retain the final results. Workflow YAML parsed and actionlint 1.7.12 passed (shellcheck/pyflakes integrations unavailable locally).
- Spikes: three OCR helper tests and all 120 OCR subprocesses passed; six XLSX probe cases ran and both constrained edits passed independent verification; child-process checks passed. Both encryption choices passed value round trips, reopen, credential cleanup and sensitive-marker scans. Standalone spike Clippy passed for lifecycle, XLSX and both encryption feature choices.

These checks establish the foundation and finite spike results. They do not establish the one-hour offline network-capture suite, a document automation workflow, model performance, sidecar installer packaging, macOS support, or 8 GB usability.

## Corrections and review

- Fixed a visible blank isolation iframe caused by strict CSP blocking Tauri's inline style. Bundled CSS hides the frame; real WebView verification passed without weakening CSP.
- Added missing `forbid(unsafe_code)` to the host build script and spike crates; replaced encryption's silent key-store fallback with a failing result and verified credential cleanup, value round trips and ciphertext refusals.
- Bounded worker response allocations and reject partial length prefixes; job-only descendant cleanup now has a Windows assertion.
- Corrected the SRS paragraph that placed document parsing in the trusted core: PDF/OCR parsing belongs in the bounded separate worker. Updated design, traceability and checklist evidence in the same change.
- Replaced stale scaffolding/setup instructions with the actual Windows setup and embedded-assets launch method. Turned lifecycle and encryption spike CI failures into blocking failures; added the independently observed XLSX regression gate.
- Corrected doc/Mermaid discovery to exclude ignored `.localloop-dev` vendor documentation while still checking repository and spike docs; a regression test covers that boundary.

OCR, constrained XLSX writing and encryption ADRs remain **Proposed** for owner review. The accepted Windows-priority ADR records an instruction already given by the owner. Review the milestone report before authorizing M1.1; no domain, policy or execution implementation has been started.
