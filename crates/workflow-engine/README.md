# `workflow-engine`

> **Planned — no code yet.** Design: [component-design.md §3.1](../../docs/architecture/component-design.md#31-workflow-engine--domain-model-compiler-planner-recommender).

**Layer 4: Workflow Compiler.** The core of the domain. It turns untrusted proposals and user edits into validated workflow definitions and execution plans.

## Responsibilities

- Domain types for workflows, versions, steps, locations, record schemas, and postconditions, matching the [workflow schema](../../schemas/workflow/0.1/workflow.schema.json) (FR-002, NFR-029).
- **Ports** (traits) that other crates implement: `WorkflowAnalyzer`, `FieldExtractor`, `DecisionProvider` (implemented by `local-ai`), `StateObserver`, `OperationAdapter`.
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
