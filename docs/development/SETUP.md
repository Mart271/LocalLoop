# LocalLoop — Development Setup

| Field | Value |
|---|---|
| Version | 0.1 |
| Date | 2026-10-09 |

> **Current state:** this repository contains documentation, a draft workflow schema, example workflows, and documentation checks. **There is no application code yet.** Nothing can be built or run as an app. The first code milestone is M1.0 in the [Roadmap](ROADMAP.md).

---

## 1. What you can run today

### Prerequisites

- Git
- Python 3.10 or later
- Node.js (current LTS) and npm, only for the Mermaid diagram check

### Documentation and schema checks

```bash
# Requirement IDs, cross-references, traceability coverage, relative links and anchors
python3 scripts/check_docs.py

# Validate example workflows against the draft JSON Schema
python3 -m pip install -r scripts/requirements.txt
python3 scripts/validate_schemas.py

# Render every Mermaid diagram to catch syntax errors (downloads Chromium via Puppeteer)
npm install --no-save @mermaid-js/mermaid-cli@11.17.0
python3 scripts/validate_mermaid.py --mmdc node_modules/.bin/mmdc
```

On Linux CI runners, Chromium may need `--puppeteer-config scripts/puppeteer-config.json` (disables the Chromium sandbox for rendering trusted, repository-owned diagrams only).

The same checks run in GitHub Actions (`.github/workflows/ci.yml`) once the repository is pushed.

## 2. Toolchain for application development (from M1.0)

These are the **proposed** prerequisites, pending the ADRs in [docs/adr](../adr/README.md). Pin exact versions in `rust-toolchain.toml` and `package.json` when the code is created.

| Tool | Purpose | Notes |
|---|---|---|
| Rust (stable, via `rustup`) | Core crates, Tauri host, document worker | Add `rustfmt`, `clippy` |
| Node.js (current LTS) + pnpm | React UI, TypeScript types, Mermaid checks; browser bridge in Phase 2 | |
| Tauri 2 prerequisites | Desktop shell | Windows: Microsoft C++ Build Tools and WebView2; macOS: Xcode Command Line Tools |
| `cargo-deny`, `cargo-audit` | Dependency advisories, licences, bans | CI from M1.0 |
| SQLite tooling (optional) | Inspecting local databases during development | |

Platform notes:

- **Windows:** develop on x64; test with a standard (non-admin) user account; keep Excel installed on one test machine to reproduce file-lock behaviour (EXC-08).
- **macOS:** expect permission prompts (Files and Folders; later Accessibility and Screen Recording). Reset with `tccutil` during testing.

## 3. Commands to begin development (M1.0)

Run these when starting milestone M1.0 ([BACKLOG](BACKLOG.md) LL-001, LL-002). They are listed here for planning and have **not** been run in this repository.

```bash
# 1. Rust workspace and crates (LL-001)
#    `cargo init` works inside the existing folders (each currently holds only a README.md)
cargo init --lib --vcs none crates/workflow-engine
cargo init --lib --vcs none crates/policy-engine
cargo init --lib --vcs none crates/execution-engine
cargo init --lib --vcs none crates/verification-engine
cargo init --lib --vcs none crates/local-ai
cargo init --lib --vcs none crates/observation
cargo init --lib --vcs none crates/storage
cargo init --lib --vcs none --name adapter-files crates/adapters/files
cargo init --lib --vcs none --name adapter-documents crates/adapters/documents
cargo init --lib --vcs none --name adapter-spreadsheet crates/adapters/spreadsheet
# then create a root Cargo.toml with [workspace] members and shared lints

# 2. Desktop app (LL-002) — interactive; choose TypeScript + React + pnpm
cd apps
npm create tauri-app@latest desktop
```

## 4. Repository conventions

- **Branches:** `main` is protected once the repo is published; work on `feat/…`, `fix/…`, `docs/…`, `spike/…` branches.
- **Commits:** Conventional Commits (`feat(policy-engine): …`, `docs(srs): …`).
- **Requirement references:** PR descriptions and commit bodies cite requirement IDs (`FR-063`) and backlog IDs (`LL-037`).
- **Decisions:** significant design changes need an ADR ([template](../adr/template.md)).
- **No real documents:** use synthetic fixtures only (A-19). Never commit real invoices, customer data, credentials, or model files (`*.gguf` is git-ignored).

## 5. Git and GitHub

The repository is initialized locally. **No remote has been created and nothing has been pushed.** When the project owner approves publishing:

```bash
gh repo create <owner>/LocalLoop --private --source . --remote origin
git push -u origin main
```

Before making the repository public: choose a licence ([LICENSE_SELECTION.md](../../LICENSE_SELECTION.md)), enable private vulnerability reporting, and protect `main`.
