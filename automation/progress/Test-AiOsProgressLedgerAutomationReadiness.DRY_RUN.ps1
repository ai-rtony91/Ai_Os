$ErrorActionPreference = "Stop"

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$RequiredFiles = @(
    "docs\AI_OS\progress\AIOS_PROGRESS_LEDGER_APPEND_RULES_DRAFT.md",
    "docs\AI_OS\progress\AIOS_PROGRESS_LEDGER_DASHBOARD_HANDOFF_DRAFT.md",
    "automation\progress\Update-AiOsProgressLedger.DRY_RUN.ps1",
    "automation\progress\New-AiOsProgressSnapshot.DRY_RUN.ps1",
    "Reports\progress\AIOS_PROGRESS_LEDGER_TEMPLATE.csv"
)

$Results = foreach ($RelativePath in $RequiredFiles) {
    $FullPath = Join-Path $RepoRoot $RelativePath
    [PSCustomObject]@{
        Path = $RelativePath
        Exists = Test-Path -LiteralPath $FullPath -PathType Leaf
    }
}

$Missing = $Results | Where-Object { -not $_.Exists }

Write-Host "AI_OS Progress Ledger Automation Readiness DRY_RUN"
$Results | Format-Table -AutoSize

if ($Missing) {
    Write-Host "Result: FAIL"
    exit 1
}

Write-Host "Result: PASS"
exit 0
