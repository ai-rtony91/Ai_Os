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
    throw "PUBLISH_REQUIRES_MAIN_BRANCH"
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

& "$PSScriptRoot/validate_forex_flow1_active_execution_authority_runtime_sos_profit_countdown_v2.ps1"
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

$branchName = "lane/forex-flow1-active-execution-authority-runtime-sos-profit-countdown-v2"
git checkout -B $branchName
git commit -m "feat(forex): add flow1 active execution authority runtime sos profit countdown" | Out-Null
git push -u origin $branchName

gh pr create --title "Add Flow 1 active execution authority runtime SOS profit countdown" `
    --body "Flow 1 active execution authority packet with capacity engine, countdown gates, bridge map, validator and publish artifacts." `
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

$finalStatus = git status --short
if ($finalStatus) {
    throw "POST_PUBLISH_DIRTY"
}

Write-Output "PUBLISH_COMPLETE_CLEAN"
