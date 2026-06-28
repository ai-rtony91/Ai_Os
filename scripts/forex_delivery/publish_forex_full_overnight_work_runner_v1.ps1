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
    throw "PUBLISH_REQUIRES_MAIN_BRANCH"
}

$status = git status --short
$invalid = @()
foreach ($line in $status) {
    if (-not $line) { continue }
    $trimmed = $line.ToString().Trim()
    if ($trimmed.Length -lt 4) {
        continue
    }
    $path = $trimmed.Substring(3).Trim()
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

& "$PSScriptRoot/validate_forex_full_overnight_work_runner_v1.ps1"
if ($LASTEXITCODE -ne 0) {
    throw "VALIDATOR_FAILED"
}

git add -- $AllowedPaths
$staged = git diff --cached --name-only
foreach ($path in $staged) {
    if ($AllowedPaths -notcontains $path) {
        throw "STAGED_SCOPE_VIOLATION: $path"
    }
}
if (-not $staged) {
    throw "NO_FILES_STAGED_FOR_PUBLISH"
}

$branchName = "lane/forex-full-overnight-work-runner-end-to-end-continuation-system-v1"
git checkout -B $branchName
git commit -m "feat(forex): add full overnight work runner" | Out-Null
git push -u origin $branchName

$prUrl = gh pr create --title "feat: add full overnight work runner" --body "Add full overnight runner module, host orchestration, validator, publish script, and report artifacts." --base "main" --head $branchName
if ([string]::IsNullOrWhiteSpace($prUrl)) {
    throw "PR_CREATE_FAILED"
}

gh pr checks --watch $prUrl
if ($LASTEXITCODE -ne 0) {
    throw "PR_CHECKS_FAILED"
}

gh pr merge --squash $prUrl
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
