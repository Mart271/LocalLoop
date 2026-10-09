# `local-ai`

> **Planned — no code yet.** Design: [component-design.md §3.5](../../docs/architecture/component-design.md#35-local-ai--model-registry-runtime-prompts-structured-outputs), [ADR-0003](../../docs/adr/0003-local-inference-sidecar.md).

**Layer 3: Local AI Intelligence.** Implements the AI ports defined by `workflow-engine`. Everything it returns is an **untrusted proposal or untrusted data**.

## Responsibilities

- Model registry: import a model from a local file or offline package, verify its hash, and record licence and size (FR-108).
- Capability levels (Basic Automation, Lightweight Local AI, Enhanced Local AI) and a resource guard that refuses to load a model the machine cannot hold (FR-109, FR-113).
- Supervise the inference sidecar (a llama.cpp server bound to `127.0.0.1` with a random port and a per-session key), load on demand, and unload when idle (FR-112, NFR-010).
- Versioned prompt templates that mark every slot as trusted or untrusted, so document and page text are never treated as instructions (FR-106).
- Request schema-constrained output and validate it; invalid output is retried within limits, then escalated, never guessed (FR-110).
- Task APIs: demonstration analysis, field extraction, decision choice among declared options, mode signals, and explanations.
- Behaviour when no model is available: AI features are disabled and model-free workflows still run (FR-111).

## Must not

- Depend on `policy-engine`, `execution-engine`, adapters, or `storage` (NFR-030). It cannot reach an adapter even by mistake.
- Call any remote AI service. There is no network client for model APIs in the product (C-03).

## Open questions

- Runtime build and model shortlist for 8 GB machines: EV-01, D-05.
- Model-assisted extraction and decision quality: EV-02, EV-03. Related requirements stay *Unvalidated* until measured.

## First backlog items

LL-073 (registry), LL-074 (resource guard), LL-075 (sidecar supervisor), LL-076 (prompt templates and output validator), LL-077 (field extractor), LL-078 (demonstration analyzer). All are milestone M1.5.
