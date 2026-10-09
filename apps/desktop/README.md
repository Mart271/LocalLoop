# `apps/desktop`

> **Scaffolded (LL-002).** Tauri 2 host and React UI with a strict CSP, the isolation pattern, and one allowlisted command (`ping`). Run with `pnpm --filter desktop tauri dev`. Design: [component-design.md §3.10](../../docs/architecture/component-design.md#310-appsdesktop--composition-root-and-ipc) and [§11](../../docs/architecture/component-design.md#11-desktop-ipc-command-surface).

**Layer 1: User Interface**, and the **composition root**: the only place where all crates are wired together.

## Planned contents

| Path | Contents |
|---|---|
| `src/` | React + TypeScript UI: library, editor, recorder, mode recommendation, permissions, run monitor, approvals, review queue, history, models, settings |
| `src-tauri/` | Tauri 2 host in Rust: thin IPC command handlers (validate input → call a core service → map errors to user-facing messages) and shell services |

## Responsibilities

- Show every step, permission, external dependency, and limitation in plain language before a run (FR-010, NFR-024).
- Keep a visible automation indicator, and offer pause, resume, and emergency stop from the window, the tray or menu bar, and a global shortcut (FR-097, FR-098, FR-100).
- Present approvals and decision escalations, and never approve on the user's behalf (FR-099, FR-051).
- Expose only an allowlist of IPC commands with typed, validated inputs (NFR-014).

## Security baseline (planned)

- Load only bundled local content, with a strict Content Security Policy (`default-src 'self'`); no remote content in the WebView.
- Minimal Tauri capabilities; no shell or generic file-system plugin exposed to the UI.
- No telemetry, crash upload, or update checks by default (A-12).

## Scaffolding note

If the Tauri scaffolder refuses to write into a non-empty folder, move this README out temporarily and merge it back afterwards.
