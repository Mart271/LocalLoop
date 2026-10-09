# ADR-0003: Local inference through an on-demand llama.cpp sidecar

| Field | Value |
|---|---|
| Status | Proposed (pending EV-01) |
| Date | 2026-10-09 |
| Deciders | Project owner (pending review) |
| Related requirements | FR-108 to FR-113, NFR-008 to NFR-010, AIC-05, AIC-06 |

## Context

The proposal names llama.cpp "or another compatible local inference engine" (P§5 Layer 3), small quantized models for low-memory machines, and unloading inactive models (P§7). Outputs must be structured and validated (FR-110). The core is written in Rust.

## Decision

Run inference in a **separate process** using llama.cpp's server (`llama-server`), bundled per platform and pinned to a tested version:

- Spawned on demand by the runtime supervisor; ended after an idle timeout to free memory (FR-112).
- Bound to `127.0.0.1` on a random port with a per-session API key (or stdio if the chosen build supports it), never exposed to the network (AIC-05).
- Requests carry a JSON schema so generation is constrained to valid JSON; outputs are validated again in `local-ai` (FR-110).
- Models are GGUF files registered with SHA-256, licence, and capability level, and verified before every load (FR-108).
- The model shortlist and memory budgets come from EV-01 on the reference machines.

## Consequences

- Positive: memory is fully released by ending the process; runtime crashes do not crash the app; runtime upgrades are isolated; the same approach works on Windows (CPU/Vulkan/CUDA builds) and macOS (Metal).
- Negative: one more binary per platform and GPU backend to package; process start and model load latency on first use; HTTP or IPC overhead (small compared with inference).
- Follow-up: EV-01 benchmark (memory, latency, structured-output validity rate) for 2–3 candidate small instruct models; define the idle timeout default; licence review of chosen models.

## Alternatives considered

| Option | Why not chosen (for now) |
|---|---|
| Embed llama.cpp in-process through Rust bindings | No process isolation; harder to guarantee memory release; a crash kills the app |
| Rust-native engines (`candle`, `mistral.rs`) in-process | Attractive single-language stack; keep as a fallback candidate in EV-01, but same isolation concerns |
| Ollama as a dependency | Separate install and background service with its own network listener; less control over versions; could be supported later as an optional "bring your own local endpoint" |
| ONNX Runtime GenAI, MLC LLM | Viable; fewer GGUF models available off the shelf; can be revisited if EV-01 favours them |

## Validation

EV-01 report: per model and machine, peak memory, load time, tokens/second, structured-output validity rate, and task accuracy on a small fixed set. Revisit if no candidate meets the Lightweight Local AI needs on 8 GB machines; in that case AI features are limited to higher-memory machines and the product still works at Basic Automation level.
