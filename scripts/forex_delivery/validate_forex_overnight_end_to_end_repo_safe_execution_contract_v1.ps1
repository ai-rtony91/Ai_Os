Set-Location -Path "C:/Dev/Ai.Os"
$ErrorActionPreference = "Stop"

$allowedPaths = @(
  "docs/governance/programs/contracts/AIOS_FOREX_OVERNIGHT_END_TO_END_REPO_SAFE_EXECUTION_CONTRACT_V1.md",
  "docs/governance/programs/flows/FLOW-FOREX-002-SUPERVISED-DEMO-EVIDENCE-COUNTDOWN-CAPTURE-V1.md",
  "docs/governance/programs/flows/FLOW-FOREX-003-PROFIT-LOOP-LIVE-WEEK-VACATION-GATE-V1.md",
  "docs/governance/programs/flows/FLOW-FOREX-004-LIVE-EXCEPTION-AND-REAL-MONEY-GATE-V1.md",
  "automation/forex_engine/forex_overnight_end_to_end_repo_safe_execution_contract_v1.py",
  "scripts/forex_delivery/run_forex_overnight_end_to_end_repo_safe_execution_contract_v1.py",
  "scripts/forex_delivery/validate_forex_overnight_end_to_end_repo_safe_execution_contract_v1.ps1",
  "scripts/forex_delivery/publish_forex_overnight_end_to_end_repo_safe_execution_contract_v1.ps1",
  "Reports/forex_delivery/AIOS_FOREX_OVERNIGHT_END_TO_END_REPO_SAFE_EXECUTION_CONTRACT_V1.json",
  "Reports/forex_delivery/AIOS_FOREX_OVERNIGHT_END_TO_END_REPO_SAFE_EXECUTION_CONTRACT_V1_REPORT.md",
  "Reports/forex_delivery/AIOS_FOREX_OVERNIGHT_END_TO_END_REPO_SAFE_EXECUTION_NEXT_ACTION_QUEUE_V1.md",
  "Reports/forex_delivery/AIOS_FOREX_OVERNIGHT_END_TO_END_REPO_SAFE_EXECUTION_CONTINUATION_LEDGER_V1.md",
  "Reports/forex_delivery/AIOS_FOREX_EXTERNAL_GATE_BRIDGE_REGISTRY_V1.md",
  "Reports/forex_delivery/AIOS_FOREX_FLOW2_SUPERVISED_DEMO_EVIDENCE_CAPTURE_CONTRACT_V1.md",
  "Reports/forex_delivery/AIOS_FOREX_FLOW3_PROFIT_LOOP_LIVE_WEEK_VACATION_GATE_CONTRACT_V1.md",
  "Reports/forex_delivery/AIOS_FOREX_LIVE_EXCEPTION_REAL_MONEY_GATE_CONTRACT_V1.md",
  "Reports/forex_delivery/AIOS_FOREX_NEXT_CODEX_PACKET_FLOW2_IMPLEMENTATION_V1.md",
  "Reports/forex_delivery/AIOS_FOREX_NEXT_CODEX_PACKET_FLOW3_IMPLEMENTATION_V1.md",
  "Reports/forex_delivery/AIOS_FOREX_NEXT_CODEX_PACKET_LIVE_EXCEPTION_GATE_V1.md",
  "tests/forex_engine/test_forex_overnight_end_to_end_repo_safe_execution_contract_v1.py"
)

$branch = git branch --show-current
if ($branch -ne "main") {
    throw "VALIDATION_REQUIRES_MAIN_BRANCH"
}

$status = git status --short
$invalid = @()
foreach ($line in $status) {
    if (-not $line) { continue }
    $parts = $line -split "\s+", 2
    if ($parts.Count -lt 2) { continue }
    $path = $parts[1].Trim()
    if ($path.EndsWith("/")) { continue }
    if ($allowedPaths -notcontains $path) {
        $invalid += $path
    }
}
if ($invalid.Count -gt 0) {
    throw "DIRTY_SCOPE_VIOLATION: $($invalid -join ', ')"
}

python scripts/forex_delivery/run_forex_overnight_end_to_end_repo_safe_execution_contract_v1.py
if ($LASTEXITCODE -ne 0) {
    throw "RUNNER_FAILED"
}

python -m pytest tests/forex_engine/test_forex_overnight_end_to_end_repo_safe_execution_contract_v1.py -q
if ($LASTEXITCODE -ne 0) {
    throw "PYTEST_FAILED"
}

git diff --check -- $allowedPaths
if ($LASTEXITCODE -ne 0) {
    throw "GIT_DIFF_CHECK_FAILED"
}

$json = Get-Content "Reports/forex_delivery/AIOS_FOREX_OVERNIGHT_END_TO_END_REPO_SAFE_EXECUTION_CONTRACT_V1.json" -Raw | ConvertFrom-Json
$requiredFields = @(
    "overnight_contract_status",
    "overnight_contract_mode",
    "anchor_status",
    "target_return_band",
    "runtime_objective",
    "flow2_contract_status",
    "flow3_contract_status",
    "live_exception_contract_status",
    "next_required_flow"
)
foreach ($field in $requiredFields) {
    if (-not ($json.PSObject.Properties.Name -contains $field)) {
        throw "JSON_REQUIRED_FIELD_MISSING: $field"
    }
}

Write-Output "VALIDATION_PASSED"
