# `policy-engine`

> **Planned — no code yet.** Design: [component-design.md §3.2](../../docs/architecture/component-design.md#32-policy-engine--permissions-scopes-taint-approvals) and [§5](../../docs/architecture/component-design.md#5-policy-evaluation).

**Layer 4: Policy Engine.** The only component that can authorize an operation. AI reasoning is never treated as permission (C-01).

## Responsibilities

- Evaluate every resolved operation before dispatch, in both execution modes, and return `Allow`, `RequireApproval`, or `Deny` (FR-048, FR-104).
- Issue `AuthorizedOperation`, a sealed type that only this crate can construct and the only input adapters accept.
- Enforce the permission manifest and the user's grants, which are bound to a workflow version (FR-102, FR-103, FR-107).
- Canonicalize paths (symbolic links, junctions, `..`, case, Unicode) and re-check opened handles to prevent swap attacks (FR-105).
- Apply taint rules: values from documents, pages, screens, or models may fill only declared parameter positions and never choose locations, hosts, or operations (FR-106).
- Decide approval requirements from effect class and author marking (FR-099).
- Enforce host allowlists for browser operations (FR-074, Phase 2).

## Must not

- Depend on `local-ai`, `execution-engine`, adapters, or storage.
- Default to allow. Anything not explicitly permitted is denied and audit-logged.

## First backlog items

LL-021 (pipeline and sealed type), LL-022 (path canonicalization per OS), LL-023 (taint), LL-051 (grants and revocation).
