# LocalLoop — Requirements Traceability

| Field | Value |
|---|---|
| Version | 0.1 (draft) |
| Date | 2026-10-09 |
| Related | [SRS](SRS.md) · [Use cases](use-cases.md) · [Roadmap](../development/ROADMAP.md) · [Backlog](../development/BACKLOG.md) |

This matrix links **Product Objective → Requirement → Architecture Component → Test Case → Development Phase**. Every FR and NFR in the SRS appears exactly once in the matrix; every MVP requirement has at least one test case. `scripts/check_docs.py` enforces these rules in CI.

> **Status:** Test cases are *planned* specifications. None has been implemented or run.

## 1. Product Objectives

| ID | Objective | Proposal source |
|---|---|---|
| OBJ-01 | Operate without cloud AI, remote processing, or online accounts | P§1, P§6 |
| OBJ-02 | Let non-programmers create automations from demonstrations or simple instructions | P§3, P§4.1, P§16 |
| OBJ-03 | Execute predictable workflows deterministically and reliably | P§1, P§4.2 (Mode A) |
| OBJ-04 | Handle variation with local AI inside approved constraints | P§4.2 (Mode B), P§4.6 |
| OBJ-05 | Make execution modes and workflow behaviour transparent and explainable | P§4.3, P§13, P§15.8 |
| OBJ-06 | Keep the user in control: least privilege, approvals, stop, no AI-granted authority | P§5 Layer 4, P§9, P§15.6 |
| OBJ-07 | Guarantee verified outcomes and data integrity | P§4.7, P§13, P§15.9 |
| OBJ-08 | Run on ordinary 8 GB laptops | P§7, P§15.5 |
| OBJ-09 | Keep workflows portable, versioned, and user-owned | P§4.8, P§14 |
| OBJ-10 | Protect the privacy of recorded and processed data | P§9, P§15.7 |
| OBJ-11 | Extend automation to browsers and native applications | P§4.4, P§4.5, P§4.6 |
| OBJ-12 | Engineer the product so its claims are measurable and maintainable | P§11, P§13, P§14 |
| OBJ-13 | Demonstrate real productivity value against alternatives | P§10, P§13 |

## 2. Legends

**Components** refer to modules in [SYSTEM_ARCHITECTURE.md §5](../architecture/SYSTEM_ARCHITECTURE.md#5-layered-architecture): `ui` (apps/desktop), `observation`, `local-ai`, `workflow-engine`, `policy-engine`, `execution-engine`, `verification-engine`, `storage`, `adapters/files`, `adapters/documents`, `adapters/spreadsheet`, `adapters/browser`, `adapters/desktop`, `document-worker`, `browser-bridge`, `platform` (OS abstraction), `installer`, `ci`. `system` means the requirement is verified on the whole application.

**Test levels:** U = unit, I = integration, E2E = end-to-end through the UI, S = system test on reference machines or VMs, EV = evaluation study (`EV-nn`), UX = usability study, R = review/inspection.

**Milestones** (`M1.0` … `M4.4`) are defined in the [Roadmap](../development/ROADMAP.md). The MVP release is the end of Phase 1 (milestone M1.6).

## 3. Traceability Matrix — Functional Requirements

| Objective | Requirement | Title | Release | Validation | Components | Test cases | Phase · Milestone |
|---|---|---|---|---|---|---|---|
| OBJ-02 | FR-001 | Create a workflow with an objective | MVP | Committed | ui, workflow-engine, storage | TC-001 | Phase 1 · M1.3 |
| OBJ-09 | FR-002 | Portable, documented workflow format | MVP | Committed | workflow-engine | TC-002 | Phase 1 · M1.1 |
| OBJ-09 | FR-003 | Immutable versioning | MVP | Committed | workflow-engine, storage | TC-003 | Phase 1 · M1.1 |
| OBJ-09 | FR-004 | Browse and search the workflow library | MVP | Committed | ui, storage | TC-004 | Phase 1 · M1.3 |
| OBJ-09 | FR-005 | Duplicate a workflow | MVP | Committed | ui, storage | TC-005 | Phase 1 · M1.3 |
| OBJ-09 | FR-006 | Archive and restore a workflow | MVP | Committed | ui, storage | TC-006 | Phase 1 · M1.3 |
| OBJ-09 | FR-007 | Export a workflow | MVP | Committed | workflow-engine, storage | TC-007 | Phase 1 · M1.3 |
| OBJ-09 | FR-008 | Import a workflow | MVP | Committed | workflow-engine, policy-engine | TC-008 | Phase 1 · M1.3 |
| OBJ-09 | FR-009 | Version history and revert | MVP | Committed | ui, storage | TC-009 | Phase 1 · M1.3 |
| OBJ-05 | FR-010 | Pre-execution inspection | MVP | Committed | ui, workflow-engine | TC-010 | Phase 1 · M1.3 |
| OBJ-06 | FR-011 | Lifecycle state enforcement | MVP | Committed | workflow-engine, execution-engine | TC-011 | Phase 1 · M1.1 |
| OBJ-02 | FR-012 | Workflow editor | MVP | Committed | ui, workflow-engine | TC-012 | Phase 1 · M1.3 |
| OBJ-02 | FR-013 | Create from structured instruction or template | MVP | Committed | ui, workflow-engine | TC-013 | Phase 1 · M1.3 |
| OBJ-05 | FR-014 | Known limitations | MVP | Committed | workflow-engine, ui | TC-014 | Phase 1 · M1.3 |
| OBJ-10 | FR-015 | Recording consent and scope selection | MVP | Committed | observation, ui | TC-015 | Phase 1 · M1.4 |
| OBJ-06 | FR-016 | Recording indicator and controls | MVP | Committed | observation, ui | TC-016 | Phase 1 · M1.4 |
| OBJ-10 | FR-017 | Scope-restricted capture | MVP | Committed | observation | TC-017 | Phase 1 · M1.4 |
| OBJ-10 | FR-018 | Protected input exclusion | MVP | Committed | observation | TC-018 | Phase 1 · M1.4 |
| OBJ-10 | FR-019 | Review and redact before analysis | MVP | Committed | observation, ui | TC-019 | Phase 1 · M1.4 |
| OBJ-02 | FR-020 | File-operation demonstration capture | MVP | Committed | observation | TC-020 | Phase 1 · M1.4 |
| OBJ-02 | FR-021 | Document field annotation | MVP | Committed | ui, adapters/documents | TC-021 | Phase 1 · M1.4 |
| OBJ-02 | FR-022 | Spreadsheet mapping demonstration | MVP | Committed | ui, adapters/spreadsheet | TC-022 | Phase 1 · M1.4 |
| OBJ-02 | FR-023 | Request additional examples | MVP | Unvalidated (EV-02) | local-ai, ui | TC-023 | Phase 1 · M1.5 |
| OBJ-11 | FR-024 | Browser interaction recording | P2 | Committed | observation, browser-bridge | TC-125 | Phase 2 · M2.2 |
| OBJ-11 | FR-025 | Desktop application interaction recording | P3 | Unvalidated (EV-05) | observation, adapters/desktop | TC-126 | Phase 3 · M3.2 |
| OBJ-11 | FR-026 | Authorized-window screenshots | P2 | Committed | observation | TC-127 | Phase 2 · M2.2 |
| OBJ-10 | FR-027 | Recording retention and deletion | MVP | Committed | observation, storage | TC-024 | Phase 1 · M1.4 |
| OBJ-02 | FR-028 | Analyze a demonstration into a proposed workflow | MVP | Unvalidated (EV-02) | local-ai, workflow-engine | TC-025 | Phase 1 · M1.5 |
| OBJ-02 | FR-029 | Variable detection | MVP | Unvalidated (EV-02) | local-ai | TC-025 | Phase 1 · M1.5 |
| OBJ-05 | FR-030 | Mark inferred elements | MVP | Committed | ui, workflow-engine | TC-026 | Phase 1 · M1.5 |
| OBJ-06 | FR-031 | Compile proposals | MVP | Committed | workflow-engine | TC-027 | Phase 1 · M1.1 |
| OBJ-01 | FR-032 | Model-free analysis fallback | MVP | Committed | workflow-engine, observation | TC-028 | Phase 1 · M1.4 |
| OBJ-07 | FR-033 | Explicit success conditions | MVP | Committed | workflow-engine | TC-029 | Phase 1 · M1.1 |
| OBJ-07 | FR-034 | Validation run and preview | MVP | Committed | workflow-engine, execution-engine, ui | TC-030 | Phase 1 · M1.3 |
| OBJ-05 | FR-035 | Mode recommendation | MVP | Committed | workflow-engine | TC-031 | Phase 1 · M1.3 |
| OBJ-05 | FR-036 | Recommendation explanation | MVP | Committed | workflow-engine, ui | TC-031 | Phase 1 · M1.3 |
| OBJ-05 | FR-037 | Accept or override | MVP | Committed | ui | TC-032 | Phase 1 · M1.3 |
| OBJ-06 | FR-038 | Compatibility check | MVP | Committed | workflow-engine | TC-032 | Phase 1 · M1.3 |
| OBJ-03 | FR-039 | Prefer determinism | MVP | Committed | workflow-engine | TC-031 | Phase 1 · M1.3 |
| OBJ-06 | FR-040 | Mode change requires revalidation | MVP | Committed | workflow-engine | TC-011 | Phase 1 · M1.3 |
| OBJ-05 | FR-041 | Record recommendation and decision | MVP | Committed | storage | TC-033 | Phase 1 · M1.3 |
| OBJ-03 | FR-042 | Deterministic step execution | MVP | Committed | execution-engine | TC-034 | Phase 1 · M1.3 |
| OBJ-03 | FR-043 | Variables, loops, and explicit conditionals | MVP | Committed | workflow-engine, execution-engine | TC-035 | Phase 1 · M1.3 |
| OBJ-01 | FR-044 | Model-free execution | MVP | Committed | execution-engine | TC-036 | Phase 1 · M1.3 |
| OBJ-03 | FR-045 | Handling unexpected conditions | MVP | Committed | execution-engine, verification-engine | TC-037 | Phase 1 · M1.3 |
| OBJ-04 | FR-046 | Data-only AI steps in Exact Replay | MVP | Unvalidated (EV-02) | execution-engine, local-ai | TC-038 | Phase 1 · M1.5 |
| OBJ-04 | FR-047 | Bounded decision points | MVP | Unvalidated (EV-03) | execution-engine, local-ai | TC-039 | Phase 1 · M1.5 |
| OBJ-06 | FR-048 | All model actions pass compiler and policy | MVP | Committed | policy-engine, execution-engine | TC-040 | Phase 1 · M1.5 |
| OBJ-04 | FR-049 | Uncertainty escalation | MVP | Committed | execution-engine, ui | TC-041 | Phase 1 · M1.5 |
| OBJ-06 | FR-050 | Adaptive budgets | MVP | Committed | execution-engine | TC-042 | Phase 1 · M1.5 |
| OBJ-04 | FR-051 | Manual decision fallback | MVP | Committed | execution-engine, ui | TC-043 | Phase 1 · M1.5 |
| OBJ-04 | FR-052 | Adaptive browser execution | P2 | Unvalidated (EV-03, EV-09) | execution-engine, local-ai, browser-bridge | TC-128 | Phase 2 · M2.3 |
| OBJ-04 | FR-053 | Adaptive recovery proposals | P2 | Unvalidated (EV-03) | verification-engine, local-ai | TC-129 | Phase 2 · M2.3 |
| OBJ-03 | FR-054 | Receive documents from an input location | MVP | Committed | adapters/files | TC-044 | Phase 1 · M1.2 |
| OBJ-03 | FR-055 | Text-layer extraction | MVP | Committed | document-worker | TC-045 | Phase 1 · M1.2 |
| OBJ-01 | FR-056 | Local OCR | MVP | Committed | document-worker | TC-046 | Phase 1 · M1.2 |
| OBJ-03 | FR-057 | Rule-based field extraction | MVP | Committed | workflow-engine | TC-047 | Phase 1 · M1.2 |
| OBJ-04 | FR-058 | Model-assisted field extraction | MVP | Unvalidated (EV-02) | local-ai | TC-048 | Phase 1 · M1.5 |
| OBJ-07 | FR-059 | Field provenance | MVP | Committed | adapters/documents, storage | TC-049 | Phase 1 · M1.2 |
| OBJ-07 | FR-060 | Data validation rules | MVP | Committed | workflow-engine | TC-050 | Phase 1 · M1.2 |
| OBJ-07 | FR-061 | Review queue routing | MVP | Committed | execution-engine, ui | TC-051 | Phase 1 · M1.3 |
| OBJ-03 | FR-062 | Spreadsheet update | MVP | Committed | adapters/spreadsheet | TC-052 | Phase 1 · M1.2 |
| OBJ-07 | FR-063 | Spreadsheet write safety | MVP | Committed | adapters/spreadsheet | TC-053 | Phase 1 · M1.2 |
| OBJ-03 | FR-064 | File organization | MVP | Committed | adapters/files | TC-054 | Phase 1 · M1.2 |
| OBJ-06 | FR-065 | Path sanitization of derived values | MVP | Committed | workflow-engine, policy-engine | TC-055 | Phase 1 · M1.1 |
| OBJ-05 | FR-066 | Execution report | MVP | Committed | execution-engine, adapters/files | TC-056 | Phase 1 · M1.3 |
| OBJ-07 | FR-067 | Duplicate and re-run protection | MVP | Committed | execution-engine, storage | TC-057 | Phase 1 · M1.3 |
| OBJ-11 | FR-068 | Managed browser session | MVP (cond.) | Unvalidated (EV-09) | adapters/browser, browser-bridge | TC-058 | Phase 2 · M2.1 (Phase 1 if D-02 includes browser) |
| OBJ-11 | FR-069 | Basic browser operations | MVP (cond.) | Unvalidated (EV-09) | adapters/browser, browser-bridge | TC-059 | Phase 2 · M2.1 (Phase 1 if D-02 includes browser) |
| OBJ-11 | FR-070 | Semantic element targeting | P2 | Committed | browser-bridge | TC-060 | Phase 2 · M2.2 |
| OBJ-11 | FR-071 | Advanced page interactions | P2 | Committed | browser-bridge | TC-061 | Phase 2 · M2.2 |
| OBJ-11 | FR-072 | Page data extraction | P2 | Committed | browser-bridge, adapters/browser | TC-062 | Phase 2 · M2.2 |
| OBJ-07 | FR-073 | Transition detection and submission validation | P2 | Committed | adapters/browser, verification-engine | TC-063 | Phase 2 · M2.2 |
| OBJ-06 | FR-074 | Host allowlist | MVP (cond.) / P2 | Committed | policy-engine, browser-bridge | TC-064 | Phase 2 · M2.1 (Phase 1 if D-02 includes browser) |
| OBJ-10 | FR-075 | Credential references | P2 | Committed | adapters/browser, platform | TC-065 | Phase 2 · M2.2 |
| OBJ-06 | FR-076 | Respect authentication and website restrictions | MVP (cond.) / P2 | Committed | browser-bridge, execution-engine | TC-066 | Phase 2 · M2.1 (Phase 1 if D-02 includes browser) |
| OBJ-03 | FR-077 | API-first execution | MVP | Committed | workflow-engine | TC-067 | Phase 1 · M1.1 |
| OBJ-11 | FR-078 | Windows UI Automation adapter | P3 | Unvalidated (EV-05) | adapters/desktop | TC-068 | Phase 3 · M3.1 |
| OBJ-11 | FR-079 | macOS Accessibility adapter | P3 | Unvalidated (EV-05) | adapters/desktop | TC-069 | Phase 3 · M3.1 |
| OBJ-11 | FR-080 | Application support registry | P3 | Committed | adapters/desktop, ui | TC-070 | Phase 3 · M3.1 |
| OBJ-08 | FR-081 | Tiered screen inspection | P3 | Committed | adapters/desktop, document-worker | TC-071 | Phase 3 · M3.3 |
| OBJ-07 | FR-082 | Observe, interpret, act, verify | P3 | Committed | execution-engine, verification-engine | TC-072 | Phase 3 · M3.3 |
| OBJ-06 | FR-083 | Uncertain targets | P3 | Committed | adapters/desktop, ui | TC-073 | Phase 3 · M3.3 |
| OBJ-04 | FR-084 | Local VLM interpretation | P3 | Unvalidated (EV-05) | local-ai | TC-074 | Phase 3 · M3.4 |
| OBJ-07 | FR-085 | Postcondition evaluation | MVP | Committed | verification-engine | TC-075 | Phase 1 · M1.2 |
| OBJ-07 | FR-086 | Outcome classification | MVP | Committed | verification-engine | TC-076 | Phase 1 · M1.2 |
| OBJ-07 | FR-087 | No unverified success claims | MVP | Committed | verification-engine, ui | TC-076 | Phase 1 · M1.2 |
| OBJ-07 | FR-088 | Failure diagnostics | MVP | Committed | execution-engine, storage | TC-077 | Phase 1 · M1.3 |
| OBJ-07 | FR-089 | Controlled retries | MVP | Committed | verification-engine, execution-engine | TC-078 | Phase 1 · M1.3 |
| OBJ-07 | FR-090 | Rollback of reversible operations | MVP | Committed | verification-engine, adapters/files, adapters/spreadsheet | TC-079 | Phase 1 · M1.3 |
| OBJ-07 | FR-091 | Checkpoints and resume | MVP | Committed | execution-engine, storage | TC-080 | Phase 1 · M1.3 |
| OBJ-07 | FR-092 | Validate recovery-originated changes | MVP | Committed | workflow-engine, execution-engine | TC-081 | Phase 1 · M1.3 |
| OBJ-05 | FR-093 | Execution history | MVP | Committed | ui, storage | TC-082 | Phase 1 · M1.3 |
| OBJ-07 | FR-094 | Tamper-evident audit log | MVP | Committed | storage | TC-083 | Phase 1 · M1.1 |
| OBJ-10 | FR-095 | Log and report redaction | MVP | Committed | storage, execution-engine | TC-084 | Phase 1 · M1.1 |
| OBJ-06 | FR-096 | Progress display | MVP | Committed | ui, execution-engine | TC-085 | Phase 1 · M1.3 |
| OBJ-06 | FR-097 | Pause and resume | MVP | Committed | execution-engine, ui | TC-086 | Phase 1 · M1.3 |
| OBJ-06 | FR-098 | Emergency stop | MVP | Committed | execution-engine, ui | TC-087 | Phase 1 · M1.3 |
| OBJ-06 | FR-099 | Human approval for consequential operations | MVP | Committed | policy-engine, execution-engine, ui | TC-088 | Phase 1 · M1.3 |
| OBJ-06 | FR-100 | Automation indicator | MVP | Committed | ui | TC-089 | Phase 1 · M1.3 |
| OBJ-06 | FR-101 | Single active run | MVP | Committed | execution-engine | TC-090 | Phase 1 · M1.3 |
| OBJ-06 | FR-102 | Permission manifest | MVP | Committed | workflow-engine, policy-engine | TC-091 | Phase 1 · M1.1 |
| OBJ-06 | FR-103 | Grants bound to versions | MVP | Committed | policy-engine, ui, storage | TC-092 | Phase 1 · M1.3 |
| OBJ-06 | FR-104 | Closed operation catalog | MVP | Committed | workflow-engine, policy-engine | TC-027, TC-111 | Phase 1 · M1.1 |
| OBJ-06 | FR-105 | Scope enforcement with canonicalization | MVP | Committed | policy-engine, adapters/files | TC-055 | Phase 1 · M1.1 |
| OBJ-06 | FR-106 | Untrusted content separation and taint | MVP | Committed | workflow-engine, policy-engine, local-ai | TC-040 | Phase 1 · M1.1 |
| OBJ-06 | FR-107 | Revoke permissions | MVP | Committed | policy-engine, ui | TC-093 | Phase 1 · M1.3 |
| OBJ-01 | FR-108 | Local model registry | MVP | Committed | local-ai | TC-094 | Phase 1 · M1.5 |
| OBJ-08 | FR-109 | Capability levels | MVP | Committed | local-ai, ui | TC-095 | Phase 1 · M1.5 |
| OBJ-04 | FR-110 | Constrained structured outputs | MVP | Committed | local-ai | TC-038 | Phase 1 · M1.5 |
| OBJ-01 | FR-111 | Behaviour when AI is unavailable | MVP | Committed | local-ai, execution-engine | TC-036 | Phase 1 · M1.5 |
| OBJ-08 | FR-112 | Model lifecycle | MVP | Committed | local-ai | TC-096 | Phase 1 · M1.5 |
| OBJ-08 | FR-113 | Resource guard | MVP | Committed | local-ai | TC-097 | Phase 1 · M1.5 |
| OBJ-01 | FR-114 | Network-independent core | MVP | Committed | system | TC-098 | Phase 1 · M1.6 |
| OBJ-01 | FR-115 | No mandatory online account or licence check | MVP | Committed | ui, installer | TC-099 | Phase 1 · M1.6 |
| OBJ-01 | FR-116 | External dependency labelling | MVP | Committed | workflow-engine, ui | TC-100 | Phase 1 · M1.3 |
| OBJ-01 | FR-117 | Network transparency | MVP | Committed | system | TC-101 | Phase 1 · M1.6 |
| OBJ-01 | FR-118 | Offline installation | MVP / P4 | Committed | installer | TC-102 | Phase 1 · M1.6, M4.4 |
| OBJ-09 | FR-119 | Backup and restore | MVP / P4 | Committed | storage, ui | TC-103 | Phase 1 · M1.6, M4.3 |
| OBJ-10 | FR-120 | Evidence retention | MVP | Committed | storage, ui | TC-104 | Phase 1 · M1.6 |

## 4. Traceability Matrix — Non-Functional Requirements

| Objective | Requirement | Title | Release | Validation | Components | Test cases | Phase · Milestone |
|---|---|---|---|---|---|---|---|
| OBJ-03 | NFR-001 | Deterministic replay success | MVP | Target | execution-engine, verification-engine | TC-105 | Phase 1 · M1.6 |
| OBJ-07 | NFR-002 | Source file integrity under faults | MVP | Target | adapters/*, verification-engine | TC-106 | Phase 1 · M1.6 |
| OBJ-07 | NFR-003 | Critical mismatch detection | MVP | Target | verification-engine | TC-075, TC-107 | Phase 1 · M1.6 |
| OBJ-07 | NFR-004 | Crash consistency | MVP | Committed | execution-engine, storage | TC-080 | Phase 1 · M1.3 |
| OBJ-03 | NFR-005 | Plan reproducibility | MVP | Committed | workflow-engine | TC-034 | Phase 1 · M1.1 |
| OBJ-01 | NFR-006 | Offline core features | MVP | Target | system | TC-098 | Phase 1 · M1.6 |
| OBJ-01 | NFR-007 | No unexpected outbound traffic | MVP | Committed | system | TC-101 | Phase 1 · M1.6 |
| OBJ-08 | NFR-008 | Usable on 8 GB reference machines | MVP | Target | system | TC-108 | Phase 1 · M1.0, M1.6 |
| OBJ-08 | NFR-009 | No inference during deterministic operation | MVP | Committed | execution-engine, local-ai | TC-036 | Phase 1 · M1.3 |
| OBJ-08 | NFR-010 | Idle model unload | MVP | Committed | local-ai | TC-096 | Phase 1 · M1.5 |
| OBJ-06 | NFR-011 | Responsive controls | MVP | Committed | ui, execution-engine | TC-087 | Phase 1 · M1.3 |
| OBJ-06 | NFR-012 | Emergency stop latency | MVP | Target | execution-engine, ui | TC-087 | Phase 1 · M1.3 |
| OBJ-12 | NFR-013 | Evidence-based performance statements | All releases | Committed | documentation, process | TC-109 | Phase 1 · M1.0 |
| OBJ-06 | NFR-014 | Least privilege for the UI process | MVP | Committed | ui | TC-110 | Phase 1 · M1.3 |
| OBJ-06 | NFR-015 | No arbitrary code execution path | MVP | Committed | system | TC-111 | Phase 1 · M1.6 |
| OBJ-10 | NFR-016 | Secret handling | MVP | Committed | platform, storage | TC-084, TC-065 | Phase 1 · M1.3 |
| OBJ-10 | NFR-017 | Protection of sensitive data at rest | MVP | Committed | storage | TC-112 | Phase 1 · M1.1 |
| OBJ-12 | NFR-018 | Supply-chain integrity | MVP | Committed | ci, local-ai | TC-113 | Phase 1 · M1.0 |
| OBJ-06 | NFR-019 | Signed releases | P4 | Committed | installer, ci | TC-114 | Phase 4 · M4.3 |
| OBJ-06 | NFR-020 | Prompt-injection resilience | MVP | Target | policy-engine, local-ai | TC-040 | Phase 1 · M1.5 |
| OBJ-10 | NFR-021 | No telemetry by default | MVP | Committed | system | TC-101 | Phase 1 · M1.6 |
| OBJ-10 | NFR-022 | Recording minimization | MVP | Committed | observation | TC-017 | Phase 1 · M1.4 |
| OBJ-10 | NFR-023 | User-controlled deletion | MVP | Committed | storage, ui | TC-104 | Phase 1 · M1.6 |
| OBJ-05 | NFR-024 | Workflow transparency | MVP | Target | ui | TC-010 | Phase 1 · M1.3 |
| OBJ-05 | NFR-025 | Understandable mode recommendations | MVP | Unvalidated (EV-07) | ui, workflow-engine | TC-115 | Phase 1 · M1.6 |
| OBJ-02 | NFR-026 | Accessible user interface | MVP | Committed | ui | TC-116 | Phase 1 · M1.6 |
| OBJ-05 | NFR-027 | Actionable errors | MVP | Committed | ui | TC-117 | Phase 1 · M1.6 |
| OBJ-12 | NFR-028 | Platform support | MVP | Target | system | TC-118 | Phase 1 · M1.6 |
| OBJ-09 | NFR-029 | Workflow format compatibility | MVP | Committed | workflow-engine | TC-119 | Phase 1 · M1.1 |
| OBJ-12 | NFR-030 | Enforced layer boundaries | MVP | Committed | ci | TC-120 | Phase 1 · M1.0 |
| OBJ-12 | NFR-031 | Testability of operations | MVP | Committed | all crates | TC-121 | Phase 1 · M1.2 |
| OBJ-12 | NFR-032 | Local diagnostic logging | MVP | Committed | all crates | TC-122 | Phase 1 · M1.1 |
| OBJ-12 | NFR-033 | Living documentation | All releases | Committed | documentation, ci | TC-123 | Phase 1 · M1.0 |
| OBJ-13 | NFR-034 | Productivity | P2 evaluation | Unvalidated (EV-08) | system | TC-124 | Phase 2 · M2.4 |
| OBJ-02 | NFR-035 | AI workflow construction success | MVP evaluation | Unvalidated (EV-02) | local-ai | TC-025 | Phase 1 · M1.5 |
| OBJ-01 | NFR-036 | Offline installability | MVP (basic); P4 (full) | Committed | installer | TC-102 | Phase 1 · M1.6 |

## 5. Test Case Catalogue

Test cases are grouped under `tests/` by level once code exists (see [tests/README.md](../../tests/README.md)). The *Implemented in* column lists the test code; an empty cell means the test is not implemented yet.

| Test case | Description | Level | Verifies | Implemented in |
|---|---|---|---|---|
| TC-001 | Create workflow requires name and objective; appears as Draft | U, E2E | FR-001 |  |
| TC-002 | Every stored version exports to JSON that validates against its schema version | U | FR-002 |  |
| TC-003 | Saving creates a new version; earlier content hash unchanged; runs reference exact hash | U, I | FR-003 |  |
| TC-004 | Library lists required columns; search by name and description | E2E | FR-004 |  |
| TC-005 | Duplicate is a new Draft with no grants | I | FR-005 |  |
| TC-006 | Archived workflow cannot start; history retained; restore works | I | FR-006 |  |
| TC-007 | Export contains no secrets, absolute paths, grants, or evidence | I | FR-007 |  |
| TC-008 | Import validates schema; invalid file rejected with first failing field; valid import is Draft without grants | U, I | FR-008 |  |
| TC-009 | Version history shows origin; revert creates a Draft equal to the selected version | I | FR-009 |  |
| TC-010 | Inspection view shows 100% of steps, parameters, permissions, and external services | E2E | FR-010, NFR-024 |  |
| TC-011 | Only Approved versions run; material changes and mode changes create Drafts | U, I | FR-011, FR-040 |  |
| TC-012 | Editor blocks schema-invalid definitions with inline errors | U, E2E | FR-012 |  |
| TC-013 | MVP template creates a working workflow with no model installed | E2E | FR-013 |  |
| TC-014 | System-detected limitations shown in inspection view | I | FR-014 |  |
| TC-015 | No event captured before consent confirmation | I | FR-015 |  |
| TC-016 | Recording indicator visible throughout; paused events not captured | E2E | FR-016 |  |
| TC-017 | Events outside selected folders/apps are not captured | I | FR-017, NFR-022 |  |
| TC-018 | Typed password characters never appear in stored recordings | I | FR-018 |  |
| TC-019 | Redacted events absent from analysis input and storage | I | FR-019 |  |
| TC-020 | File move/rename in scope captured in order with metadata | I | FR-020 |  |
| TC-021 | Field annotation stores name, type, sample value, page, and position | I | FR-021 |  |
| TC-022 | Spreadsheet mapping and key columns stored in draft | I | FR-022 |  |
| TC-023 | Ambiguous elements are asked about or flagged, never silently assumed | EV (EV-02) | FR-023 |  |
| TC-024 | Recording deletion removes rows and files; retention cleanup applies | I | FR-027 |  |
| TC-025 | AI workflow construction and variable detection on the EV-02 task set | EV (EV-02) | FR-028, FR-029, NFR-035 |  |
| TC-026 | AI-originated draft elements carry an inferred marker and rationale | I | FR-030 |  |
| TC-027 | Compiler rejects unknown operations (e.g. shell) and is deterministic | U | FR-031, FR-104 |  |
| TC-028 | With no model, demonstration produces an editable literal draft | I | FR-032 |  |
| TC-029 | Validation fails without workflow success conditions | U | FR-033 |  |
| TC-030 | Preview produces change list and leaves files and spreadsheets byte-identical | I, E2E | FR-034 |  |
| TC-031 | Mode recommendation rules and explanations over factor fixtures | U | FR-035, FR-036, FR-039 |  |
| TC-032 | Override allowed; incompatible mode blocks validation with explanation | U, I | FR-037, FR-038 |  |
| TC-033 | Recommendation, factors, and selected mode stored in history | I | FR-041 |  |
| TC-034 | Exact Replay operations match plan; plan hash stable across previews | U, I | FR-042, NFR-005 |  |
| TC-035 | Variables, for_each, and if branches behave correctly at boundaries | U | FR-043 |  |
| TC-036 | Model-free runs complete without starting the inference runtime | I, S | FR-044, FR-111, NFR-009 |  |
| TC-037 | Error rules stop, skip, route to review, or retry as declared | I | FR-045 |  |
| TC-038 | Schema-invalid model output is rejected and never passed downstream | U, I | FR-046, FR-110 |  |
| TC-039 | Decision outputs outside declared options are rejected | U | FR-047 |  |
| TC-040 | Prompt-injection corpus: zero operations outside the approved workflow | I, S | FR-048, FR-106, NFR-020 |  |
| TC-041 | Inconsistent, low-confidence, or precondition-failing decisions escalate | U, I | FR-049 |  |
| TC-042 | Adaptive budgets stop runs with budget_exhausted | I | FR-050 |  |
| TC-043 | Without a model, decision points are presented to the user and recorded as user-made | I | FR-051 |  |
| TC-044 | Input folder with mixed files creates items for supported types only | I | FR-054 |  |
| TC-045 | Text-layer extraction matches fixture text | I | FR-055 |  |
| TC-046 | OCR runs offline; low confidence flagged | I | FR-056 |  |
| TC-047 | Rule-based extraction equals expected values on fixtures | U, I | FR-057 |  |
| TC-048 | Model-assisted extraction accuracy reported per field | EV (EV-02) | FR-058 |  |
| TC-049 | Every extracted value has complete provenance | I | FR-059 |  |
| TC-050 | Each validation rule type has passing and failing fixtures | U | FR-060 |  |
| TC-051 | Invalid items routed to review without spreadsheet change; correction and resubmission work | I, E2E | FR-061 |  |
| TC-052 | Upsert produces expected rows in XLSX and CSV | I | FR-062 |  |
| TC-053 | Lock detection, structure check, atomic write under kill, formula neutralization | I | FR-063 |  |
| TC-054 | Collision policy suffix/fail; existing files never overwritten | I | FR-064 |  |
| TC-055 | Traversal, link, junction, reserved-name, and prefix cases stay in scope (per OS) | U, I | FR-065, FR-105 |  |
| TC-056 | Report outcomes equal run record; sensitive fields masked | I | FR-066 |  |
| TC-057 | Re-running on same inputs adds no rows | I, E2E | FR-067 |  |
| TC-058 | Browser steps never use the everyday profile | I | FR-068 |  |
| TC-059 | Basic navigate/click/fill/download against local fixture site | I | FR-069 |  |
| TC-060 | Semantic locators survive CSS class changes | I | FR-070 |  |
| TC-061 | Dropdowns, tables, dynamic content, uploads on fixture site | I | FR-071 |  |
| TC-062 | Page table extraction equals expected records | I | FR-072 |  |
| TC-063 | Submission without confirmation is never completed | I | FR-073 |  |
| TC-064 | Navigation to non-allowlisted host denied | I | FR-074 |  |
| TC-065 | No credential value found in any stored data after credentialed run | S | FR-075, NFR-016 |  |
| TC-066 | Challenge page pauses the run | I | FR-076 |  |
| TC-067 | MVP catalog contains no input-simulation operation | R | FR-077 |  |
| TC-068 | UIA adapter operates test application controls | I | FR-078 |  |
| TC-069 | AX adapter reports missing permission and performs no action | I | FR-079 |  |
| TC-070 | Unregistered application labelled untested | I | FR-080 |  |
| TC-071 | No OCR/VLM call when structural inspection finds the target | I | FR-081 |  |
| TC-072 | Missing expected effect blocks dependent actions | I | FR-082 |  |
| TC-073 | Ambiguous consequential target prompts the user | I | FR-083 |  |
| TC-074 | VLM features disabled below Enhanced level | I | FR-084 |  |
| TC-075 | Adapter falsely reporting success is detected by re-observation | I | FR-085, NFR-003 |  |
| TC-076 | Outcome classification table tests; no unverified completed | U | FR-086, FR-087 |  |
| TC-077 | Injected failures produce complete diagnostic records | I | FR-088 |  |
| TC-078 | Retries only for idempotent/transient; consequential never auto-retried | U, I | FR-089 |  |
| TC-079 | Rollback restores files and spreadsheet, verified by hash | I | FR-090 |  |
| TC-080 | Kill at each step boundary; resume without duplicates | S | FR-091, NFR-004 |  |
| TC-081 | Recovery-originated changes create Draft versions | I | FR-092 |  |
| TC-082 | Every run reachable in history with complete step records | E2E | FR-093 |  |
| TC-083 | Modified audit entry detected at first broken link | U | FR-094 |  |
| TC-084 | Seeded secrets and sensitive values absent or masked in logs and reports | S | FR-095, NFR-016 |  |
| TC-085 | Progress events at every step boundary | I | FR-096 |  |
| TC-086 | No step starts while paused | I | FR-097 |  |
| TC-087 | No dispatch after stop acknowledgement; stop works during inference; latency distribution | S | FR-098, NFR-011, NFR-012 |  |
| TC-088 | Approval bound to op hash; tampered parameters invalidate; unapproved never runs | U, I | FR-099 |  |
| TC-089 | Run indicator visible including when minimized | E2E | FR-100 |  |
| TC-090 | Second run request does not start concurrent execution | I | FR-101 |  |
| TC-091 | Manifest derived from steps; undeclared access fails compilation | U | FR-102 |  |
| TC-092 | Manifest change requires new grant; identical manifest reuses grant | I | FR-103 |  |
| TC-093 | Revoking during a run stops it with permission_revoked | I | FR-107 |  |
| TC-094 | Model with mismatched hash refused; adding a model needs no network | I | FR-108 |  |
| TC-095 | Capability level gating with and without models | I | FR-109 |  |
| TC-096 | Model memory released after idle timeout | S | FR-112, NFR-010 |  |
| TC-097 | Model load refused when available memory is insufficient | I | FR-113 |  |
| TC-098 | Offline acceptance suite on network-disabled VM | S | FR-114, NFR-006 |  |
| TC-099 | First launch on never-online machine; no sign-in or licence check | S | FR-115 |  |
| TC-100 | External-service label names the host | E2E | FR-116 |  |
| TC-101 | Network capture: no unexpected outbound connections | S | FR-117, NFR-007, NFR-021 |  |
| TC-102 | Offline installation on clean VM, then MVP workflow runs | S | FR-118, NFR-036 |  |
| TC-103 | Backup and restore reproduce library and version hashes; grants not restored | I | FR-119 |  |
| TC-104 | Retention cleanup and deletion remove rows and files; deletion logged without content | I | FR-120, NFR-023 |  |
| TC-105 | Reference suite repeated ≥100 times per machine; report success rate | S | NFR-001 |  |
| TC-106 | Fault-injection suite: zero undetected loss or corruption | S | NFR-002 |  |
| TC-107 | Mismatch-injection suite: 100% detected | S | NFR-003 |  |
| TC-108 | Resource baseline and regression on reference machines | S, EV (EV-01) | NFR-008 |  |
| TC-109 | PR checklist: published figures cite reproducible benchmarks | R | NFR-013 |  |
| TC-110 | Non-allowlisted IPC command refused | I | NFR-014 |  |
| TC-111 | Review + injection attempts through every input surface: no execution path | R, I | FR-104, NFR-015 |  |
| TC-112 | No plaintext sensitive values in database pages or evidence files | I | NFR-017 |  |
| TC-113 | CI runs dependency audit and licence checks; tampered sidecar refused | I, R | NFR-018 |  |
| TC-114 | Installer and update signatures verify | R | NFR-019 |  |
| TC-115 | Usability study: participants explain selected mode correctly | UX (EV-07) | NFR-025 |  |
| TC-116 | Automated and manual WCAG 2.2 AA checks | R, UX | NFR-026 |  |
| TC-117 | Every EXC message states what happened, impact, next step | R | NFR-027 |  |
| TC-118 | MVP acceptance suite on both reference machines | S | NFR-028 |  |
| TC-119 | Schema migration fixtures; unsupported versions rejected | U | NFR-029 |  |
| TC-120 | Forbidden crate dependencies fail CI | I | NFR-030 | [`scripts/tests/test_check_crate_deps.py`](../../scripts/tests/test_check_crate_deps.py), [`scripts/check_crate_deps.py`](../../scripts/check_crate_deps.py) |
| TC-121 | Operation-to-test coverage report | R | NFR-031 |  |
| TC-122 | Structured logs with correlation IDs; no secrets | I | NFR-032 |  |
| TC-123 | Documentation checks (IDs, links, Mermaid, schema examples) in CI | I | NFR-033 | [`scripts/check_docs.py`](../../scripts/check_docs.py), [`scripts/validate_schemas.py`](../../scripts/validate_schemas.py), [`scripts/validate_mermaid.py`](../../scripts/validate_mermaid.py) |
| TC-124 | Productivity study versus manual processing | EV (EV-08) | NFR-034 |  |
| TC-125 | Recorded browser form task replays using semantic descriptors | I | FR-024 |  |
| TC-126 | Keystrokes in unselected applications not captured | I | FR-025 |  |
| TC-127 | Screenshots contain only selected application windows | I | FR-026 |  |
| TC-128 | Adaptive browser loop: non-allowlisted navigation denied; budgets enforced | I | FR-052 |  |
| TC-129 | Recovery proposals outside declared options rejected | U, I | FR-053 |  |

## 6. Coverage Summary

| Type | MVP (incl. conditional) | P2 | P3 | P4 | Total |
|---|---|---|---|---|---|
| FR | 103 | 9 | 8 | 0 | 120 |
| NFR | 32 | 0 | 0 | 1 | 36 (+3 other) |

| Objective | Requirements traced |
|---|---|
| OBJ-01 | 13 |
| OBJ-02 | 11 |
| OBJ-03 | 12 |
| OBJ-04 | 9 |
| OBJ-05 | 12 |
| OBJ-06 | 29 |
| OBJ-07 | 21 |
| OBJ-08 | 7 |
| OBJ-09 | 10 |
| OBJ-10 | 13 |
| OBJ-11 | 11 |
| OBJ-12 | 7 |
| OBJ-13 | 1 |

**Unvalidated requirements** (17): FR-023, FR-025, FR-028, FR-029, FR-046, FR-047, FR-052, FR-053, FR-058, FR-068, FR-069, FR-078, FR-079, FR-084, NFR-025, NFR-034, NFR-035. These depend on the evaluations in [SRS §18.5](SRS.md#185-planned-evaluations-and-spikes) and are not commitments until those pass.

## 7. Maintenance Rules

1. A new requirement must be added to this matrix in the same pull request.
2. A withdrawn requirement stays in the matrix with *Withdrawn* in the Release column.
3. When a test is implemented, add its path in the *Implemented in* column of §5.
4. `python3 scripts/check_docs.py` must pass before merging.
