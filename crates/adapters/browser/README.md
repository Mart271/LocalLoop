# `adapters/browser`

> **Planned for Phase 2**, following owner decision D-02 (2026-10-09). EV-09 is deferred to that phase. No code yet. Design: [ADR-0004](../../../docs/adr/0004-browser-automation-bridge.md), [component-design.md §10.3](../../../docs/architecture/component-design.md#103-core--browser-bridge-p2-d-02-deferral-confirmed).

**Layer 5 adapter.** The Rust-side client of the [browser bridge](../../../sidecars/browser-bridge/README.md), which hosts Playwright.

## Responsibilities

- Translate `AuthorizedOperation`s such as `browser.navigate`, `browser.click`, and `browser.download` into bridge requests (FR-068, FR-069).
- Target elements by role and accessible name first, then label, test ID, and CSS. Visual fallback comes only in Phase 3 (FR-070).
- Allow only hosts in the workflow's allowlist. The bridge enforces this again with request interception (FR-074).
- Resolve credential references from the OS credential store in memory only. Values never appear in definitions, logs, or prompts (FR-075).
- Pause and hand control to the user on login challenges, CAPTCHAs, or multi-factor prompts. LocalLoop does not bypass them (FR-076, EXC-26).
- Downloads land in a LocalLoop staging folder and are moved under policy by `files.move`.
