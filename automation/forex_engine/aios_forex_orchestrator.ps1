param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("PHASE_0","PHASE_1")]
    [string]$Phase
)

$ErrorActionPreference = "Stop"

function Fail-Hard($msg) {
    Write-Error $msg
    exit 1
}

function Assert-Path($path) {
    if (!(Test-Path $path)) {
        Fail-Hard "MISSING_PATH: $path"
    }
}

# Required base paths
$phase0Script = "automation/forex_engine/phase0_gap_audit.py"
$testsPath = "tests/forex_engine/"
$reportPath = "Reports/forex_delivery/AIOS_FOREX_PHASE0_GAP_AUDIT_V1.md"
$reportDir = "Reports/forex_delivery/"

Assert-Path "automation/forex_engine/"
Assert-Path $testsPath
Assert-Path $reportDir

if ($Phase -eq "PHASE_0") {
    Assert-Path $phase0Script

    Write-Host "RUNNING PHASE_0 AUDIT"
    python $phase0Script
    if ($LASTEXITCODE -ne 0) {
        Fail-Hard "PHASE_0_SCRIPT_FAILED"
    }

    if (!(Test-Path $reportPath)) {
        Fail-Hard "MISSING_ARTIFACT: $reportPath"
    }

    $state = @{ phase = "PHASE_0"; status = "COMPLETED" } | ConvertTo-Json -Depth 3
    $state | Out-File -FilePath "campaign_state.json" -Encoding utf8

    exit 0
}

if ($Phase -eq "PHASE_1") {
    Write-Host "RUNNING PHASE_1 TEST SUITE"

    python -m pytest $testsPath -q
    if ($LASTEXITCODE -ne 0) {
        Fail-Hard "TEST_FAILURE"
    }

    $state = @{ phase = "PHASE_1"; status = "COMPLETED" } | ConvertTo-Json -Depth 3
    $state | Out-File -FilePath "campaign_state.json" -Encoding utf8

    exit 0
}

Fail-Hard "INVALID_PHASE"