param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("PHASE_0","PHASE_1")]
    [string]$Phase
)

$ErrorActionPreference = "Stop"

$root = Resolve-Path .
$reportsDir = Join-Path $root "Reports/forex_delivery"
$stateFile = Join-Path $root "automation/forex_engine/campaign_state.json"

function Write-State($phase, $status) {
    $state = @{
        phase = $phase
        status = $status
        timestamp = (Get-Date).ToString("o")
    } | ConvertTo-Json -Depth 5
    Set-Content -Path $stateFile -Value $state -Encoding UTF8
}

function Require-File($path) {
    if (!(Test-Path $path)) {
        throw "REQUIRED_ARTIFACT_MISSING: $path"
    }
}

if ($Phase -eq "PHASE_0") {
    Write-Host "[AIOS] PHASE 0 START"
    Write-State "PHASE_0" "RUNNING"

    pwsh -c "python automation/forex_engine/phase0_gap_audit.py"

    $report = Join-Path $reportsDir "AIOS_FOREX_PHASE0_GAP_AUDIT_V1.md"
    Require-File $report

    Write-State "PHASE_0" "COMPLETED"
    Write-Host "[AIOS] PHASE 0 COMPLETE — STOP"
    exit 0
}

if ($Phase -eq "PHASE_1") {
    Write-Host "[AIOS] PHASE 1 START"
    Write-State "PHASE_1" "RUNNING"

    pwsh -c "pytest tests/forex_engine/ -q"
    if ($LASTEXITCODE -ne 0) {
        throw "TEST_FAILURE_DETECTED"
    }

    Write-State "PHASE_1" "COMPLETED"
    Write-Host "[AIOS] PHASE 1 COMPLETE — STOP"
    exit 0
}
