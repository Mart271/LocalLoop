# ADR-0001: Initial architecture — layered core with AI outside the trusted execution path

| Field | Value |
|---|---|
| Status | Proposed |
| Date | 2026-10-09 |
| Deciders | Project owner (pending review) |
| Related requirements | FR-031, FR-048, FR-085, FR-104, FR-106, FR-112, NFR-014, NFR-015, NFR-030 |

## Context

The proposal defines seven layers (P§5) and a central principle: *"Use AI to understand work. Use reliable automation to execute it."* It requires that AI cannot bypass the workflow compiler, policy engine, permissions, or verification (P§5 Layer 4, P§15.6), that deterministic workflows run without a model (P§6), and that the product works on 8 GB laptops (P§7). It also proposes Tauri + React, Rust, SQLite, and llama.cpp.

We need a structure that makes these properties hold *by construction*, not only by convention, and that a small team can build incrementally, model-free path first.

## Decision

1. **Process structure:** a Tauri desktop process (React UI + Rust core) plus on-demand child processes: a **document worker** for parsing untrusted files, an **inference sidecar** for the local model (ADR-0003), and, from Phase 2, a **browser bridge** (ADR-0004).
2. **Module structure:** a Rust workspace with crates matching the layers: `workflow-engine` (domain model, ports, compiler, planner, recommender), `policy-engine`, `execution-engine`, `verification-engine`, `local-ai`, `observation`, `storage`, and `adapters/*`. The desktop app is the only composition root.
3. **AI outside the trusted path:** `local-ai` depends only on `workflow-engine`; it implements ports that return untrusted data. It cannot depend on `policy-engine`, `execution-engine`, `storage`, or adapters. CI enforces forbidden dependencies (NFR-030).
4. **Capability by construction:** adapters execute only `AuthorizedOperation` values, which only `policy-engine` can construct.
5. **Rule-based mode recommendation:** the recommendation (P§4.3) is computed by deterministic rules from factor signals; a model may help derive signals but never makes the recommendation (A-09).
6. **Verification is independent:** postconditions are evaluated by re-observing state through read-only observers, not by trusting adapter results.
7. **Model-free first:** the first end-to-end milestone runs the MVP workflow with no model installed.

## Consequences

- Positive: the security property "AI cannot execute" is enforced by the type system and the dependency graph, not only by code review; Basic Automation works without a model; parser crashes do not take down the app; models can be unloaded by ending a process.
- Negative: more processes to package and supervise; IPC protocols to version; ports add some indirection.
- Follow-up: define IPC protocols (component-design §10); add the forbidden-dependency check to CI when the Cargo workspace is created; spike packaging of child processes on both OSes (Phase 1).

## Alternatives considered

| Option | Why not chosen |
|---|---|
| Single process, everything in-process | Simpler, but a parser or inference crash kills the app and memory cannot be fully released by unloading |
| Agent-centric design where the model plans and executes with tools | Conflicts with P§5 Layer 4 and P§15.3; hard to verify; continuous inference on 8 GB machines |
| Model-based mode recommendation | Less explainable and not reproducible; conflicts with "determinism whenever possible" |
| Electron + Node core | Larger footprint; Node in the privileged process widens the attack surface; the proposal names Tauri and Rust |

## Validation

- Phase 1 exit: model-free MVP workflow passes on both reference machines; forbidden-dependency check in CI; fault-injection suite shows no unverified success claims.
- Revisit if process overhead makes the 8 GB target unreachable (NFR-008) or if packaging child processes proves impractical on either OS.
