# ADR-0002: Closed operation catalog; no arbitrary command execution

| Field | Value |
|---|---|
| Status | Proposed |
| Date | 2026-10-09 |
| Deciders | Project owner (pending review) |
| Related requirements | FR-031, FR-102, FR-104, FR-106, NFR-015, NFR-020, C-02 |

## Context

The proposal excludes "arbitrary AI-generated shell commands or unrestricted code execution" from the default execution model (P§5 Layer 4) and requires restricted execution of generated operations (P§9). Local models can be misled by content in documents and websites. If any execution path accepts free-form commands, a single successful injection could do anything the user can do.

## Decision

1. LocalLoop executes only operations listed in a versioned **operation catalog** (component-design §2). Each entry defines its parameters, effect class, scope rules, idempotency, undo, and default postconditions.
2. The catalog contains **no** operation that runs shell commands, scripts, or code from workflows, documents, websites, or models, and no generic HTTP request or permanent delete operation.
3. Conditions and templates are declarative data with a fixed set of operators and filters; there is no embedded expression or scripting language.
4. Adding an operation requires an ADR covering effect class, scope rules, postconditions, undo, taint positions, and tests.

## Consequences

- Positive: removes the highest-impact failure mode by design; makes policy evaluation and testing tractable; workflow files stay inspectable by non-programmers.
- Negative: some tasks cannot be automated until a suitable operation is added; power users cannot "drop to a script".
- Follow-up: publish the catalog with the schema; consider a future, separately reviewed extension mechanism only if user research shows strong need (would require its own sandbox design and ADR).

## Alternatives considered

| Option | Why not chosen |
|---|---|
| Allow shell commands with user approval | Approval fatigue; users cannot judge command safety; conflicts with P§5 |
| Embedded scripting language (Lua, JavaScript) in a sandbox | Large attack surface and sandbox-escape risk; harder to verify and explain |
| Generic HTTP operation | Easy data exfiltration channel; replaced by allowlisted browser operations |

## Validation

Static review that no IPC command, adapter, or sidecar method executes caller-supplied commands; prompt-injection corpus with zero policy bypasses (NFR-020).
