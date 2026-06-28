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
    throw "PUBLISH_REQUIRES_MAIN_BRANCH"
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

& "$PSScriptRoot/validate_forex_overnight_end_to_end_repo_safe_execution_contract_v1.ps1"
if ($LASTEXITCODE -ne 0) {
    throw "VALIDATOR_FAILED"
}

git add -- $allowedPaths
$staged = git diff --cached --name-only
foreach ($path in $staged) {
    if ($allowedPaths -notcontains $path) {
        throw "STAGED_SCOPE_VIOLATION: $path"
    }
}

$branchName = "lane/forex-overnight-end-to-end-repo-safe-execution-contract-v1"
git checkout -B $branchName
git commit -m "feat(forex): add overnight end-to-end repo-safe execution contract" | Out-Null
git push -u origin $branchName

gh pr create --title "Add overnight end-to-end repo-safe execution contract" `
    --body "Overnight end-to-end repo-safe execution contract for Flow 2 and Flow 3 progression." `
    --base "main" --head $branchName

gh pr checks --watch
if ($LASTEXITCODE -ne 0) {
    throw "PR_CHECKS_FAILED"
}

gh pr merge --squash
if ($LASTEXITCODE -ne 0) {
    throw "PR_MERGE_FAILED"
}

git checkout main
git fetch origin
git reset --hard origin/main
if (git status --short) {
    throw "POST_PUBLISH_DIRTY"
}

Write-Output "PUBLISH_COMPLETE_CLEAN"
