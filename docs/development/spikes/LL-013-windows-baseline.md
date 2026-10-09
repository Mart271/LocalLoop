# LL-013: Windows foundation shell baseline

Date: 2026-10-10 (Asia/Manila). [Process samples](evidence/windows-baseline.json), [actual WebView evidence](evidence/windows-smoke.json), [measurement harness](../../../spikes/baseline/measure.ps1), [smoke harness](../../../spikes/baseline/smoke.mjs).

## Environment and scope

Observed hardware: MSI MS-7A70, Intel Core i5-7500 at 3.40 GHz, 17,104,429,056 physical RAM bytes (approximately 16 GB), Windows 10 Pro build 19045, x64. Rust 1.99.0, Node 24.11.1, pnpm 12.10.1, Python 3.12.10. Tauri 2.12.2, React 19.3.0; the local C++ toolchain is Visual Studio 2022. No AI model or quantization. This is a **foundation shell**, not the MVP document workflow. Fixture seed 20261009 applies to the related studies; the shell baseline uses no documents.

The earlier progress log named an ASUS i5-12500H / Windows 11 laptop and different tool versions. Those values are not evidence for this session. The measured machine is not an 8 GB reference machine. macOS and reference-machine acceptance remain pending; no capability level or release memory budget is established here (NFR-008).

## Build and real UI check

Build with `pnpm --filter desktop tauri build --debug --no-bundle`, which embeds local assets. A plain `cargo build` expects Vite at the dev URL and cannot establish a standalone offline launch. CI now also builds with `tauri/custom-protocol`.

The real WebView2 displayed **Connected (version 0.1.0)**, and clicking **Check again** returned to Connected. The strict-CSP isolation frame was hidden using bundled CSS. A screenshot was visually inspected; no page errors were reported. The smoke test uses a temporary loopback debugging port and a fresh WebView profile, confined to the test environment. This does not enable product network access or developer tooling in shipped configuration.

The one measured readiness sample was 13,246 ms, including debugger polling and background build contention. It is not a responsiveness target or an isolated startup benchmark. The raw smoke artifact records its method; do not compare it directly with the process-window timing below.

## Process samples

Five debug embedded-assets launches, ten seconds of sampling per launch, fresh WebView profile each time. Background activity was uncontrolled. The approximately 100 ms interval also incurs CIM polling overhead. Aggregate working set counts shared pages once per process; it is not unique physical memory, committed bytes or an unsampled lifetime peak.

| Run | Process-window handle time | Sampled peak app-tree working set |
|---|---|---|
| 1 | 635.52 ms | 396.15 MiB |
| 2 | 185.19 ms | 398.13 MiB |
| 3 | 156.25 ms | 401.14 MiB |
| 4 | 180.05 ms | 404.30 MiB |
| 5 | 300.69 ms | 492.30 MiB |

The process-window handle can include the debug console and is **not first usable UI**. Only the separate real WebView test establishes that the shell content loaded and ping worked. The sampler fails if the application exits or no memory samples are collected. Earlier runs that shared WebView profiles or loaded a development error page were discarded and are not the published baseline.

## Reproduce and follow-up

```powershell
pnpm --filter desktop tauri build --debug --no-bundle
# Install the isolated Mermaid/Puppeteer tooling prefix described in SETUP.md.
node spikes/baseline/smoke.mjs
powershell -NoProfile -ExecutionPolicy Bypass -File spikes/baseline/measure.ps1
```

Run these sequentially; do not rebuild the executable during measurement. M1.6 still needs release-build measurements, controlled background load, Windows 8 GB reference hardware, full model-free workflow runs, and the offline network-capture acceptance suite. macOS remains deferred under ADR-0010. Windows 10 execution is evidence of this development run, not resolution of the longer-term support decision D-08.
