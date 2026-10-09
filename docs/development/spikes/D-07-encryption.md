# D-07 / LL-010: Windows encryption at rest comparison

Date: 2026-10-10 (Asia/Manila). [SQLCipher runtime](evidence/ll010-a-windows.json), [first native build](evidence/ll010-a-first-build-windows.json), [application AEAD](evidence/ll010-b-windows.json), [Rust probe](../../../spikes/encryption/src/main.rs).

## Environment and method

MSI MS-7A70, Intel Core i5-7500, approximately 16 GB RAM, Windows 10 Pro build 19045, x64. Rust 1.99.0, Visual Studio 2022 MSVC 14.44.35207; rusqlite 0.40.2, keyring 3.6.3, chacha20poly1305 0.10.1. SQLCipher reports 4.14.0 community. Vendored OpenSSL 3.6.3 (openssl-src 300.6.1+3.6.3, openssl-sys 0.9.117) uses Strawberry Perl 5.42.3.1. No model or quantization; no 8 GB or macOS claim.

Each option inserts 10,000 synthetic rows with a repeated internal vendor marker and sensitive totals/notes, reads and compares all values, performs 1,000 indexed lookups, and encrypts/decrypts twenty 256 KiB evidence files. Unique temporary folders and per-run credential entries prevent interference or overwriting unrelated files. Keys are stored, loaded and compared through Windows Credential Manager; a store error fails the run. No in-memory fallback is accepted.

Both options use random 24-byte nonces and XChaCha20-Poly1305 for evidence, with file identifiers as associated data. Option B also binds each encrypted column to its row/column. The spike uses one random 256-bit key for comparison; production needs key separation. No key is printed. Each successful run explicitly deletes its credential and temporary folder.

Scans inspect the live database/WAL/evidence before checkpoint, after checkpoint and after database close for the exact sensitive marker. Database read-back, lookup IDs, persisted row count after reopen, evidence plaintext equality and wrong-file associated-data refusal are enforced assertions. Option B additionally refuses row substitution and a flipped ciphertext bit. This finite marker scan does not prove that all possible sensitive data, OS paging or crash dumps are protected.

## Results

Both final runs exited successfully. These are one exploratory sample per option, with warm caches and uncontrolled background activity, not a controlled speed comparison or release performance promise.

| Measurement | A: SQLCipher | B: selected columns encrypted |
|---|---|---|
| Credential store / load | 3.34 / 4.22 ms | 4.07 / 5.56 ms |
| Insert 10,000 rows | 40.5 ms | 79.0 ms |
| Read/compare 10,000 rows | 6.9 ms | 48.1 ms |
| 1,000 indexed lookups | 8.3 ms | 9.0 ms |
| Encrypt / verify-decrypt 20 evidence files | 92.1 / 19.3 ms | 106.0 / 20.9 ms |
| Checkpointed database size | 1,096 KiB | 1,924 KiB |
| Sensitive marker hits (each scan) | 0 | 0 |
| Internal vendor marker hits | 0 | 10,005 |
| Plain SQLite header | Absent | Present |
| Reopen with key | 10,000 rows | 10,000 rows |
| Read without key | Refused: file is not a database | Schema and 10,000-row count readable; protected columns remain ciphertext |
| Credential deletion | Succeeded | Succeeded |

The first SQLCipher build plus probe took 1,250.689 seconds on this machine (about 21 minutes). It emitted MSVC LNK4099 warnings about the vendored OpenSSL debug PDB; the executable linked and ran. Release-profile Clippy with warnings denied passed for both feature choices. The initial capture wrapper failed while displaying Unicode compiler output in the Windows legacy console encoding **after** writing the successful probe result; the wrapper now uses UTF-8, and the final capture passed. Do not interpret a successful probe as a warning-free installer build.

Executable sizes and hashes are retained in the runtime evidence. These are spike binaries, not product or installer size estimates.

## Recommendation and limits

Recommend **Option A plus authenticated evidence files**, subject to owner review of [ADR-0008](../../adr/0008-encryption-at-rest.md). Metadata remained protected without maintaining a sensitive-column list. Keep the production credential, storage and backup APIs explicit and default-deny. Product encryption remains unimplemented (NFR-017 / LL-027 / TC-112).

The production suite still needs corruption/wrong-key tests for SQLCipher, secret-safe diagnostics, encrypted migration backups and recovery, key-loss UX, credential restrictions, atomic evidence writes, extension lockdown, key separation, memory handling and complete plaintext scans. macOS compilation/Keychain and on-device checks are deferred.

## Reproduce

```powershell
# Point to a native Windows Perl, not Git's minimal Perl.
$env:OPENSSL_SRC_PERL = 'C:/Strawberry/perl/bin/perl.exe'
.venv/Scripts/python.exe spikes/capture.py --output docs/development/spikes/evidence/ll010-a-windows.json -- cargo run --release --locked --manifest-path spikes/encryption/Cargo.toml --features option-a-sqlcipher
.venv/Scripts/python.exe spikes/capture.py --output docs/development/spikes/evidence/ll010-b-windows.json -- cargo run --release --locked --manifest-path spikes/encryption/Cargo.toml --features option-b-app-level
```

The report uses the prebuilt SQLCipher binary for the final runtime sample; its first-build artifact records the Cargo command and compiler output. Both feature choices are blocking Windows CI jobs. The CI result is tracked separately from this local evidence.
