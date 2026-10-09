# LL-011: Windows worker lifecycle and checksum evidence

Date: 2026-10-10 (Asia/Manila). [Raw evidence](evidence/ll011-windows.json), [test harness](../../../spikes/child-process/tests/lifecycle.rs), [framing tests](../../../spikes/child-process/src/lib.rs).

MSI MS-7A70, Intel Core i5-7500, 16 GB RAM, Windows 10 Pro 19045, x64; Rust 1.99.0, Tokio 1.53.2, process-wrap 10.0.1, sysinfo 0.37.2. Release profile, synthetic worker/grandchild, no AI model or user documents. The run overlapped other development work. macOS is deferred.

## Results

One framing unit test and nine lifecycle tests passed. Oversized frames, truncated length prefixes and invalid UTF-8 are refused; writes enforce the same size cap, and the supervisor also caps response allocation.

| Case | Sample size | Median | p95 | Finding |
|---|---|---|---|---|
| Spawn to first worker frame | 20 | 134.8 ms | 280.6 ms | Worker starts and answers |
| Abrupt supervisor kill to worker/grandchild gone | 20 | 59.7 ms | 111.7 ms | Neither process survives |
| Normal supervisor exit to descendants gone | 10 | 27.9 ms | 61.3 ms | Neither process survives |

Additional cases passed: hung worker timeout/kill; a stuck parser under both safeguards; watchdog-only cleanup; job-only cleanup on Windows (now asserted); crash detection; modified worker binary refused with exit code 3 before spawning. The no-safeguard negative control deliberately survived for 10 seconds and was then cleaned up by the test.

A [final validation run](evidence/ll011-validation-windows.json) also passed all ten tests after bounding supervisor sends and making the tampered-binary fixture process-specific with create-new semantics. The earlier table remains the first measured sample; the final run is additional evidence, not an isolated performance comparison.

## Recommendation

Use the Tokio process-wrap frontend with a Windows job object and `KillOnDrop`, plus a dedicated stdin reader that terminates the worker on parent EOF even when parsing hangs. The spike found that the std frontend does not provide the same kill-on-job-close behavior; do not assume that owning a child handle alone provides containment. Verify SHA-256 before spawn and verify the authorized executable/handle again in production. Bound request and response lengths and treat partial frames as protocol errors.

This tests process mechanics with a synthetic worker. It does not establish installer sidecar placement, binary signing, privilege restrictions, a parser sandbox, model supervision, or a bundled document worker. These remain adapter/installer work in M1.2/M1.5/M1.6. NFR-018 remains In Progress because product assets are not yet implemented.

## Reproduce

```powershell
.venv/Scripts/python.exe spikes/capture.py --output docs/development/spikes/evidence/ll011-windows.json -- cargo test --release --locked --manifest-path spikes/child-process/Cargo.toml -- --nocapture --test-threads=1
```
