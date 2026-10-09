## Summary

<!-- What does this change do and why? -->

## Links

- Issue / backlog item: <!-- e.g. #12, LL-037 -->
- Requirements: <!-- e.g. FR-063, NFR-002 -->
- ADR (if a design decision changed): <!-- e.g. ADR-0002 -->

## Type

- [ ] Documentation / requirements
- [ ] Feature
- [ ] Fix
- [ ] Test
- [ ] Spike (report included)
- [ ] Chore / CI

## Checklist

- [ ] `python3 scripts/check_docs.py` passes
- [ ] Requirements and the traceability matrix are updated for new or changed behaviour
- [ ] `docs/requirements/REQUIREMENTS_CHECKLIST.md` status and evidence updated for every requirement whose implementation or verification changed (no Implemented/Verified without evidence)
- [ ] Tests cover the change (or the PR explains why not)
- [ ] Proposals, assumptions, and targets are labelled as such; no unmeasured performance claims (NFR-013)
- [ ] No secrets, real documents, personal data, or model files are included
- [ ] AI assistance, if significant, is mentioned below

## Security impact

- [ ] No security impact
- [ ] Adds or changes a catalog operation, IPC command, or sidecar method (threat model and ADR updated)
- [ ] Handles untrusted content (documents, web pages, screen text, model output)
- [ ] Adds or updates a dependency (licence and advisories checked)

<!-- Describe any security-relevant details here. -->

## Notes for reviewers
