Set-Location -LiteralPath "C:/Dev/Ai.Os"
$ErrorActionPreference = "Stop"

$AllowedPaths = @(
  "automation/forex_engine/forex_full_overnight_work_runner_v1.py"
  "scripts/forex_delivery/run_forex_full_overnight_work_runner_v1.py"
  "scripts/forex_delivery/validate_forex_full_overnight_work_runner_v1.ps1"
  "scripts/forex_delivery/publish_forex_full_overnight_work_runner_v1.ps1"
  "scripts/forex_delivery/Invoke-ForexFullOvernightWorkRunner.V1.ps1"
  "docs/governance/programs/contracts/AIOS_FOREX_FULL_OVERNIGHT_WORK_RUNNER_V1.md"
  "Reports/forex_delivery/AIOS_FOREX_FULL_OVERNIGHT_WORK_RUNNER_V1.json"
  "Reports/forex_delivery/AIOS_FOREX_FULL_OVERNIGHT_WORK_RUNNER_V1_REPORT.md"
  "Reports/forex_delivery/AIOS_FOREX_FULL_OVERNIGHT_WORK_RUNNER_NEXT_ACTION_QUEUE_V1.md"
  "Reports/forex_delivery/AIOS_FOREX_FULL_OVERNIGHT_WORK_RUNNER_CHECKPOINT_V1.md"
  "Reports/forex_delivery/AIOS_FOREX_FULL_OVERNIGHT_WORK_RUNNER_ACTIVE_PACKET_QUEUE_V1.md"
  "Reports/forex_delivery/AIOS_FOREX_FULL_OVERNIGHT_WORK_RUNNER_EXTERNAL_GATE_STOP_V1.md"
  "Reports/forex_delivery/AIOS_FOREX_FULL_OVERNIGHT_WORK_RUNNER_OWNER_HANDOFF_V1.md"
  "Reports/forex_delivery/AIOS_FOREX_FULL_OVERNIGHT_WORK_RUNNER_NEXT_CODEX_PROMPT_V1.md"
  "tests/forex_engine/test_forex_full_overnight_work_runner_v1.py"
)

$branch = git branch --show-current
if ($branch -ne "main") {
    throw "VALIDATION_REQUIRES_MAIN_BRANCH"
}

$invalid = @()
$statusLines = git status --short
foreach ($line in $statusLines) {
    if (-not $line) { continue }
    $trimmed = $line.ToString().Trim()
    if ($trimmed.Length -lt 4) {
        continue
    }
    $path = $line.ToString().Substring(3).Trim()
    if ([string]::IsNullOrWhiteSpace($path)) {
        continue
    }
    if ($path.EndsWith("/")) {
        continue
    }
    if ($path -like "*->*") {
        $path = $path.Split("->")[-1].Trim()
    }
    if ($AllowedPaths -notcontains $path) {
        $invalid += $path
    }
}
if ($invalid.Count -gt 0) {
    throw "DIRTY_SCOPE_VIOLATION: $($invalid -join ', ')"
}

python scripts/forex_delivery/run_forex_full_overnight_work_runner_v1.py
if ($LASTEXITCODE -ne 0) {
    throw "RUNNER_FAILED"
}

python -m pytest tests/forex_engine/test_forex_full_overnight_work_runner_v1.py -q
if ($LASTEXITCODE -ne 0) {
    throw "PYTEST_FAILED"
}

git diff --check -- $AllowedPaths
if ($LASTEXITCODE -ne 0) {
    throw "GIT_DIFF_CHECK_FAILED"
}

$json = Get-Content "Reports/forex_delivery/AIOS_FOREX_FULL_OVERNIGHT_WORK_RUNNER_V1.json" -Raw | ConvertFrom-Json
$requiredFields = @(
    "runner_status",
    "runner_mode",
    "active_anchor",
    "next_packet_id",
    "next_required_flow",
    "overnight_loop_status",
    "active_anchor_map",
    "checkpoint"
)
foreach ($field in $requiredFields) {
    if (-not ($json.PSObject.Properties.Name -contains $field)) {
        throw "JSON_REQUIRED_FIELD_MISSING: $field"
    }
}

Write-Output "VALIDATION_PASSED"
