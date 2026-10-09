# ADR-0004: Browser automation through a Playwright bridge process

| Field | Value |
|---|---|
| Status | Proposed (pending EV-09) |
| Date | 2026-10-09 |
| Deciders | Project owner (pending review) |
| Related requirements | FR-024, FR-068 to FR-076, FR-052, A-11, D-02 |

## Context

The proposal names Playwright and the Chrome DevTools Protocol for browser automation (P§4.4) and asks for semantic element identification. Playwright's official libraries target Node.js, Python, Java, and .NET; there is no official Rust binding. LocalLoop must work offline and must not touch the user's everyday browser profile.

## Decision

1. A **browser bridge** process (Node.js + Playwright) is controlled by the Rust core over JSON-RPC on stdio (component-design §10.3).
2. The bridge launches a **managed profile** in an installed Chromium-based browser (Edge or Chrome channel) or a bundled Chromium; which one is decided by EV-09 based on offline packaging and reliability.
3. Host allowlists are enforced in both the core (policy) and the bridge (request interception).
4. The bridge writes downloads only to its staging folder; files reach user folders through policy-checked `files.move`.
5. The core talks to the bridge only through a `BrowserAdapter` interface, so the implementation can be replaced (for example by direct CDP from Rust) without touching policy or execution.

**D-02 scope decision (owner, 2026-10-09):** browser automation and EV-09 are deferred to Phase 2. The implementation proposal above remains Proposed; browser packaging is not an M1.0 gate.

## Consequences

- Positive: mature locators (role, label, text) matching FR-070; auto-waiting; a large community; CDP available when needed.
- Negative: a Node.js runtime must be packaged offline (embedded runtime or single-executable build); larger installer; two languages in the codebase; Playwright browser downloads must be disabled in favour of bundled or installed browsers.
- Follow-up: EV-09 spike: package the bridge for Windows and macOS without network, measure installer size, test against local fixture sites, and decide D-02 (whether basic browser support is in the MVP).

## Alternatives considered

| Option | Why not chosen (for now) |
|---|---|
| Direct CDP from Rust (for example `chromiumoxide`) | One language, smaller footprint; but locator and auto-wait logic would have to be built; Chromium-only. Strong fallback if EV-09 packaging is impractical |
| Playwright for Python | Would add a Python runtime instead of Node; no advantage for a Rust core |
| WebDriver BiDi | Emerging standard; tooling less mature today |
| Driving the user's own browser profile | Exposes the user's sessions, cookies, and history; conflicts with least privilege |

## Validation

EV-09 report: offline install succeeds on both OSes; fixture-site tests pass for navigate, click, fill, select, download; installer size impact recorded.
