# LocalLoop — Development Setup

| Field | Value |
|---|---|
| Version | 0.2 |
| Date | 2026-10-10 |

The Windows foundation shell and Cargo workspace exist. See [PROGRESS.md](PROGRESS.md) for measured evidence and remaining work. macOS validation is deferred by the owner ([ADR-0010](../adr/0010-windows-first-validation.md)).

## 1. Prerequisites

- Rust 1.99.0, rustfmt and Clippy, pinned in `rust-toolchain.toml`.
- Node LTS in the supported `>=24 <27` range; CI uses `.nvmrc`. The measured Windows session used Node 24.11.1.
- pnpm 12.10.1, pinned in `package.json`. Install with `npm install --global pnpm@12.10.1`. Older pnpm/corepack shims may need reinstalling after the native pnpm executable migration.
- Python 3.12 or later. Use a repository virtual environment for pinned fixture/schema dependencies.
- Microsoft C++ build tools with a Windows SDK; WebView2 runtime.
- `cargo-deny` and `cargo-audit` for advisories/licence checks.

Development-time downloads are allowed. Product code must remain offline: no telemetry, update checks, remote fonts/scripts, or automatic model downloads.

## 2. Install and validate (PowerShell, repository root)

```powershell
rustup toolchain install 1.99.0 --profile minimal --component rustfmt --component clippy
npm install --global pnpm@12.10.1
pnpm install --frozen-lockfile
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r scripts/requirements.txt -r tools/fixtures/requirements.txt
cargo install cargo-deny --locked
cargo install cargo-audit --locked

.venv/Scripts/python.exe scripts/check_docs.py
.venv/Scripts/python.exe scripts/sync_requirements_checklist.py --check
.venv/Scripts/python.exe scripts/validate_schemas.py
.venv/Scripts/python.exe -m unittest discover -s scripts/tests -v
.venv/Scripts/python.exe scripts/check_crate_deps.py
.venv/Scripts/python.exe tools/fixtures/generate.py --check
pnpm --filter desktop build
cargo fmt --all --check
cargo clippy --workspace --all-targets --locked -- -D warnings
cargo test --workspace --locked
cargo deny --locked check
cargo audit --deny warnings
pnpm -r lint
pnpm -r typecheck
pnpm -r test
pnpm audit --audit-level low
pnpm gen:types
git diff --exit-code -- packages/shared/src/generated
```

Install the Rust toolchain before running parallel Cargo commands: competing rustup installers can race on component downloads. Run each check as a separate command, or stop a script on the first nonzero exit code.

## 3. Run the desktop shell

```powershell
$env:LOCALLOOP_STRICT_OFFLINE = "1"
pnpm --filter desktop tauri dev
```

For a standalone binary with embedded assets:

```powershell
pnpm --filter desktop tauri build --debug --no-bundle
& ./target/debug/localloop.exe
```

A plain `cargo build` produces a development host that expects Vite at the configured dev URL. It is not a standalone offline shell. Tauri's build command enables `tauri/custom-protocol`; CI also checks that embedded-assets build directly. The M1.0 shell supports only ping and clearly labels later features as unavailable.

Windows benchmark commands and reproduction notes: [spike reports](spikes/README.md). Installer creation is M1.6 work.

## 4. Mermaid diagrams

Use an isolated development-tool prefix so the diagram checker does not change the UI lockfile:

```powershell
npm install --prefix .localloop-dev/tooling @mermaid-js/mermaid-cli@11.17.0
$mermaid = (Resolve-Path .localloop-dev/tooling/node_modules/.bin/mmdc.cmd).Path
.venv/Scripts/python.exe scripts/validate_mermaid.py --mmdc $mermaid
```

Linux CI uses `scripts/puppeteer-config.json` for trusted repository diagrams. The tooling prefix and downloaded browsers/models are ignored and never shipped.

## 5. Repository conventions

One branch per milestone; small Conventional Commits citing backlog and requirement IDs. Update docs and requirement evidence with code. Use synthetic fixtures only (A-19); never commit credentials, real documents, model binaries, build output or dependencies.

The `origin` remote exists and foundation PR #4 is merged into `main`. Pushing `feat/m1.0-foundation` for CI was approved on 2026-10-09. PRs, issues and other pushes need the owner's explicit OK. Stop for review at each milestone boundary.

macOS toolchain, platform behavior, packaging and on-device checks remain deferred. Passing Windows checks does not establish macOS support or 8 GB reference-machine usability.
