# ADR-0007: Preserve XLSX packages and reject unsupported workbook writes

| Field | Value |
|---|---|
| Status | Proposed |
| Date | 2026-10-10 |
| Deciders | Project owner, pending milestone review |
| Related requirements | FR-062, FR-063, A-05, EXC-08, EXC-09 |

## Context

[EV-04](../development/spikes/EV-04-xlsx.md) demonstrated chart loss and an unexpected column-width change with umya-spreadsheet 3.1.0. A narrow ZIP/XML cell update preserved all untouched package parts and the independently checked semantics. A successful writer return does not prove fidelity.

## Decision

Recommend a constrained package-preserving XLSX writer using ZIP and quick-xml, with a separate reader/observer. Accept only the explicitly implemented simple workbook subset. Reject unknown parts/relationships, macros, pivots, external links, protection/signatures and advanced workbook features before any original-file write. Separate output files or CSV are the fallback; never flatten an unsupported original workbook silently.

The M1.2 adapter must specify its exact supported structures and mappings, enforce quotas, retain untouched parts, neutralize untrusted formulas as literal text, lock and back up first, stage and atomically replace, then re-read all required postconditions. Existing formulas must never be overwritten by an untrusted value.

## Consequences

- More implementation work than a generic library round trip, but the supported surface is explicit and testable.
- The one-cell spike does not demonstrate general upsert, row insertion, formula recalculation or table expansion.
- Unsupported workbooks remain unchanged and receive an actionable EXC-09 result.
- macOS lock and filesystem behavior remain deferred under ADR-0010.

## Alternatives considered

| Option | Reason |
|---|---|
| Unrestricted umya round trip | Measured integrity regressions on synthetic F6 |
| Rebuild a workbook from read values | Can discard formatting, formulas and unrelated sheets; suitable only for a new output file |
| Excel automation | Requires Excel and broadens the application integration scope |

## Validation

TC-052 and TC-053 in M1.2 must cover supported row upserts, unsupported package refusal, lock behavior, formula payloads, independent re-read, backup/restore and kill-during-write. The spike is groundwork, not completion of these requirements.
