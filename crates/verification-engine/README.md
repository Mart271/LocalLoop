# `verification-engine`

> **Planned — no code yet.** Design: [component-design.md §3.4](../../docs/architecture/component-design.md#34-verification-engine--postconditions-outcomes-recovery).

**Layer 6: Verification and Recovery.** Decides whether work actually happened.

## Responsibilities

- Evaluate postconditions and success conditions by **re-observing state** through read-only `StateObserver` ports, never by trusting an adapter's return value (FR-085).
- Classify items and runs as *completed*, *partially completed*, *failed*, or *unverified* ([SRS §16.1](../../docs/requirements/SRS.md#161-outcome-definitions); FR-086).
- Never report *completed* unless every required condition was verified (FR-087).
- Choose recovery actions from each step's declared rules (FR-089).
- Build rollback plans from the undo journal for reversible operations (FR-090).
- Require validation before any recovery-originated change is saved as a new workflow version (FR-092).

## Must not

- Change state. Observers are read-only, so verification can always run safely, including after a crash.

## First backlog items

LL-038 (observers and MVP postconditions), LL-039 (outcome classifier), LL-044 (rollback executor).
