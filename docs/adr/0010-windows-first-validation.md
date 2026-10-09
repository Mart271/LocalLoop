# ADR-0010: Prioritize Windows and defer macOS validation

| Field | Value |
|---|---|
| Status | Accepted |
| Date | 2026-10-10 |
| Deciders | Project owner, explicit instruction in the development session |
| Related requirements | A-01, NFR-008, NFR-013, NFR-028 |

## Context

The owner instructed us to finish and verify M1.0 while prioritizing Windows and setting macOS aside. The original roadmap requires evidence on both platforms and reference machines; neither a Mac nor an 8 GB reference machine is available in this session.

## Decision

Windows is the active implementation and milestone validation gate. Defer macOS builds, packaging, benchmarks and on-device checks; remove macOS from the active CI matrices. Record every deferred item explicitly. Preserve the shared architecture and the longer-term platform targets in the SRS.

M1.0 may close for its Windows scope after local checks and spike reports, with CI changes reviewed locally. A local pass is not evidence that a remote CI run passed. NFR-008 and the original cross-platform MVP release gate remain unverified; this decision does not establish 8 GB usability or macOS support. EV-01 remains deferred to M1.5 and EV-09 to Phase 2, following the recorded 2026-10-09 decisions.

## Consequences

- Windows work can progress without claiming unavailable macOS or reference-hardware results.
- Re-enable and run the macOS matrix when the owner reactivates that platform.
- M1.6 must resolve reference-hardware acceptance and the release platform scope before release.

## Alternatives considered

| Option | Reason |
|---|---|
| Keep macOS as a blocking milestone gate | Conflicts with the owner's current instruction |
| Remove all macOS architecture and requirements | Broader than the requested temporary deferral |

## Validation

The progress report distinguishes observed Windows evidence, remote CI status, and deferred checks. Performance evidence identifies the measured machine, versions, fixture seed, date, model and method.
