# `workflow-engine`

> **Skeleton only (LL-001):** the crate builds but has no public API yet. Design: [component-design.md §3.1](../../docs/architecture/component-design.md#31-workflow-engine--domain-model-compiler-planner-recommender).

**Layer 4: Workflow Compiler.** The core of the domain. It turns untrusted proposals and user edits into validated workflow definitions and execution plans.

## Responsibilities

- Domain types for workflows, versions, steps, locations, record schemas, and postconditions, matching the [workflow schema](../../schemas/workflow/0.1/workflow.schema.json) (FR-002, NFR-029).
- **Ports** (traits) that `local-ai` implements: `WorkflowAnalyzer`, `FieldExtractor`, `DecisionProvider`. The execution-side traits live elsewhere because they name policy types this crate must not depend on: `OperationAdapter` (takes an `AuthorizedOperation`) is defined in `execution-engine`, and `StateObserver` in `verification-engine` ([component-design.md §3.3–3.4](../../docs/architecture/component-design.md#33-execution-engine--orchestration-journal-control-decisions)).
- The **`Tainted<T>`** wrapper and its sanitizers (`sanitize_path_segment`, typed parsers) live here, because `local-ai` ports return tainted values and `local-ai` cannot depend on `policy-engine`. The rules for *which parameter positions* accept tainted values live in `policy-engine` (FR-106).
- **Compiler:** catalog check, type check, derivation of the minimum permission manifest, and errors that point to the exact field (FR-012, FR-031, FR-102, FR-104).
- **Conditions and templates** with a fixed set of operators and filters. Expressions are references, not code ([component-design.md §8](../../docs/architecture/component-design.md#8-expressions-and-templates)).
- **Planner and preview:** item plans and plan hashes (FR-034, NFR-005).
- **Mode recommender:** deterministic rules over the six factors, with explanation templates (FR-035 to FR-039).
- Rule-based field extraction and validation rules (FR-057, FR-060).
- Lifecycle state machine for versions (FR-011, FR-040).

## Must not

- Perform I/O or depend on any other internal crate.
- Accept model output as anything other than an untrusted proposal.

## First backlog items

LL-014 (schema and domain model), LL-015 (hashing), LL-016 (compiler), LL-017 (conditions and templates), LL-018 (path segment sanitizer), LL-019 (planner), LL-020 (lifecycle).
