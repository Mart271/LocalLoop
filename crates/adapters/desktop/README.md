# `adapters/desktop`

> **Planned for Phase 3.** No code yet. Design: [SYSTEM_ARCHITECTURE §13](../../../docs/architecture/SYSTEM_ARCHITECTURE.md#13-platform-specific-integration-boundaries).

**Layer 5 adapter.** Automates native applications through accessibility APIs.

## Responsibilities

- Windows UI Automation (FR-078) and the macOS Accessibility API (FR-079) behind one interface.
- Keep a registry of tested applications, versions, and capabilities. Workflows for unregistered applications are labelled *untested* and need the user's explicit acknowledgement, because support is tested, never assumed (FR-080).
- Inspect in tiers: structural (accessibility tree) first, then OCR and traditional computer vision, then an optional local vision-language model (FR-081, FR-084).
- Observe, interpret, act, verify. A consequential action on a target that cannot be identified with confidence goes to the user instead (FR-082, FR-083).
- Simulated keyboard and mouse input only inside windows of granted applications, and every action needs an expected-effect postcondition.

## Expected exception

This is the one crate expected to need `unsafe` code for platform bindings. It will be isolated and justified in an ADR.

## Open questions

Accessibility coverage of target applications, and whether vision models are feasible on 8 GB machines: spike EV-05. Related requirements are *Unvalidated* until then.
