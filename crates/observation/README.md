# `observation`

> **Skeleton only (LL-001):** the crate builds but has no public API yet. Design: [component-design.md §3.6](../../docs/architecture/component-design.md#36-observation--recording-sessions).

**Layer 2: Workflow Observation.** Records demonstrations, but only what the user allowed and only while they can see that it is recording.

## Responsibilities

- Recording sessions with explicit consent bound to the exact scope summary shown to the user (FR-015).
- Visible recording indicator, plus pause, resume, and stop (FR-016).
- Capture only inside the selected scope (FR-017). In the MVP that means file operations in selected folders (FR-020), together with in-app document annotation and spreadsheet mapping (FR-021, FR-022).
- Exclude protected input such as password fields, and let the user redact events before any analysis (FR-018, FR-019).
- Retention and deletion of recordings (FR-027).
- Later phases: browser capture in the managed profile (FR-024, Phase 2) and desktop capture through accessibility APIs (FR-025, Phase 3).

## Must not

- Depend on `execution-engine` or adapters.
- Install OS-wide keyboard or mouse hooks in the MVP (A-03).

## First backlog items

LL-065 (session state machine and consent hash), LL-067 (scoped file-event capture), LL-072 (retention). All are milestone M1.4.
