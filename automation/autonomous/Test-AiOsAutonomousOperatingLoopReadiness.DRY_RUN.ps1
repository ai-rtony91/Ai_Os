$ErrorActionPreference = "Stop"

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$RequiredFiles = @(
    "docs\AI_OS\autonomous\AIOS_OBSERVE_PLAN_REPORT_CYCLE_DRAFT.md",
    "docs\AI_OS\autonomous\AIOS_CHECKPOINT_DRIVEN_AUTONOMY_DRAFT.md",
    "docs\AI_OS\autonomous\AIOS_OPERATOR_APPROVAL_GATES_DRAFT.md",
    "docs\AI_OS\autonomous\AIOS_PROGRESS_LEDGER_INTEGRATION_DRAFT.md",
    "docs\AI_OS\autonomous\AIOS_STOP_CONDITIONS_ESCALATION_RULES_DRAFT.md"
)

$Results = foreach ($RelativePath in $RequiredFiles) {
    $FullPath = Join-Path $RepoRoot $RelativePath
    [PSCustomObject]@{
        Path = $RelativePath
        Exists = Test-Path -LiteralPath $FullPath -PathType Leaf
    }
}

$Missing = $Results | Where-Object { -not $_.Exists }

Write-Host "AI_OS Autonomous Operating Loop Readiness DRY_RUN"
$Results | Format-Table -AutoSize

if ($Missing) {
    Write-Host "Result: FAIL"
    exit 1
}

Write-Host "Result: PASS"
exit 0
