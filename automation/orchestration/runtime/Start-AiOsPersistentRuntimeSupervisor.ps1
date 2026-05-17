param(
    [int]$Cycles = 3,
    [int]$IntervalSeconds = 5,
    [switch]$Apply
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

$Mode = if ($Apply) { "APPLY" } else { "DRY_RUN" }
$AuditLogPath = Join-Path $PSScriptRoot "logs/supervisor_cycles.jsonl"
$AuditLogDirectory = Split-Path -Parent $AuditLogPath

if (-not (Test-Path -LiteralPath $AuditLogDirectory)) {
    New-Item -ItemType Directory -Path $AuditLogDirectory -Force | Out-Null
}

function Convert-AiOsExitCodeToAuditResult {
    param(
        [int]$ExitCode
    )

    if ($ExitCode -eq 0) {
        return "PASS"
    }

    return "FAIL_EXIT_CODE_$ExitCode"
}

function Write-AiOsSupervisorCycleAuditLog {
    param(
        [int]$Cycle,
        [string]$PathRegistryResult,
        [string]$SelfRouteResult,
        [string]$PacketAdvancementResult,
        [string]$Mode,
        [string]$Result,
        [AllowNull()][string]$Blocker
    )

    $auditRecord = [ordered]@{
        timestamp_utc = (Get-Date).ToUniversalTime().ToString("o")
        cycle = $Cycle
        path_registry_result = $PathRegistryResult
        self_route_result = $SelfRouteResult
        packet_advancement_result = $PacketAdvancementResult
        mode = $Mode
        result = $Result
        blocker = $Blocker
    }

    $auditRecord | ConvertTo-Json -Compress | Add-Content -LiteralPath $AuditLogPath -Encoding UTF8
}

Write-Host "AIOS Persistent Runtime Supervisor"
Write-Host "Mode: $Mode"
Write-Host "Cycles: $Cycles"
Write-Host ""

for ($i = 1; $i -le $Cycles; $i++) {
    $pathRegistryResult = "NOT_RUN"
    $selfRouteResult = "NOT_RUN"
    $packetAdvancementResult = "NOT_RUN"
    $cycleResult = "PASS"
    $blocker = $null

    Write-Host "================================="
    Write-Host "RUNTIME CYCLE $i"
    Write-Host "================================="
    Write-Host ""

    powershell -ExecutionPolicy Bypass -File automation/runtime/path_registry/Test-AiOsPathRegistry.ps1
    $pathRegistryResult = Convert-AiOsExitCodeToAuditResult -ExitCode $LASTEXITCODE
    if ($LASTEXITCODE -ne 0) {
        $cycleResult = "BLOCKED"
        $blocker = "invalid path registry"
        Write-AiOsSupervisorCycleAuditLog `
            -Cycle $i `
            -PathRegistryResult $pathRegistryResult `
            -SelfRouteResult $selfRouteResult `
            -PacketAdvancementResult $packetAdvancementResult `
            -Mode $Mode `
            -Result $cycleResult `
            -Blocker $blocker
        Write-Host "Runtime halted due to invalid path registry."
        continue
    }

    powershell -ExecutionPolicy Bypass -File automation/orchestration/runtime/Invoke-AiOsRuntimeSelfRoute.ps1 -Apply
    $selfRouteResult = Convert-AiOsExitCodeToAuditResult -ExitCode $LASTEXITCODE
    if ($LASTEXITCODE -ne 0) {
        $cycleResult = "FAIL"
        $blocker = "self route failed"
    }

    if ($Apply) {
        powershell -ExecutionPolicy Bypass -File automation/orchestration/runtime/Invoke-AiOsRuntimePacketAdvancement.ps1 -Apply
    } else {
        powershell -ExecutionPolicy Bypass -File automation/orchestration/runtime/Invoke-AiOsRuntimePacketAdvancement.ps1
    }
    $packetAdvancementResult = Convert-AiOsExitCodeToAuditResult -ExitCode $LASTEXITCODE
    if ($LASTEXITCODE -ne 0) {
        $cycleResult = "FAIL"
        if (-not $blocker) {
            $blocker = "packet advancement failed"
        }
    }

    Write-AiOsSupervisorCycleAuditLog `
        -Cycle $i `
        -PathRegistryResult $pathRegistryResult `
        -SelfRouteResult $selfRouteResult `
        -PacketAdvancementResult $packetAdvancementResult `
        -Mode $Mode `
        -Result $cycleResult `
        -Blocker $blocker

    if ($i -lt $Cycles) {
        Write-Host ""
        Write-Host "Sleeping $IntervalSeconds seconds..."
        Start-Sleep -Seconds $IntervalSeconds
    }
}

Write-Host ""
Write-Host "Supervisor complete."
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
