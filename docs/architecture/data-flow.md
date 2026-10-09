# LocalLoop — Data Flow

| Field | Value |
|---|---|
| Version | 0.1 (draft) |
| Date | 2026-10-09 |
| Parent | [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md) |

> **Status:** Proposed design. Retention defaults below are proposals to confirm, not decisions.

This document details how data moves through LocalLoop: the MVP document-processing flow, recording, AI calls, and (Phase 2) browser flows. It also specifies data classification handling, **taint propagation**, and the data lifecycle. Classification levels are defined in [SRS §8.1](../requirements/SRS.md#81-data-inventory-and-classification).

---

## 1. MVP Document Workflow (DFD level 1)

```mermaid
flowchart TB
    inbox[("Input location<br/>granted, read")]
    ref[/"Reference list<br/>optional, read"/]
    sheet[("Target spreadsheet<br/>granted, write")]
    dest[("Destination location<br/>granted, write")]
    review[("Review queue")]
    rpt[/"Report files<br/>HTML, JSON, CSV"/]

    list["1 List documents<br/>files.list"]
    read["2 Read bytes<br/>files adapter, in scope"]
    parse["3 Parse and OCR<br/>document worker"]
    extract["4 Extract fields<br/>rules or local model"]
    validate["5 Validate record"]
    dup["6 Duplicate check"]
    upsert["7 Upsert row<br/>backup, atomic write"]
    org["8 Move or rename<br/>sanitized template"]
    verify["9 Verify postconditions<br/>re-read state"]
    report["10 Write report"]

    ev[("Evidence store<br/>encrypted if sensitive")]
    jr[("Journal and audit")]

    inbox -->|"DF-01 file names, metadata"| list
    list -->|"DF-02 item list"| read
    inbox -->|"DF-03 document bytes, untrusted"| read
    read -->|"DF-04 bytes over stdio"| parse
    parse -->|"DF-05 text and positions, tainted"| extract
    extract -->|"DF-06 record with provenance, tainted"| validate
    ref -->|"DF-07 allowed values"| validate
    validate -->|"DF-08 invalid record and reasons"| review
    validate -->|"DF-09 valid record"| dup
    dup -->|"DF-10 existing key match"| review
    dup -->|"DF-11 new record"| upsert
    upsert -->|"DF-12 neutralized cell values"| sheet
    upsert --> org
    org -->|"DF-13 file move within scope"| dest
    sheet -->|"DF-14 re-read rows"| verify
    dest -->|"DF-15 re-read file hash"| verify
    verify --> report
    report -->|"DF-16 masked summary"| rpt
    extract --> ev
    verify --> ev
    upsert --> jr
    org --> jr
    verify --> jr
```

### 1.1 Flow catalogue

| Flow | Data | Classification | Tainted | Protection |
|---|---|---|---|---|
| DF-01 | File names and metadata in the input location | Internal | Yes (names are attacker-controllable) | Scope check; names never used as paths without canonicalization |
| DF-03 | Document bytes | Sensitive | Yes | Read only inside granted scope; size limit |
| DF-04 | Bytes sent to worker | Sensitive | Yes | Stdio only; worker has no file or network access by design |
| DF-05 | Extracted text with coordinates | Sensitive | Yes | Kept in memory; stored as evidence only per retention |
| DF-06 | Typed record + provenance | Sensitive | Yes | Field-level sensitivity tags from the record schema |
| DF-08 / DF-10 | Items for review | Sensitive | Yes | Review UI shows values as plain text |
| DF-12 | Cell values | Sensitive | Yes | Formula neutralization; typed conversion (FR-063) |
| DF-13 | File move | Internal | Path segments derived from tainted values | Sanitized segment + canonicalization + handle check (FR-065, FR-105) |
| DF-14 / DF-15 | Observed state | Internal | No (observed by LocalLoop) | Read-only observers |
| DF-16 | Report | Sensitive (masked by default) | Contains tainted values | Masking of *sensitive* fields; HTML-escaped output |

---

## 2. Recording Data Flow (MVP)

```mermaid
flowchart LR
    user(["User"])
    consent["Consent dialog<br/>scope summary"]
    capture["Scoped capture<br/>file events"]
    annotate["Annotation and mapping<br/>in LocalLoop UI"]
    filter["Scope filter and<br/>protected-input exclusion"]
    reviewR["Review and redact"]
    bundle[("Demonstration bundle<br/>local, deletable")]
    analysis["Analysis<br/>local model or literal draft"]

    user --> consent --> capture
    user --> annotate
    capture --> filter
    annotate --> filter
    filter --> reviewR
    user -->|"deletes items"| reviewR
    reviewR --> bundle --> analysis
```

Data never captured: events outside the selected folders, protected inputs (FR-018), and file contents other than the samples the user chose to annotate.

---

## 3. AI Data Flow and Minimization

| AI task | What is sent to the model | What is never sent | What is stored |
|---|---|---|---|
| Demonstration analysis (AI-01) | Objective, event list with redacted values, field annotations (names, types, sample values) | Secrets, protected inputs, unrelated documents | Inference record; proposal (as evidence, per retention) |
| Field extraction (AI-03) | Text of the current document (or the pages the template names), field schema | Other documents, previous items' values | Inference record; extracted record with provenance |
| Decision (AI-04) | Declared options, validated record fields relevant to the decision, short excerpt if the decision declares it | Secrets, unrelated fields marked *sensitive* unless the decision declares them | Decision + inference record |
| Explanation (AI-06) | Factor values, step names | Document content | Rendered text |

Prompts are built from templates whose untrusted slots are delimited and labelled as data (AIC-03). Prompts are not stored by default when they contain *sensitive* values; the inference record stores template ID, version, and hashes instead (AIC-07).

---

## 4. Taint Propagation

```mermaid
flowchart LR
    subgraph sources ["Taint sources"]
        s1["Document text and OCR"]
        s2["File names in input locations"]
        s3["Web page content, P2"]
        s4["Screen and UI text, P3"]
        s5["Model output"]
    end

    subgraph prop ["Propagation"]
        p1["Extraction, parsing,<br/>template rendering:<br/>output stays tainted"]
    end

    subgraph sanit ["Sanitizers, position-specific"]
        z1["sanitize_path_segment"]
        z2["parse_typed: decimal, date, enum"]
        z3["neutralize_cell_value"]
        z4["match_declared_option"]
    end

    subgraph sinks ["Sinks"]
        k1["Path leaf segment: allowed after z1"]
        k2["Cell value: allowed after z3"]
        k3["Condition operand: allowed, branches are declared"]
        k4["Decision choice: allowed only via z4"]
        k5["Location, host, credential, operation kind, step order: NEVER"]
    end

    s1 --> p1
    s2 --> p1
    s3 --> p1
    s4 --> p1
    s5 --> p1
    p1 --> z1 --> k1
    p1 --> z3 --> k2
    p1 --> z2 --> k3
    p1 --> z4 --> k4
    p1 -.->|"denied by policy"| k5
```

Rules:

1. Every value from a source in the diagram is wrapped as `Tainted<T>` (component-design §3.1).
2. Sanitizers produce values valid only for their sink position; a sanitized path segment is not acceptable as a host, for example.
3. The policy engine checks taint per parameter position (FR-106; full table in [security-architecture.md §6](security-architecture.md#6-prompt-injection-and-untrusted-content-defence)).
4. Taint never "washes out" through the model: model output is itself a taint source.

---

## 5. Browser Data Flow (Phase 2; MVP only if D-02)

```mermaid
flowchart LR
    core["LocalLoop core"]
    bridge["Browser bridge"]
    browser["Managed browser<br/>LocalLoop profile"]
    site["Allowlisted host"]
    staging[("Bridge staging folder")]
    dest[("Granted location")]
    keys["OS credential store"]

    core -->|"commands, allowlist"| bridge
    bridge --> browser
    browser <-->|"HTTPS, allowlisted only"| site
    browser -->|"downloads"| staging
    bridge -->|"snapshots, extracted data: tainted"| core
    core -->|"files.move under policy"| staging
    staging --> dest
    keys -->|"secret resolved in core memory, P2"| core
    core -->|"secret over stdio, never logged"| bridge
```

The bridge writes only to its staging folder. Files reach user folders only through a policy-checked `files.move`.

---

## 6. Data Lifecycle and Retention

| Data | Created | Used | Retention default (proposed) | Deletion |
|---|---|---|---|---|
| Raw recording | Recording session | Analysis | Kept until the workflow is created, then 30 days (configurable) | User delete (FR-027) or retention cleanup |
| Workflow versions | Save, import, revert | Execution, history | Until the workflow is deleted | User delete; exported copies are the user's |
| Run records (steps, outcomes) | Each run | History, audit | 1 year (configurable) | Retention cleanup |
| Evidence (values, page images) | Runs | Review, reports | 90 days (configurable) | FR-120 |
| Audit chain | Security events | Verification | Until the user deletes all data | Only via full data reset (logged as a new chain start) |
| Reports | Run end | User | User-managed (in their folders) | User |
| Inference records | Each AI call | Provenance | Same as run records; outputs per evidence retention | Retention cleanup |
| Backups | User action | Restore | User-managed | User |

Deleting data removes rows and files; it does not guarantee physical erasure on SSDs (NFR-023), and the UI says so.

---

## 7. External Data Flows

Only these flows can leave the device, and only through approved workflow steps:

| Flow | Release | Control |
|---|---|---|
| Browser navigation and requests to allowlisted hosts | MVP if D-02, else P2 | FR-074 |
| Form submissions and uploads | P2 | `external_send` approval (FR-099) |
| User-initiated export or backup to a chosen location (possibly a synced folder) | MVP | User action; exports exclude secrets and evidence by default (FR-007) |

There is no telemetry, crash upload, or update check by default (FR-117).
