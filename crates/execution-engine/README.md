# `execution-engine`

> **Planned — no code yet.** Design: [component-design.md §3.3](../../docs/architecture/component-design.md#33-execution-engine--orchestration-journal-control-decisions) and the run and step state machines in [§4](../../docs/architecture/component-design.md#4-state-machines).

**Layer 5: Execution Engine.** Runs approved workflow versions, one operation at a time, and asks the policy engine before every dispatch.

## Responsibilities

- Run orchestrator state machine, with one active run at a time (FR-042, FR-101).
- Exact Replay: execute the approved plan with variables, loops, and explicit conditions; no model chooses actions (FR-042 to FR-045).
- Adaptive Execution at **bounded decision points**: ask the `DecisionProvider` port to choose among declared options, check consistency, apply confidence thresholds and budgets, and escalate to the user (FR-047 to FR-051).
- Control channel: pause, resume, and emergency stop with cancellation tokens (FR-097, FR-098).
- Approval service with single-use tokens bound to the operation hash (FR-099).
- Write-ahead journal and checkpoints; recover interrupted runs on startup (FR-091, NFR-004).
- Error rules and bounded retries; consequential operations are never retried automatically (FR-089).
- Review queue, duplicate protection, and report writing (FR-061, FR-066, FR-067).

## Must not

- Call an adapter without an `AuthorizedOperation`.
- Mark a run as completed. Outcome classification belongs to `verification-engine`.

## First backlog items

LL-041 (orchestrator), LL-042 (control channel), LL-043 (retries), LL-045 (crash recovery), LL-046 (approvals), LL-047 (review queue), LL-048 (duplicates), LL-049 (reports), LL-080 (decision points, M1.5).
