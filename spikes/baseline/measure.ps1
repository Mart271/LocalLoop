# LL-013 / TC-108 groundwork: measure the Windows foundation shell, without an AI model.
# This is not the MVP model-free workflow or an 8 GB reference-machine acceptance test.
param(
    [string]$Executable = "target/debug/localloop.exe",
    [string]$Output = "docs/development/spikes/evidence/windows-baseline.json",
    [int]$Runs = 5,
    [int]$SampleSeconds = 10,
    [int]$DebugPort = 0
)
$ErrorActionPreference = "Stop"
$binaryPath = (Resolve-Path -LiteralPath $Executable).Path
$env:LOCALLOOP_STRICT_OFFLINE = "1"
if ($DebugPort -gt 0) {
    # Development-only WebView2 inspection; never configured in product code.
    $env:WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS = "--remote-debugging-port=$DebugPort --remote-debugging-address=127.0.0.1"
}
$samples = @()
for ($index = 0; $index -lt $Runs; $index++) {
    # A unique WebView profile prevents another test instance from sharing the browser process.
    $env:WEBVIEW2_USER_DATA_FOLDER = Join-Path (Get-Location) (".localloop-dev/webview/" + [Guid]::NewGuid().ToString())
    $timer = [System.Diagnostics.Stopwatch]::StartNew()
    $appProcess = Start-Process -FilePath $binaryPath -PassThru -WindowStyle Hidden
    $childIds = @()
    try {
        do {
            Start-Sleep -Milliseconds 50
            $appProcess.Refresh()
            if ($appProcess.HasExited) { throw "LocalLoop exited before creating its window (code $($appProcess.ExitCode))" }
        } while ($appProcess.MainWindowHandle -eq 0 -and $timer.Elapsed.TotalSeconds -lt 30)
        if ($appProcess.MainWindowHandle -eq 0) { throw "No LocalLoop window within 30 seconds" }
        $windowMs = $timer.Elapsed.TotalMilliseconds
        $peakBytes = [long]0
        $peakProcessCount = 0
        $sampling = [System.Diagnostics.Stopwatch]::StartNew()
        while ($sampling.Elapsed.TotalSeconds -lt $SampleSeconds) {
            $appProcess.Refresh()
            if ($appProcess.HasExited) { throw "LocalLoop exited while sampling (code $($appProcess.ExitCode))" }
            $allProcesses = @(Get-CimInstance Win32_Process)
            $treeIds = @($appProcess.Id)
            do {
                $newIds = @($allProcesses | Where-Object { $_.ParentProcessId -in $treeIds -and $_.ProcessId -notin $treeIds } | ForEach-Object { [int]$_.ProcessId })
                $treeIds += $newIds
            } while ($newIds.Count -gt 0)
            $childIds = @($treeIds | Where-Object { $_ -ne $appProcess.Id })
            $bytes = [long]0
            foreach ($processId in $treeIds) {
                $member = Get-Process -Id $processId -ErrorAction SilentlyContinue
                if ($null -ne $member) { $bytes += $member.WorkingSet64 }
            }
            $peakBytes = [Math]::Max($peakBytes, $bytes)
            $peakProcessCount = [Math]::Max($peakProcessCount, $treeIds.Count)
            Start-Sleep -Milliseconds 100
        }
        if ($peakBytes -le 0) { throw "No process memory samples were collected" }
        $samples += [ordered]@{run=$index + 1;window_ms=[Math]::Round($windowMs,2);sampled_tree_peak_working_set_bytes=$peakBytes;process_count=$peakProcessCount;window_title=$appProcess.MainWindowTitle}
    } finally {
        # Close only the application started by this script; never enumerate unrelated WebViews.
        $appProcess.Refresh()
        if (-not $appProcess.HasExited) {
            $null = $appProcess.CloseMainWindow()
            if (-not $appProcess.WaitForExit(5000)) { $appProcess.Kill(); $appProcess.WaitForExit() }
        }
    }
    Write-Output "BASELINE run=$($index + 1) window_ms=$($samples[-1].window_ms) tree_mib=$([Math]::Round($samples[-1].sampled_tree_peak_working_set_bytes/1MB,2))"
}
$computer = Get-CimInstance Win32_ComputerSystem
$operatingSystem = Get-CimInstance Win32_OperatingSystem
$processor = Get-CimInstance Win32_Processor
$report = [ordered]@{
    recorded_at_utc=[DateTime]::UtcNow.ToString("o")
    hardware=@{manufacturer=$computer.Manufacturer;model=$computer.Model;cpu=$processor.Name;ram_bytes=$computer.TotalPhysicalMemory;os=$operatingSystem.Caption;build=$operatingSystem.BuildNumber}
    rust=(rustc -V);node=(node --version);pnpm=(pnpm --version)
    binary_sha256=(Get-FileHash -LiteralPath $binaryPath -Algorithm SHA256).Hash.ToLowerInvariant()
    build_profile="debug";ai_model="none";strict_offline="1";reference_machine=$false
    method="Time to process window handle (may include the debug console), not first usable UI; aggregate sampled RSS of app plus descendants (shared pages counted per process); one sample per approximately 100 ms plus CIM overhead; unique WebView profile per run; background load uncontrolled. UI readiness is checked separately by windows-smoke.json"
    samples=$samples;macos="deferred by owner on 2026-10-10"
}
$outputPath = [System.IO.Path]::GetFullPath((Join-Path (Get-Location) $Output))
$null = New-Item -ItemType Directory -Force -Path (Split-Path -Parent $outputPath)
[System.IO.File]::WriteAllText($outputPath, (($report | ConvertTo-Json -Depth 8) + "`n"), [System.Text.UTF8Encoding]::new($false))
