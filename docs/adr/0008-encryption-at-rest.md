# ADR-0008: Encrypt the database with SQLCipher and evidence with authenticated encryption

| Field | Value |
|---|---|
| Status | Proposed |
| Date | 2026-10-10 |
| Deciders | Project owner, pending milestone review |
| Related requirements | NFR-016, NFR-017, NFR-004, FR-119, D-07 |

## Context

[LL-010 / D-07](../development/spikes/D-07-encryption.md) built and ran both encryption options on Windows. SQLCipher protected the entire database, including the tested metadata and live WAL. Selective application-level encryption protected the tested sensitive columns but exposed vendor names, schema, row counts and indexed invoice identifiers. Both used authenticated encryption for evidence files and a key in Windows Credential Manager.

## Decision

Recommend SQLCipher for the whole product database and XChaCha20-Poly1305 for sensitive evidence files. Keep random key material in the OS credential store. Production must use independently generated or domain-separated database and evidence keys; the throwaway spike reuses one key only to compare the options.

Fail closed when the credential store or decryption fails. Bind evidence ciphertext to an immutable evidence identifier and format version through associated data; refuse substitutions and corruption. Never persist a plaintext fallback, key, or temporary sensitive file. Lock down database extensions and the storage API; encryption does not authorize operations.

## Consequences

- Whole-database encryption reduces the risk of newly added sensitive fields escaping a selective-encryption list.
- Windows native builds require a supported native Perl and vendored OpenSSL toolchain. The first local dependency build took about 21 minutes; release packaging and dependency review remain work.
- LL-027 must cover migrations, WAL/crash recovery, encrypted backup/restore, unavailable/lost keys, authenticated evidence formats and plaintext scans. The spike does not implement product storage.
- Missing keys mean encrypted data cannot be recovered without an explicit recovery design; never silently create a new database over the existing one.
- macOS Keychain, compilation and packaging are deferred under ADR-0010.
- Copied files are protected; malware in the same user session can access the credential store. This does not provide protection from a compromised session.

## Alternatives considered

| Option | Reason |
|---|---|
| Selective encrypted columns in plain SQLite | Meets the tested sensitive-value scan but leaves metadata plaintext and requires every new field to be classified correctly |
| Encrypt the entire SQLite file only at shutdown | Can leave plaintext while running or after a crash; unsuitable for live WAL and recovery |
| Plain SQLite relying on disk encryption | Does not meet the app's portable at-rest requirement for copied files |

## Validation

NFR-017 / TC-112 remains Not Started for the product until LL-027 runs its own storage acceptance tests. The Windows spike independently scanned persisted files, checked value round trips and reopen, refused opening SQLCipher without a key, and verified credential deletion. Review this ADR at the M1.0 boundary before dependent storage implementation.
