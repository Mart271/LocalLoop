# Security Policy

## Project status

LocalLoop is **pre-implementation**: there are no releases and no application code yet. This policy covers the documentation, schema, and scripts in this repository now, and will cover the application once code exists.

## Supported versions

| Version | Supported |
|---|---|
| No releases yet | — |

## Reporting a vulnerability

Please **do not open a public issue** for security problems.

- Once the repository is published on GitHub, use **private vulnerability reporting** (*Security → Report a vulnerability*).
- Until then, contact the maintainer privately.

Please include: affected component or document, steps to reproduce, impact, and any suggested fix. **Do not include real personal data, real business documents, or credentials** in a report; use synthetic examples.

Response goals (best effort for a small project): acknowledge within 7 days, share an assessment within 30 days, and credit reporters who wish to be named.

## Security model in brief

LocalLoop's central rule is that **AI reasoning is never execution permission**:

- The local model only proposes. A compiler and a policy engine turn proposals into operations from a **closed catalog**; there is no operation that runs shell commands or code.
- Every operation is checked against the workflow's permission manifest, the user's grant, scope rules, and taint rules. Consequential operations need explicit, hash-bound human approval.
- Results are verified by re-observing state; outcomes are never reported as completed without evidence.
- Untrusted content (documents, web pages, screens) is treated as data and cannot expand permissions.
- Secrets live only in the operating system's credential store.

Full threat model, controls, and residual risks: [docs/architecture/security-architecture.md](docs/architecture/security-architecture.md).

## Scope

In scope: prompt injection leading to unauthorized actions; scope escapes (path traversal, link swaps); secret or sensitive-data leakage; parser vulnerabilities; IPC or UI privilege issues; approval bypass; integrity problems (unverified success, corrupted files).

Out of scope: attacks that require malware already running with the user's or an administrator's privileges; vulnerabilities in the operating system, WebView, or browser engines themselves (please report those upstream); security of third-party websites that users automate.
