# Contributing to LocalLoop

Thank you for your interest. LocalLoop is in the **design phase**: the repository holds requirements, architecture, a draft schema, and checks. Implementation starts with milestone M1.0 ([Roadmap](docs/development/ROADMAP.md)).

> Licensing is not decided yet ([LICENSE_SELECTION.md](LICENSE_SELECTION.md)). Please ask before contributing substantial code, because contribution terms (for example a CLA) may be required.

## Ways to contribute now

- Review the [SRS](docs/requirements/SRS.md) and [architecture](docs/architecture/SYSTEM_ARCHITECTURE.md); open issues for ambiguities, contradictions, or untestable requirements.
- Challenge assumptions (`A-nn`) and decisions (`D-nn`) with evidence.
- Propose test cases or adversarial fixtures (synthetic only).

## Workflow

1. Find or open an issue. Reference backlog IDs (`LL-037`) and requirement IDs (`FR-063`).
2. Branch from `main`: `feat/…`, `fix/…`, `docs/…`, `spike/…`, `test/…`.
3. Use [Conventional Commits](https://www.conventionalcommits.org/): `feat(policy-engine): deny tainted hosts`.
4. Run the checks (below) and open a pull request using the template.

## Documentation rules

- **Requirements:** new or changed behaviour needs a requirement in the SRS with priority, release, validation status, source, and acceptance criteria, plus a row in the [traceability matrix](docs/requirements/requirements-traceability.md). IDs are never reused.
- **Decisions:** significant design changes need an ADR ([template](docs/adr/template.md)).
- **Honest claims:** no performance or accuracy figure without a reproducible benchmark (NFR-013). Label proposals, assumptions, and targets as such.
- **Diagrams:** Mermaid in Markdown so they render on GitHub.

## Engineering rules (from first code)

- **Security first.** Do not add an operation to the catalog, a Tauri command, or a sidecar method without updating the threat model and, for operations, writing an ADR (ADR-0002). Never add a path that executes commands or code from workflows, documents, websites, or models.
- **Respect layer boundaries.** `local-ai` must not depend on policy, execution, storage, or adapters; adapters must not depend on `local-ai` (NFR-030).
- **Treat external content as data.** Wrap it as tainted; sanitize per position; never render it as HTML.
- **No secrets or sensitive values in logs**, reports, prompts, or test snapshots.
- **Rust:** `cargo fmt`, `cargo clippy -- -D warnings`; no `unsafe` without a justification comment and review; no `unwrap()`/`expect()` in non-test code paths that handle external input; typed errors.
- **TypeScript:** `strict` mode; no `any`; no `dangerouslySetInnerHTML` for untrusted content.
- **Tests:** every catalog operation needs tests for parameter validation, policy, execution, postconditions, and undo (NFR-031).
- **Data:** synthetic fixtures only. Never commit real documents, personal data, credentials, or model weights (`*.gguf` is git-ignored).

## Checks

```bash
python3 scripts/check_docs.py
python3 -m pip install -r scripts/requirements.txt && python3 scripts/validate_schemas.py
# optional, needs Node.js:
npm install --no-save @mermaid-js/mermaid-cli@11.17.0 && python3 scripts/validate_mermaid.py --mmdc node_modules/.bin/mmdc
```

## AI-assisted contributions

AI tools may be used. You are responsible for every line you submit: review it, test it, and make sure it follows this guide. Mention significant AI assistance in the pull request.

## Conduct

Be respectful and constructive. Critique ideas, not people. Maintainers may moderate discussions that are not.
