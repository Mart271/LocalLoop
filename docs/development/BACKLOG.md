# LocalLoop — Initial Backlog

| Field | Value |
|---|---|
| Version | 0.1 (draft) |
| Date | 2026-10-09 |
| Related | [Roadmap](ROADMAP.md) · [Traceability](../requirements/requirements-traceability.md) |

Each row is sized to be one GitHub issue (roughly 0.5–5 days of focused work). The repository has an `origin` remote; this backlog does not imply that an issue exists for every row. Current evidence and status are in [PROGRESS.md](PROGRESS.md).

**Active gate (2026-10-10):** Windows first; macOS validation is deferred under [ADR-0010](../adr/0010-windows-first-validation.md). EV-01 / LL-006 moves to M1.5, and EV-09 / LL-009 to Phase 2. Where a row originally requires both platforms or reference machines, Windows milestone completion records the remaining checks as deferred; it does not verify the original cross-platform release targets.

**Sizes:** S ≈ ≤1 day · M ≈ 2–3 days · L ≈ 4–5 days (split further if it grows).
**Labels:** `type/feature`, `type/spike`, `type/test`, `type/chore`, `type/docs`, `type/security`; `area/<module>`; `phase/1`…`phase/4`; priority comes from the linked requirements.

Every issue's *definition of done* also includes: tests for the behaviour, docs updated if behaviour or interfaces changed, and `python3 scripts/check_docs.py` passing.

---

## Phase 1 — Core Automation Foundation (MVP)

### M1.0 Foundation and spikes

| ID | Title | Labels | Size | Depends on | Requirements | Done when |
|---|---|---|---|---|---|---|
| LL-001 | Create Cargo workspace with crate skeletons matching the architecture | type/chore, area/infra | S | — | NFR-030 | Workspace builds; each crate has a README and an empty public API |
| LL-002 | Scaffold Tauri 2 + React + TypeScript app in `apps/desktop` with strict CSP and minimal capabilities | type/chore, area/ui | M | LL-001 | NFR-014 | App launches on Windows and macOS; CSP `default-src 'self'`; only a ping command allowed |
| LL-003 | CI: Rust fmt, clippy, tests; TS lint, typecheck, tests; dependency audit and licence checks | type/chore, area/ci | M | LL-001, LL-002 | NFR-018 | CI green on both OS runners; audit failures block merges |
| LL-004 | Forbidden crate dependency check in CI | type/security, area/ci | S | LL-001 | NFR-030 | A test PR adding `local-ai → adapters` fails CI |
| LL-005 | Generate TypeScript DTO types from Rust into `packages/shared` | type/chore, area/ui | S | LL-002 | NFR-014 | Types regenerate in CI; drift fails the build |
| LL-006 | Spike EV-01: inference runtime and model shortlist benchmark | type/spike, area/local-ai | L | LL-013 | FR-112, FR-113, NFR-008 | Report: memory, load time, throughput, JSON validity rate for 2–3 models on both machines; ADR-0003 updated |
| LL-007 | Spike EV-06: OCR engine comparison | type/spike, area/documents | M | LL-012 | FR-056, D-04 | Report with accuracy on F1/F2, size, licence, platform support; ADR written |
| LL-008 | Spike EV-04: XLSX round-trip fidelity | type/spike, area/spreadsheet | M | LL-012 | FR-062, FR-063, A-05 | Report on formatting/formula preservation and lock behaviour; unsupported-workbook policy ADR |
| LL-009 | Spike EV-09: browser bridge offline packaging | type/spike, area/browser | M | LL-002 | FR-068, FR-069, D-02 | Bridge launches offline on both OSes; installer size delta; D-02 decision recorded |
| LL-010 | Spike D-07: encryption at rest build on both OSes | type/spike, type/security, area/storage | M | LL-001 | NFR-017, D-07 | ADR choosing SQLCipher or application-level encryption |
| LL-011 | Spike: child-process packaging and lifecycle (job objects, process groups, checksums) | type/spike, area/infra | M | LL-002 | NFR-018 | Worker and sidecar start, stop, and die with the app on both OSes |
| LL-012 | Synthetic fixture generator for sets F1–F6 | type/test, area/test | M | — | A-19 | Fixtures generated reproducibly from a seed; no real company data |
| LL-013 | Reference-machine baseline and benchmark harness | type/test, area/perf | M | LL-002 | NFR-008, NFR-013 | Baseline report with hardware, OS, and versions recorded |

### M1.1 Core domain

| ID | Title | Labels | Size | Depends on | Requirements | Done when |
|---|---|---|---|---|---|---|
| LL-014 | Finalize workflow schema 0.1 and Rust domain model with serde round-trip tests | type/feature, area/workflow-engine | M | LL-001 | FR-002, NFR-029 | All examples round-trip; schema and model agree |
| LL-015 | Canonical JSON and content hashing for versions and operations | type/feature, area/workflow-engine | S | LL-014 | FR-003, FR-099 | Hash stable across key order and whitespace |
| LL-016 | Compiler: catalog check, type check, manifest derivation, located errors | type/feature, area/workflow-engine | L | LL-014 | FR-031, FR-033, FR-102, FR-104 | Rejects unknown ops and undeclared access with JSON Pointer locations |
| LL-017 | Conditions and template engine with fixed operators and filters; regex limits | type/feature, area/workflow-engine | M | LL-014 | FR-043 | Boundary tests pass; pathological regex rejected |
| LL-018 | Path segment sanitizer for Windows and macOS rules | type/security, area/workflow-engine | S | — | FR-065 | Traversal, reserved-name, and control-character fixtures pass |
| LL-019 | Planner, item plans, and plan hash | type/feature, area/workflow-engine | M | LL-016, LL-017 | NFR-005 | Repeated planning yields identical hashes |
| LL-020 | Lifecycle state machine for workflow versions | type/feature, area/workflow-engine | S | LL-014 | FR-011, FR-040 | Material changes produce Drafts; tests for every transition |
| LL-021 | Policy engine pipeline and sealed `AuthorizedOperation` | type/security, area/policy-engine | L | LL-016 | FR-104, FR-106, FR-048 | Adapters cannot construct authorizations (compile-fail test) |
| LL-022 | Path canonicalization and handle verification per OS | type/security, area/policy-engine | M | LL-021 | FR-105 | Link/junction/prefix suite passes on both OSes |
| LL-023 | Taint wrapper and parameter-position rules | type/security, area/policy-engine | M | LL-021 | FR-106 | Tainted host or location values are denied |
| LL-024 | Storage: SQLite, migrations with pre-migration backup, repositories | type/feature, area/storage | M | LL-010 | FR-003 | Migrations apply and roll forward on fixtures |
| LL-025 | Journal and immutable-row triggers | type/feature, area/storage | S | LL-024 | NFR-004 | Updates to immutable rows raise errors |
| LL-026 | Audit hash chain and verification | type/security, area/storage | S | LL-024 | FR-094 | Tampered entry detected at the right sequence number |
| LL-027 | Encryption at rest per D-07 | type/security, area/storage | M | LL-010, LL-024 | NFR-017 | No plaintext sensitive fixture values in DB or evidence files |
| LL-028 | Structured logging with redaction layer | type/security, area/infra | S | LL-001 | FR-095, NFR-032 | Seeded secrets never appear in logs |

### M1.2 Adapters and verification

| ID | Title | Labels | Size | Depends on | Requirements | Done when |
|---|---|---|---|---|---|---|
| LL-029 | Files adapter: list, copy, move, rename with collision policy and undo | type/feature, area/adapters | M | LL-021, LL-022 | FR-054, FR-064, FR-090 | Never overwrites; undo verified by hash |
| LL-030 | Document worker: framing protocol, limits, supervisor | type/feature, area/documents | M | LL-011 | FR-055 | Oversized or hung inputs are killed and reported |
| LL-031 | Document worker: PDF text layer extraction and page rendering | type/feature, area/documents | M | LL-030 | FR-055 | F1 text matches expectations |
| LL-032 | Document worker: OCR per D-04 | type/feature, area/documents | M | LL-007, LL-030 | FR-056 | Runs offline; confidence reported; F2 results recorded |
| LL-033 | Rule-based field extraction with typed parsing | type/feature, area/workflow-engine | M | LL-031 | FR-057 | F1 extraction exact |
| LL-034 | Provenance model and evidence storage | type/feature, area/storage | S | LL-027, LL-033 | FR-059 | Every value links to source, page, method |
| LL-035 | Validation rules engine | type/feature, area/workflow-engine | M | LL-017 | FR-060 | Pass/fail fixture for each rule type |
| LL-036 | Spreadsheet adapter: read and upsert for XLSX and CSV | type/feature, area/spreadsheet | M | LL-008, LL-021 | FR-062 | Expected rows produced on F6 |
| LL-037 | Spreadsheet write safety: lock, structure, backup, atomic replace, re-read, formula neutralization | type/security, area/spreadsheet | M | LL-036 | FR-063 | Kill-during-write test leaves original or complete file |
| LL-038 | Verification engine: observers and MVP postconditions | type/feature, area/verification-engine | M | LL-029, LL-036 | FR-085 | False-success adapter detected |
| LL-039 | Outcome classifier and termination reasons | type/feature, area/verification-engine | S | LL-038 | FR-086, FR-087 | Table-driven tests for every outcome |
| LL-040 | Operation test-coverage report in CI | type/test, area/ci | S | LL-038 | NFR-031 | CI lists each catalog operation with its tests |

### M1.3 Model-free end-to-end

| ID | Title | Labels | Size | Depends on | Requirements | Done when |
|---|---|---|---|---|---|---|
| LL-041 | Run orchestrator state machine and single-run guard | type/feature, area/execution-engine | L | LL-019, LL-021, LL-038 | FR-042, FR-101 | Operation sequence equals plan in tests |
| LL-042 | Control channel: pause, resume, stop, cancellation tokens | type/feature, area/execution-engine | M | LL-041 | FR-097, FR-098, NFR-012 | No dispatch after stop acknowledgement in randomized tests |
| LL-043 | Error rules and bounded retries | type/feature, area/execution-engine | S | LL-041 | FR-045, FR-089 | Consequential operations never retried automatically |
| LL-044 | Rollback executor | type/feature, area/verification-engine | M | LL-029, LL-037 | FR-090 | Run rollback restores fixtures by hash |
| LL-045 | Crash recovery from journal on startup | type/feature, area/execution-engine | M | LL-025, LL-041 | FR-091, NFR-004 | Kill at every boundary; resume without duplicates |
| LL-046 | Approval service with plan approval and hash-bound single-use tokens | type/security, area/execution-engine | M | LL-015, LL-021 | FR-099 | Tampered parameters invalidate approval |
| LL-047 | Review queue backend and resubmission | type/feature, area/execution-engine | M | LL-041 | FR-061 | Invalid items never reach the spreadsheet |
| LL-048 | Duplicate protection by content hash and key columns | type/feature, area/execution-engine | S | LL-036 | FR-067 | Re-run adds no rows |
| LL-049 | Report writer: HTML, JSON, CSV with masking and escaping | type/feature, area/execution-engine | M | LL-039 | FR-066 | Report equals run record; HTML escaping tests |
| LL-050 | Mode recommender rules and explanation templates | type/feature, area/workflow-engine | M | LL-019 | FR-035 to FR-039 | Factor-fixture table tests |
| LL-051 | Grants, location bindings, revocation (backend) | type/security, area/policy-engine | M | LL-021, LL-024 | FR-103, FR-107 | Manifest change requires re-grant |
| LL-052 | IPC command surface with typed DTO validation | type/security, area/ui | M | LL-005 | NFR-014 | Non-allowlisted commands refused |
| LL-053 | UI: library, search, duplicate, archive, history, revert | type/feature, area/ui | M | LL-052 | FR-004 to FR-006, FR-009 | E2E tests pass |
| LL-054 | UI: template creation and editor with inline compile errors | type/feature, area/ui | L | LL-016, LL-052 | FR-012, FR-013 | MVP template workflow created without a model |
| LL-055 | UI: inspector with permissions, external-service labels, limitations | type/feature, area/ui | M | LL-052 | FR-010, FR-014, FR-116 | Inspection shows 100% of steps and permissions |
| LL-056 | UI: mode recommendation panel and compatibility messages | type/feature, area/ui | S | LL-050 | FR-035 to FR-041 | Override and blocking flows work |
| LL-057 | UI: preview and validation screen | type/feature, area/ui | M | LL-019, LL-052 | FR-034 | Preview leaves fixtures byte-identical |
| LL-058 | UI: grant dialog with broad-scope warnings | type/security, area/ui | S | LL-051 | FR-103 | Warnings shown for drive or home roots |
| LL-059 | UI: run monitor, approvals, decisions, indicator | type/feature, area/ui | M | LL-042, LL-046 | FR-096, FR-099, FR-100 | Indicator visible when minimized |
| LL-060 | Shell: tray/menu-bar stop and global shortcut | type/security, area/ui | S | LL-042 | FR-098, NFR-011 | Stop works while UI is busy |
| LL-061 | UI: review queue | type/feature, area/ui | M | LL-047 | FR-061 | Correct, resubmit, reject flows |
| LL-062 | UI: run history and audit verification | type/feature, area/ui | M | LL-026 | FR-093, FR-094 | Every run reachable with step detail |
| LL-063 | Export and import | type/feature, area/workflow-engine | S | LL-016 | FR-007, FR-008 | Exports contain no secrets or bindings; imports are Drafts |
| LL-064 | Model-free end-to-end test of the reference scenario | type/test, area/test | M | LL-041 to LL-063 | FR-044, NFR-009 | Runs on both machines with no model installed |

### M1.4 Guided demonstration

| ID | Title | Labels | Size | Depends on | Requirements | Done when |
|---|---|---|---|---|---|---|
| LL-065 | Recorder session state machine and consent summary hash | type/feature, area/observation | M | LL-024 | FR-015 | No capture before consent |
| LL-066 | Recording indicator and controls | type/feature, area/ui | S | LL-065 | FR-016 | Paused events not captured |
| LL-067 | Scoped file-event capture (Windows and macOS) | type/feature, area/observation | M | LL-065 | FR-017, FR-020 | Out-of-scope events absent |
| LL-068 | Document annotation UI | type/feature, area/ui | M | LL-031 | FR-021 | Field positions stored |
| LL-069 | Spreadsheet mapping UI | type/feature, area/ui | S | LL-036 | FR-022 | Mapping stored in draft |
| LL-070 | Review and redaction UI | type/feature, area/ui | S | LL-065 | FR-019 | Redacted items absent downstream |
| LL-071 | Literal draft builder (no model) | type/feature, area/workflow-engine | M | LL-016, LL-067 | FR-032 | Demonstration becomes an editable draft |
| LL-072 | Recording retention and deletion | type/feature, area/storage | S | LL-065 | FR-027, NFR-023 | Deletion removes rows and files |

### M1.5 Local AI slice

| ID | Title | Labels | Size | Depends on | Requirements | Done when |
|---|---|---|---|---|---|---|
| LL-073 | Model registry and import from local file or package | type/feature, area/local-ai | M | LL-006 | FR-108 | Hash mismatch refused; no network needed |
| LL-074 | Resource guard and capability levels | type/feature, area/local-ai | S | LL-073 | FR-109, FR-113 | Low-memory refusal test |
| LL-075 | Inference sidecar supervisor: spawn, token, health, idle unload | type/feature, area/local-ai | M | LL-011, LL-073 | FR-112, NFR-010 | Memory released after idle timeout |
| LL-076 | Prompt template format and output validator | type/security, area/local-ai | M | LL-075 | FR-110, AIC-02 | Invalid outputs rejected |
| LL-077 | Field extractor (model-assisted) | type/feature, area/local-ai | M | LL-076 | FR-058, FR-046 | Schema-constrained outputs; F3 results recorded |
| LL-078 | Demonstration analyzer and variable detection with inferred markers | type/feature, area/local-ai | L | LL-071, LL-076 | FR-028 to FR-030 | Proposals compile; inferred markers shown |
| LL-079 | Ambiguity questions during analysis | type/feature, area/ui | S | LL-078 | FR-023 | Ambiguous elements asked or flagged |
| LL-080 | Decision points: provider, consistency check, thresholds, budgets, escalation | type/feature, area/execution-engine | L | LL-041, LL-076 | FR-047 to FR-050 | Escalation tests; budget stop |
| LL-081 | Manual decision fallback UI | type/feature, area/ui | S | LL-080 | FR-051 | Decisions recorded as user-made |
| LL-082 | Prompt-injection corpus and CI job | type/security, area/test | M | LL-012, LL-080 | NFR-020 | Zero policy bypasses; any bypass fails CI |
| LL-083 | EV-02 protocol and report (construction and extraction) | type/spike, area/local-ai | M | LL-077, LL-078 | NFR-035 | Report published with method, sample sizes, hardware |
| LL-084 | EV-03 protocol and report (decision accuracy and calibration) | type/spike, area/local-ai | M | LL-080 | FR-047, FR-049 | Report published |

### M1.6 Hardening and MVP release

| ID | Title | Labels | Size | Depends on | Requirements | Done when |
|---|---|---|---|---|---|---|
| LL-085 | Fault-injection and mismatch-injection suites | type/test, area/test | L | LL-064 | NFR-002, NFR-003 | Zero undetected faults; 100% mismatches detected |
| LL-086 | Reliability harness (≥100 runs per machine) | type/test, area/test | M | LL-064 | NFR-001 | Success rate reported with sample size |
| LL-087 | Offline acceptance suite on network-disabled VMs with network capture | type/test, area/test | M | LL-064 | FR-114, FR-117, NFR-006, NFR-007 | Suite green; no unexpected connections |
| LL-088 | Offline installers (Windows with WebView2 offline runtime; macOS DMG) | type/chore, area/infra | L | LL-011 | FR-115, FR-118, NFR-036 | Clean offline VM install and run |
| LL-089 | Backup and restore | type/feature, area/storage | M | LL-024 | FR-119 | Hashes match after restore; grants not restored |
| LL-090 | Retention settings and evidence purge | type/feature, area/storage | S | LL-034 | FR-120 | Purge removes rows and files |
| LL-091 | Accessibility pass (WCAG 2.2 AA) | type/test, area/ui | M | LL-053 to LL-062 | NFR-026 | Issues fixed or documented |
| LL-092 | Error-message review against the EXC catalogue | type/docs, area/ui | S | LL-064 | NFR-027 | Every EXC has an actionable message |
| LL-093 | Mode explanation usability check (EV-07) | type/test, area/ui | M | LL-056 | NFR-025 | Findings report; wording updated |
| LL-094 | User documentation and release notes with limitations | type/docs | M | LL-085 to LL-093 | MVP-AC-07 | Docs reviewed |
| LL-095 | MVP security review gate | type/security | M | LL-082, LL-085 | NFR-015 | Findings resolved or accepted with rationale |

---

## Phase 2 — Browser Automation and Workflow Intelligence

| ID | Title | Milestone | Size | Requirements |
|---|---|---|---|---|
| LL-101 | Browser bridge JSON-RPC protocol and offline packaging | M2.1 | L | FR-068 |
| LL-102 | Managed profile and basic operations (open, navigate, click, fill, download) | M2.1 | M | FR-069 |
| LL-103 | Host allowlist enforcement in core policy and bridge request interception | M2.1 | M | FR-074 |
| LL-104 | Challenge and session-expiry detection with pause | M2.1 | S | FR-076 |
| LL-105 | Browser recorder with semantic descriptors and protected-input exclusion | M2.2 | L | FR-024, FR-018 |
| LL-106 | Semantic targeting and advanced interactions | M2.2 | L | FR-070, FR-071 |
| LL-107 | Page extraction and submission verification | M2.2 | M | FR-072, FR-073 |
| LL-108 | Credential references via the OS credential store | M2.2 | M | FR-075, NFR-016 |
| LL-109 | Authorized-window screenshot capture | M2.2 | M | FR-026 |
| LL-110 | Adaptive browser loop with fixed vocabulary and snapshot-bound URLs | M2.3 | L | FR-052 |
| LL-111 | Evaluate non-GET request gating for adaptive steps | M2.3 | M | FR-052, T-11 |
| LL-112 | Recovery proposals from declared options | M2.3 | M | FR-053 |
| LL-113 | Web prompt-injection corpus | M2.3 | M | NFR-020 |
| LL-114 | EV-08 productivity study | M2.4 | L | NFR-034 |
| LL-115 | Competitive comparison and Phase 3 scoping | M2.4 | M | P§10 |

## Phase 3 — Desktop Vision and Application Support

| ID | Title | Milestone | Size | Requirements |
|---|---|---|---|---|
| LL-201 | Platform accessibility layer: Windows UI Automation | M3.1 | L | FR-078 |
| LL-202 | Platform accessibility layer: macOS AX with permission flows | M3.1 | L | FR-079 |
| LL-203 | Application support registry and capability tests | M3.1 | M | FR-080 |
| LL-204 | Scoped desktop recorder | M3.2 | L | FR-025 |
| LL-205 | Tiered inspection with screen OCR | M3.3 | L | FR-081 |
| LL-206 | Observe-act-verify with window identity checks | M3.3 | L | FR-082 |
| LL-207 | Uncertain-target handling | M3.3 | M | FR-083 |
| LL-208 | EV-05 VLM feasibility; integration only if it passes | M3.4 | L | FR-084 |

## Phase 4 — Reliability, Optimization, and Production Readiness

| ID | Title | Milestone | Size | Requirements |
|---|---|---|---|---|
| LL-301 | Memory and startup profiling; regression budgets in CI | M4.1 | M | NFR-008 |
| LL-302 | Template library for common document workflows | M4.2 | L | FR-013 |
| LL-303 | OS-level sandboxing of document worker and bridge | M4.3 | L | AR-05 |
| LL-304 | Code signing and notarization pipeline | M4.3 | M | NFR-019 |
| LL-305 | Signed offline update packages | M4.3 | M | NFR-019 |
| LL-306 | Encrypted backups and audit checkpoint export | M4.3 | M | FR-119, AR-07 |
| LL-307 | External security review | M4.3 | M | NFR-015 |
| LL-308 | Implement licence decision (D-03) | M4.4 | S | D-03 |
| LL-309 | Full offline installer with model packages; upgrade tests | M4.4 | L | FR-118, NFR-036 |
