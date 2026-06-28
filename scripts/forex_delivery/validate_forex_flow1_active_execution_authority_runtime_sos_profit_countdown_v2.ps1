Set-Location -Path "C:/Dev/Ai.Os"
$ErrorActionPreference = "Stop"

$allowedPaths = @(
  "docs/governance/programs/flows/FLOW-FOREX-001-ACTIVE-EXECUTION-AUTHORITY-RUNTIME-SOS-PROFIT-COUNTDOWN-V2.md",
  "automation/forex_engine/forex_flow1_active_execution_authority_runtime_sos_profit_countdown_v2.py",
  "scripts/forex_delivery/run_forex_flow1_active_execution_authority_runtime_sos_profit_countdown_v2.py",
  "scripts/forex_delivery/validate_forex_flow1_active_execution_authority_runtime_sos_profit_countdown_v2.ps1",
  "scripts/forex_delivery/publish_forex_flow1_active_execution_authority_runtime_sos_profit_countdown_v2.ps1",
  "Reports/forex_delivery/AIOS_FOREX_FLOW1_ACTIVE_EXECUTION_AUTHORITY_RUNTIME_SOS_PROFIT_COUNTDOWN_V2.json",
  "Reports/forex_delivery/AIOS_FOREX_FLOW1_ACTIVE_EXECUTION_AUTHORITY_RUNTIME_SOS_PROFIT_COUNTDOWN_V2_REPORT.md",
  "Reports/forex_delivery/AIOS_FOREX_FLOW1_ACTIVE_EXECUTION_AUTHORITY_RUNTIME_SOS_PROFIT_COUNTDOWN_NEXT_ACTION_QUEUE_V2.md",
  "Reports/forex_delivery/AIOS_FOREX_FLOW1_TO_FLOW2_ACTIVE_SUPERVISED_DEMO_EVIDENCE_HANDOFF_V2.md",
  "tests/forex_engine/test_forex_flow1_active_execution_authority_runtime_sos_profit_countdown_v2.py"
)

$branch = git branch --show-current
if ($branch -ne "main") {
    throw "VALIDATION_REQUIRES_MAIN_BRANCH"
}

$status = git status --short
$invalid = @()
foreach ($line in $status) {
    $parts = $line -split "\s+"
    if ($parts.Count -lt 2) { continue }
    $path = $parts[-1]
    if ($path.EndsWith("/")) { continue }
    if ($parts -contains "->") {
        $path = $parts[-1]
    }
    if ($allowedPaths -notcontains $path) {
        $invalid += $path
    }
}
if ($invalid.Count -gt 0) {
    throw "DIRTY_SCOPE_VIOLATION: $($invalid -join ', ')"
}

python scripts/forex_delivery/run_forex_flow1_active_execution_authority_runtime_sos_profit_countdown_v2.py
if ($LASTEXITCODE -ne 0) {
    throw "RUNNER_FAILED"
}

python -m pytest tests/forex_engine/test_forex_flow1_active_execution_authority_runtime_sos_profit_countdown_v2.py -q
if ($LASTEXITCODE -ne 0) {
    throw "PYTEST_FAILED"
}

git diff --check -- $allowedPaths
if ($LASTEXITCODE -ne 0) {
    throw "GIT_DIFF_CHECK_FAILED"
}

$json = Get-Content "Reports/forex_delivery/AIOS_FOREX_FLOW1_ACTIVE_EXECUTION_AUTHORITY_RUNTIME_SOS_PROFIT_COUNTDOWN_V2.json" -Raw | ConvertFrom-Json
$requiredFields = @(
    "flow1_status",
    "flow1_mode",
    "owner_live_capital_intent_usd",
    "requested_max_open_positions",
    "requested_quantity_scale",
    "final_position_capacity",
    "position_capacity_status",
    "target_return_band",
    "target_return_claim_status",
    "profit_return_countdown_status",
    "runtime_objective",
    "runtime_status",
    "vacation_mode_status",
    "sos_alert_integration_status",
    "flow2_handoff_status",
    "next_required_flow"
)
foreach ($field in $requiredFields) {
    if (-not ($json.PSObject.Properties.Name -contains $field)) {
        throw "JSON_REQUIRED_FIELD_MISSING: $field"
    }
}

Write-Output "VALIDATION_PASSED"
