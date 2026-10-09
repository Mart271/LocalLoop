# CLAUDE.md — working notes for LocalLoop

LocalLoop is an **offline-first desktop workflow automation app** (Tauri 2 + React/TypeScript UI, Rust core). It turns repetitive document work into verified, reusable automations that run entirely on the user's laptop. Local AI may *propose*; only the compiler and policy engine *authorize*. Principle: *Intelligence when necessary. Determinism whenever possible. User control always.*

Current milestone and status: [docs/development/PROGRESS.md](docs/development/PROGRESS.md). Read it first when resuming.

## Doc map (the docs are the source of truth)

| Need | Read |
|---|---|
| Scope, reference scenario, fixtures F1–F6 | `docs/development/MVP_SCOPE.md` |
| Milestones and exit criteria | `docs/development/ROADMAP.md` §2 |
| Work items (LL-nnn, "Done when") | `docs/development/BACKLOG.md` |
| Architecture, dependency rules | `docs/architecture/SYSTEM_ARCHITECTURE.md` (§6.1) |
| Operation catalog, state machines, storage, IPC | `docs/architecture/component-design.md` |
| Threats, taint table, approvals | `docs/architecture/security-architecture.md`, `data-flow.md` |
| Requirements (FR/NFR/EXC) | `docs/requirements/SRS.md` |
| Test case IDs and where tests live | `docs/requirements/requirements-traceability.md` §5 |
| Decisions | `docs/adr/` (template in `docs/adr/template.md`) |
| Spike reports | `docs/development/spikes/` |

If the docs are wrong or contradict each other: propose the fix, update SRS/ADR/design doc in the same commit, and flag it in the milestone report. Never diverge silently.

## Non-negotiable rules

- **`policy-engine` is the only issuer of `AuthorizedOperation`** (sealed). Adapters accept nothing else.
- **Closed catalog:** only the operations in component-design §2.2 and constructs in §2.3. Never add `shell.exec`, script/eval, generic HTTP, permanent delete, or anything in §2.5.
- **Default deny**, audit-logged.
- **Forbidden crate edges** (checked by `scripts/check_crate_deps.py`): `local-ai` → policy/execution/adapters/storage; `adapters/*` → `local-ai`; `observation` → execution/adapters; `workflow-engine` → any internal crate.
- **Taint:** document/page/screen/model values are `Tainted<T>`; only explicit sanitizers produce clean values, per parameter position. Path segments go through `sanitize_path_segment`; paths are canonicalized and handles re-verified.
- **Verification re-observes state**; never trust adapter return values; never report `completed` without verified postconditions.
- **Never lose user data:** no overwrite, backup first, temp file + atomic replace, re-read, neutralize formulas. No delete operation.
- **Human control:** pause/resume/stop (window, tray, global shortcut); approvals hash-bound and single-use.
- **Audit:** append-only journal; hash-chained audit log with verify.
- **Single user, no accounts/roles/RBAC.** Grants, location scopes, approvals instead.
- **Offline:** product code makes no network calls (no telemetry, update checks, CDN fonts, remote scripts). Honour `LOCALLOOP_STRICT_OFFLINE=1`.
- **Tauri:** CSP `default-src 'self'`, minimal capabilities, allowlisted IPC (component-design §11), no shell/fs plugin, never render untrusted text as HTML.
- Document parsing only in the separate document worker process, with size/page/time limits.
- **Honesty:** never claim something builds, passes, or performs without running it; cite hardware and versions (NFR-013). The dev laptop is 16 GB — **not** an 8 GB reference machine; macOS on-device checks are *pending* unless run on CI.

## Code quality

- Rust: `#![forbid(unsafe_code)]` in every crate (exceptions need an ADR); typed errors (`thiserror`); no `unwrap`/`expect`/`panic!` outside tests (workspace clippy lints); `cargo fmt` and `clippy -D warnings` clean.
- TypeScript: `strict`, no `any`; IPC types generated from Rust by `ts-rs` into `packages/shared` (never hand-written).
- No placeholder code that pretends to work: unbuilt features are absent or return a typed `NotSupported` and stay hidden in the UI.
- Every backlog item: tests run and passing; docs updated; test path added in traceability §5; doc and schema checks pass.
- Lockfiles committed; `cargo deny`, `cargo audit`, `pnpm audit` in CI.

## Commands (Windows PowerShell; run from repo root)

```powershell
python scripts\check_docs.py                 # IDs, traceability, links
python scripts\validate_schemas.py           # schema + examples (pip install -r scripts\requirements.txt)
python scripts\check_crate_deps.py           # forbidden crate dependencies (NFR-030)
cargo fmt --all --check
cargo clippy --workspace --all-targets -- -D warnings
cargo test --workspace
cargo deny check                             # licences, bans, advisories, sources
cargo audit
pnpm install --frozen-lockfile
pnpm -r lint; pnpm -r typecheck; pnpm -r test
pnpm --filter desktop tauri dev              # run the desktop app
pnpm gen:types                               # regenerate packages/shared from Rust (ts-rs)
python tools\fixtures\generate.py            # synthetic fixtures F1–F6 -> tests\fixtures\generated
```

Mermaid check (needs Node): `npm install --no-save @mermaid-js/mermaid-cli@11.17.0` then `python scripts\validate_mermaid.py --mmdc "<abs path>\node_modules\.bin\mmdc.cmd"` (on Windows pass the absolute `.cmd` path).

## Layout

```text
crates/            Rust workspace members (workflow-engine, policy-engine, execution-engine,
                   verification-engine, local-ai, observation, storage, adapters/{files,documents,spreadsheet})
apps/desktop/      Tauri 2 host (src-tauri) + React UI (src) — composition root
packages/shared/   Generated TS types for IPC
schemas/, examples/ Workflow JSON Schema 0.1 and example workflows
spikes/            Throwaway spike code, NOT in the workspace and never shipped
tools/fixtures/    Synthetic fixture generator (dev only)
tests/             Shared test cases, fixtures, e2e
scripts/           Doc, schema, and dependency checks
docs/              Requirements, architecture, ADRs, roadmap, spikes, progress
```

## Git rules

- One branch per milestone (`feat/m1.0-foundation`, `feat/m1.1-core-domain`, …). Small Conventional Commits citing backlog and requirement IDs, e.g. `feat(policy-engine): seal AuthorizedOperation (LL-021, FR-104)`.
- **Never push, open PRs, or create issues without the owner's explicit OK** (pushing `feat/m1.0-foundation` for CI was approved on 2026-10-09; PRs were not).
- Never commit secrets, real documents, model files (`*.gguf`), build output, `node_modules`. Fixtures are synthetic only (A-19).
- `.gitattributes` enforces LF; don't fight it. If git reports "dubious ownership", stop and ask.
- Stop at the end of each milestone, report, update PROGRESS.md, and wait for the owner's OK.
