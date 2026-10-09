# `sidecars/browser-bridge`

> **Planned for Phase 2** (a basic subset moves into the MVP only if decision D-02 is confirmed). No code yet. Design: [ADR-0004](../../docs/adr/0004-browser-automation-bridge.md), [protocol](../../docs/architecture/component-design.md#103-core--browser-bridge-p2-mvp-if-d-02).

A small Node.js process that hosts **Playwright** and controls a **managed Chromium-based browser profile** reserved for LocalLoop. It exists because Playwright has no official Rust binding (A-11).

## Contract

- Speaks JSON-RPC 2.0 over stdio with the Rust [browser adapter](../../crates/adapters/browser/README.md). It opens no listening network port.
- Exposes a fixed method set: `session.open`, `page.navigate`, `page.snapshot`, `element.click`, `element.fill`, `element.select`, `download.await`, `session.close`. There is no "run this script" method.
- Enforces the host allowlist again with request interception and reports `request.blocked`.
- Reports `challenge.detected` for login, CAPTCHA, or multi-factor pages so the user can take over.
- Never sees credential values except in memory, for a single fill.

## Open questions (spike EV-09)

- Packaging a Node.js runtime and browser for fully offline installation, and the installer size cost.
- Using the system's Chrome or Edge versus a bundled browser.
- Holding non-GET requests triggered by model-chosen actions until they are approved.
