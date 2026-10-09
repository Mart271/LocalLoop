# Diagrams

All diagrams are **Mermaid code embedded in the Markdown documents**, so GitHub renders them and they are reviewed alongside the text they illustrate. There is one source for each diagram; this folder does not keep copies.

If exported images (SVG/PNG) are ever needed, for example for a slide deck or a printed review, put them here, name them after the section they come from, and treat the Markdown as the source of truth.

CI renders every Mermaid block with the Mermaid CLI to catch syntax errors (`scripts/validate_mermaid.py`).

## Index

| Diagram | Type | Location |
|---|---|---|
| System context (C4 level 1) | Flowchart in C4 style | [SYSTEM_ARCHITECTURE §3](../SYSTEM_ARCHITECTURE.md#3-system-context-c4-level-1) |
| Containers (C4 level 2) | Flowchart in C4 style | [SYSTEM_ARCHITECTURE §4](../SYSTEM_ARCHITECTURE.md#4-containers-c4-level-2) |
| Seven layers | Flowchart | [SYSTEM_ARCHITECTURE §5](../SYSTEM_ARCHITECTURE.md#5-layered-architecture) |
| Component architecture | Flowchart | [SYSTEM_ARCHITECTURE §6](../SYSTEM_ARCHITECTURE.md#6-component-architecture) |
| Module dependency rules | Flowchart | [SYSTEM_ARCHITECTURE §6.1](../SYSTEM_ARCHITECTURE.md#61-module-dependency-rules-nfr-030) |
| Compilation pipeline | Flowchart | [SYSTEM_ARCHITECTURE §8](../SYSTEM_ARCHITECTURE.md#8-workflow-representation-and-compilation-pipeline) |
| Workflow recording | Sequence | [SYSTEM_ARCHITECTURE §9.1](../SYSTEM_ARCHITECTURE.md#91-workflow-recording-mvp-guided-demonstration) |
| Exact Replay execution | Sequence | [SYSTEM_ARCHITECTURE §9.2](../SYSTEM_ARCHITECTURE.md#92-exact-replay-execution) |
| Adaptive Execution | Sequence + flowchart | [SYSTEM_ARCHITECTURE §9.3](../SYSTEM_ARCHITECTURE.md#93-adaptive-execution) |
| Local AI inference flow | Sequence | [SYSTEM_ARCHITECTURE §9.4](../SYSTEM_ARCHITECTURE.md#94-local-ai-inference-flow) |
| Failure and recovery | Flowchart | [SYSTEM_ARCHITECTURE §9.5](../SYSTEM_ARCHITECTURE.md#95-failure-and-recovery-flow) |
| Data flow (level 0) | Flowchart | [SYSTEM_ARCHITECTURE §10.1](../SYSTEM_ARCHITECTURE.md#101-data-flow-level-0) |
| Logical data model | Entity-relationship | [SYSTEM_ARCHITECTURE §10.2](../SYSTEM_ARCHITECTURE.md#102-logical-data-model) |
| Security and trust boundaries | Flowchart | [SYSTEM_ARCHITECTURE §11](../SYSTEM_ARCHITECTURE.md#11-security-and-trust-boundaries) |
| Offline deployment | Flowchart | [SYSTEM_ARCHITECTURE §12](../SYSTEM_ARCHITECTURE.md#12-offline-deployment-architecture) |
| Platform integration boundaries | Flowchart | [SYSTEM_ARCHITECTURE §13](../SYSTEM_ARCHITECTURE.md#13-platform-specific-integration-boundaries) |
| Run and step state machines | State | [component-design §4](../component-design.md#4-state-machines) |
| MVP document data flow (level 1), recording, taint, browser | Flowchart | [data-flow.md](../data-flow.md) |
| Workflow lifecycle | State | [SRS §11.1](../../requirements/SRS.md#111-workflow-lifecycle) |
| Use case overview | Flowchart | [use-cases.md](../../requirements/use-cases.md#use-case-overview) |
| MVP minimum components | Flowchart | [MVP_SCOPE §3](../../development/MVP_SCOPE.md#3-minimum-components) |
| Phases and gates | Flowchart | [ROADMAP §1](../../development/ROADMAP.md#1-overview) |
