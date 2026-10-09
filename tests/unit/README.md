# Unit Tests (shared cases)

Most unit tests live **inside each crate** (`#[cfg(test)]` modules) and next to UI components (`*.test.ts`). This folder is for **language-neutral, table-driven cases** that several implementations must agree on. Planned examples:

- **Policy decision tables**: effect class × grant × approval state → `Allow`, `RequireApproval`, or `Deny` ([component-design.md §5](../../docs/architecture/component-design.md#5-policy-evaluation); FR-099, FR-105).
- **Path canonicalization cases**: `..`, symbolic links, Windows junctions, case and Unicode variants that must stay inside or be denied (FR-105).
- **Outcome classification tables**: step records → completed, partially completed, failed, or unverified (FR-086, FR-087).
- **Mode recommendation tables**: six factor signals → recommendation (FR-035, FR-039).

Nothing is here yet. Cases will be added with milestone M1.0 and later ([Roadmap](../../docs/development/ROADMAP.md)).
