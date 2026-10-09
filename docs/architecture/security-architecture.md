# LocalLoop — Security Architecture

| Field | Value |
|---|---|
| Version | 0.1 (draft) |
| Date | 2026-10-09 |
| Parent | [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md) |
| Requirements | [SRS §9](../requirements/SRS.md#9-security-authorization-and-permission-requirements), NFR-014 to NFR-023 |

> **Status:** Proposed design; no control is implemented yet. Residual risks are stated explicitly. This document makes no claim that LocalLoop is secure; it defines the controls that must be built and tested.

**Core rule:** *AI reasoning is never execution permission.* The local model can propose; only the compiler and policy engine, acting on the user's grants and approvals, can authorize (C-01).

---

## 1. Scope and Assumptions

**In scope:** malicious or misleading content in documents, file names, web pages, and screens; model errors and manipulation; malicious workflow files; buggy or compromised UI code; parser vulnerabilities; accidental user actions; supply-chain risks in dependencies, sidecars, and models; data exposure through logs, reports, exports, and recordings.

**Out of scope (stated limitations):** malware already running as the user or as an administrator (it can read user files and the OS credential store session, drive the UI, or modify LocalLoop's files); physical attacks on an unlocked machine; vulnerabilities in the OS, WebView, or browser engine themselves (mitigated only by keeping them updated); security of remote websites users automate.

## 2. Assets

| Asset | Why it matters |
|---|---|
| User files in granted locations | Integrity and confidentiality of business documents |
| Target spreadsheets | Business records; corruption is costly |
| Credentials (P2+) | Account takeover if leaked |
| Extracted values and evidence | Personal and business data of third parties |
| Workflow definitions and grants | Define what LocalLoop may do |
| Audit chain | Accountability for what happened |
| The user's attention and trust | Approval fatigue leads to unsafe approvals |

## 3. Trust Boundaries

The boundaries TB-0 to TB-7 are drawn in [SYSTEM_ARCHITECTURE.md §11](SYSTEM_ARCHITECTURE.md#11-security-and-trust-boundaries).

## 4. Threat Model (STRIDE)

| ID | STRIDE | Boundary | Threat | Controls | Requirements | Residual risk |
|---|---|---|---|---|---|---|
| T-01 | Spoofing | TB-5 → TB-3 | Document text poses as an instruction from the user or system ("ignore previous instructions…") | Data-only prompts; task-scoped prompts without operation vocabulary; taint; policy independent of model | FR-106, AIC-03, AIC-04, NFR-020 | Model may mis-extract or mis-decide; caught by validation, option sets, and review |
| T-02 | Spoofing | TB-0 | A web page or another app imitates a LocalLoop approval dialog | Approvals issued only from LocalLoop's trusted UI path; approval dialog shows run ID and op hash fingerprint; P3 input injector refuses to target LocalLoop's own windows | FR-099 | Local malware can still click real dialogs (out of scope) |
| T-03 | Tampering | Import | A shared workflow file requests broad access with a misleading name | Import as Draft; grants never imported; inspection shows full manifest; warnings for broad scopes (drive root, home folder) | FR-008, FR-010, FR-103 | User may still approve; warnings and clear wording reduce this |
| T-04 | Tampering | TB-3 | Model file replaced or backdoored | SHA-256 verification against registry before load; licence/source recorded | FR-108, NFR-018 | A user-added malicious model can only emit data, which policy constrains |
| T-05 | Tampering | TB-6 | Database or audit log edited | Hash chain verification; immutable-row triggers | FR-094 | A fully privileged local attacker can rewrite the whole chain (AR-07) |
| T-06 | Tampering | TB-2 → TB-6 | Symlink/junction swap between check and use (TOCTOU) | Canonicalize then verify the opened handle's final path | FR-105 | Narrow races on some file systems; tested per platform |
| T-07 | Tampering | TB-2 → TB-6 | Extracted value written as a spreadsheet formula (CSV/formula injection) | Neutralize leading `= + - @`, tab, CR; write as text | FR-063 | None known for supported formats |
| T-08 | Repudiation | All | Disagreement about what ran and who approved | Version hashes, plan hashes, approvals, decisions (model vs. user), audit chain | FR-093, FR-094 | Single-user device: identity is the OS account |
| T-09 | Info disclosure | TB-2 | Secrets or sensitive values in logs, reports, prompts | Secrets only in OS store; redaction at log boundary; masking; secrets never in prompts | FR-095, NFR-016 | Developer error; seeded-secret scans in CI |
| T-10 | Info disclosure | Recording | Recording captures passwords or other apps | Scope filter; protected-input exclusion; review and redact | FR-015 to FR-019 | Platforms that do not flag secure fields; stated in consent dialog |
| T-11 | Info disclosure | TB-4 → TB-7 | Injected content makes an adaptive browser step send data to an attacker URL | Host allowlist (core and bridge); model may only choose URLs present as links in the current snapshot or matching declared patterns; `external_send` approval | FR-074, FR-099, FR-052 | Allowlisted host with open redirects or user content; flagged in workflow review |
| T-12 | Info disclosure | TB-3 | Another local process calls the inference server | Loopback bind, random port, per-session token; or stdio | AIC-05 | Same-user malware (out of scope) |
| T-13 | Denial of service | TB-5 → TB-4 | Malformed document hangs or exhausts the parser | Worker limits (size, pages, time), kill and restart | EXC-23 | Item fails; run continues |
| T-14 | Denial of service | TB-3 | Adaptive loop never ends | Decision, action, and time budgets | FR-050 | None beyond user time |
| T-15 | Denial of service | Host | Model load exhausts memory on 8 GB machines | Resource guard; idle unload | FR-112, FR-113 | Other apps' memory use varies |
| T-16 | Elevation | TB-3 → TB-2 | Model output executes commands or code | Closed catalog; no exec path anywhere; compiler rejects unknown operations | FR-104, NFR-015 | None by design; verified by review and tests |
| T-17 | Elevation | TB-1 → TB-2 | Untrusted text rendered as HTML runs script in the WebView and calls IPC | React escaping, no raw HTML from untrusted sources, strict CSP, IPC allowlist, typed validation | NFR-014 | WebView engine bugs |
| T-18 | Elevation | TB-5 → TB-4 | Parser exploit in PDF/image/OCR code | Separate worker process, memory-safe code where possible, fuzzing | FR-056 | Worker runs as the user; OS sandboxing is P4 (AR-05) |
| T-19 | Elevation | TB-2 → TB-6 | Path traversal through extracted values | Single-segment sanitizer; canonicalization; scope check | FR-065, FR-105 | None known |
| T-20 | Info disclosure | Exports | Backups or exports leak sensitive data | Exports exclude secrets and evidence by default; backup contents shown before writing; optional passphrase encryption (planned, P4) | FR-007, FR-119 | User stores backups insecurely |
| T-21 | Tampering | Install | Sidecar binary replaced in a user-writable install folder | Checksum verification before spawn; per-machine install recommended; signed releases (P4) | NFR-018, NFR-019 | Admin-level attacker |
| T-22 | Tampering | Build | Compromised dependency | Lockfiles; vulnerability and licence scanning; minimal dependencies; review of new dependencies | NFR-018 | Supply-chain risk cannot be eliminated |
| T-23 | Elevation | TB-4 | Malicious page exploits the managed browser | Browser's own sandbox; separate profile; bridge writes only to staging | FR-068 | Browser zero-days |
| T-24 | Safety | P3 desktop | Input lands in the wrong window after focus changes | Verify target window identity before each input; abort on focus change; expected-effect checks | FR-082, FR-083 | Fast focus changes; mitigated by stop and verification |

## 5. Authorization Model

1. **User** creates or imports a workflow → Draft.
2. **Compiler** derives the minimum manifest (FR-102).
3. **User** validates via preview and binds locations and grants the manifest for that version (FR-103).
4. **Policy engine** evaluates each operation at dispatch (component-design §5) and issues `AuthorizedOperation`.
5. **User** approves consequential operations; approvals are bound to operation hashes (FR-099).
6. **Adapters** accept only `AuthorizedOperation` and re-check file handles.

Revocation (FR-107) and manifest changes (FR-103) invalidate authority immediately.

---

## 6. Prompt-Injection and Untrusted Content Defence

Defence in depth, ordered from most to least important. **The first three layers do not depend on the model behaving well.**

| Layer | Control | Effect |
|---|---|---|
| 1 | Closed operation catalog (FR-104) | There is nothing dangerous to call, such as a shell |
| 2 | Policy engine with manifest, scopes, hosts, and approvals (FR-102 to FR-105, FR-099) | Even a fully hijacked model output stays inside the user's grant |
| 3 | Taint rules by parameter position (table below, FR-106) | Untrusted data cannot pick *where* or *what*; only *values* in safe positions |
| 4 | Option sets at decision points; fixed action vocabulary in P2 (FR-047, FR-052) | The model chooses among declared paths, not open-ended actions |
| 5 | Structured outputs with schema validation (FR-110) | Free-form text cannot be smuggled in as actions |
| 6 | Task-scoped prompts; untrusted content delimited and labelled (AIC-03, AIC-04) | Lowers the chance the model is misled |
| 7 | Consistency checks, thresholds, escalation, budgets (FR-049, FR-050) | Catches unstable decisions |
| 8 | Validation rules, verification, review queue (FR-060, FR-061, FR-085) | Wrong data does not silently reach outputs |
| 9 | Instruction-like text detection (EXC-29), informational | Gives the reviewer a signal; never changes capabilities |

### 6.1 Taint rules by parameter position

| Operation | Parameter | Tainted value allowed? | Condition |
|---|---|---|---|
| Any | Operation kind, step order, location name, host, credential reference, approval flag | **No** | Must come from the approved workflow |
| `files.copy` / `files.move` / `files.rename` | Source path | Yes | From `files.list` in a read-granted location; canonicalized |
| | Destination path template values | Yes | Each value passes `sanitize_path_segment`; final path canonicalized inside the destination location |
| `sheet.upsert_rows` | Target file, sheet, key columns | **No** | Literal in workflow |
| | Row values | Yes | Typed conversion per column; formula neutralization |
| `report.write` | Location | **No** | Literal |
| `control.if`, `validate.record` | Operands | Yes | Branches and rules are declared; taint only selects among them |
| `control.decide` | Chosen option | Yes (model output) | Must match a declared option ID (`match_declared_option`) |
| `browser.navigate` (P2) | URL | Host: **No**; path/query: restricted | Host literal or allowlisted; in Adaptive Execution the URL must appear as a link in the current snapshot or match a declared pattern |
| `browser.fill` (P2) | Value | Yes | Non-secret; target element declared or from snapshot; logged as tainted |
| `browser.fill` (P2) | `secretRef` | **No** | Literal reference, allowed host only |
| `desktop.*` (P3) | Target application | **No** | Granted application only |

### 6.2 Test corpus

A maintained corpus of adversarial documents (and later web pages) covering: direct instructions, instructions hidden in white text, metadata, or file names; instructions that impersonate LocalLoop or the user; path-traversal payloads; formula payloads; oversized and malformed files. CI runs the corpus once code exists. Any executed operation outside the approved workflow is a release blocker (NFR-020).

---

## 7. Human Approval Design

See [component-design.md §6](component-design.md#6-approval-design). Security properties:

- Approvals are bound to the exact resolved operation (hash), single-use, and expire with the run.
- Approval dialogs show what will happen in plain language, mark values from untrusted sources, and show the destination host or file.
- To limit approval fatigue: approval is required only for consequential operations; plan approval groups the known ones; the UI never offers "always approve" for `external_send` or `write_irreversible` operations.

## 8. Emergency Stop and Pause

| Aspect | Design |
|---|---|
| Triggers | UI button; tray/menu-bar item; global shortcut (FR-098) |
| Independence | The tray item and shortcut are handled by the native shell, not by the WebView, so they work if the UI hangs |
| Mechanism | An atomic stop flag checked before every dispatch; a cancellation token passed to adapters; HTTP abort for inference; `cancel` to the browser bridge; P3 input loop checks the flag between synthetic events |
| Persistence | Stop is journaled; the run is classified with `user_stopped` |
| Pause | Takes effect at the next step boundary (FR-097) |
| P3 extra | Screen-corner failsafe evaluated (AR-06) |
| Verification | NFR-011, NFR-012 tests |

## 9. Secrets Management

- Stored only in the OS credential store (Windows Credential Manager, macOS Keychain) under LocalLoop-specific names (NFR-016).
- Workflows reference secrets by name; values are resolved in core memory at dispatch time, sent to the bridge over stdio when needed, and cleared from memory after use (zeroizing buffers).
- Secrets are never shown in the UI after entry, never sent to the model, never logged, and never exported.
- MVP: no secrets are needed (no automated sign-in, A-17). P2 introduces credential references (FR-075).

## 10. Data Protection at Rest (D-07)

| Option | Description | Pros | Cons |
|---|---|---|---|
| A | SQLCipher for the whole database + authenticated encryption of evidence files; keys in the OS credential store | Covers every column, including ones added later | Build complexity (crypto library per platform); small performance cost |
| B | Application-level authenticated encryption of *sensitive* columns and evidence files only | Simpler build; selective | Easy to miss a field; metadata stays plaintext |

**Recommendation:** Option A, decided in an ADR during Phase 1 after a build spike on both platforms. Either option protects against copied files and offline disk access. Neither protects against malware running in the user's session, which can request the same keys; the documentation must say so.

## 11. Recording Consent and Privacy Controls

Consent summary hashing (the session starts only with the hash of the summary the user saw), visible indicator, scope filtering, protected-input exclusion, review/redact, retention, and deletion: FR-015 to FR-019, FR-027, NFR-022. See [data-flow.md §2](data-flow.md#2-recording-data-flow-mvp).

## 12. Integrity, Verification, and Partial Completion

Independent re-observation (FR-085); outcome classes that cannot claim unverified success (FR-087); journaled intents and results for crash recovery (FR-091); backups and atomic writes for spreadsheets (FR-063); never-overwrite collision policy (FR-064); duplicate protection (FR-067).

## 13. Build, Release, and Supply Chain

| Control | Phase |
|---|---|
| Lockfiles committed; dependency review on additions | From first code |
| `cargo audit` / `cargo deny` (advisories, licences, bans) and npm audit in CI | From first code |
| Forbidden-dependency check between crates (NFR-030) | From first code |
| Fuzzing of document worker parsers and IPC decoders (`cargo fuzz`) | Phase 1–2 |
| Checksums for bundled sidecars and OCR data; verification at spawn | MVP |
| Code signing and notarization; signed offline updates | Phase 4 |
| GitHub Actions with read-only default token permissions; actions pinned and updated via Dependabot | Now (see `.github/`) |

## 14. Safeguard Coverage

| Safeguard (master brief §6) | Controls | Requirements |
|---|---|---|
| Explicit recording consent | Consent dialog with hashed summary; indicator | FR-015, FR-016 |
| Scoped filesystem and application permissions | Symbolic locations bound at grant; canonicalization; handle check; app registry (P3) | FR-102, FR-103, FR-105, FR-080 |
| Restricted operation allowlists | Closed catalog; per-workflow operation manifest | FR-104, FR-102, ADR-0002 |
| Human approval for destructive or consequential actions | Effect classes; hash-bound single-use approvals | FR-099, SRS §9.4 |
| Protection against prompt injection | §6 layers; taint table; test corpus | FR-106, FR-047, FR-110, NFR-020 |
| Local storage and protection of sensitive data | OS credential store; encryption at rest; masking; retention | NFR-016, NFR-017, FR-095, FR-120 |
| Verification of postconditions | Independent observers | FR-085, FR-087 |
| Partial-completion tracking | Item/step journal; outcome classes | FR-086, FR-091 |
| Controlled retries and recovery | Bounded retries for idempotent/transient only; rollback | FR-089, FR-090, FR-092 |
| Pause and emergency-stop controls | §8 | FR-097, FR-098, NFR-012 |
| Prevention of arbitrary AI-generated command execution | No exec operations; compiler rejects unknown operations; `AuthorizedOperation` type seal | FR-104, NFR-015, C-02 |

## 15. Security Testing Plan

| Test | Target | Requirement |
|---|---|---|
| Prompt-injection corpus | Extraction, decisions, analysis, P2 browser | NFR-020 |
| Path traversal and link-swap suite (per OS) | Files adapter, policy | FR-065, FR-105 |
| Formula injection cases | Spreadsheet adapter | FR-063 |
| Seeded-secret and sensitive-value scans | Logs, DB, reports, exports | FR-095, NFR-016 |
| IPC allowlist and DTO fuzzing | Desktop commands | NFR-014 |
| Parser fuzzing | Document worker | T-13, T-18 |
| Approval tampering (modified parameters after approval) | Approval ledger | FR-099 |
| Stop latency and dispatch-after-stop | Execution engine | NFR-012 |
| Network monitoring during offline suite | Whole app | NFR-007 |

## 16. Residual Risks

1. Local malware with the user's privileges can do anything the user can (out of scope, stated to users).
2. The model can still produce wrong data within allowed positions; validation and review are the mitigation, and accuracy is measured, not assumed (EV-02, EV-03).
3. Approval fatigue can lead to careless approvals; mitigated by minimizing approvals and making them specific.
4. The document worker is process-isolated but not OS-sandboxed until Phase 4.
5. The audit chain is tamper-evident, not tamper-proof.

## 17. Security Review Gates

| Gate | Required before |
|---|---|
| Threat model update + review of new operations and IPC commands | Each phase exit |
| Prompt-injection corpus green, zero policy bypasses | MVP release; each AI scope expansion |
| External or peer security review of policy engine and adapters | MVP release candidate |
