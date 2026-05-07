$ErrorActionPreference = "Stop"

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$RequiredFiles = @(
    "docs\AI_OS\progress\AIOS_PROGRESS_LEDGER_SOURCE_OF_TRUTH.md",
    "docs\AI_OS\progress\AIOS_CODEX_PROGRESS_COUNTDOWN_STANDARD.md",
    "docs\AI_OS\progress\AIOS_WORKLOAD_PROGRESS_SCHEMA_DRAFT.md",
    "automation\progress\New-AiOsProgressSnapshot.DRY_RUN.ps1",
    "Reports\progress\AIOS_PROGRESS_LEDGER_TEMPLATE.csv"
)

$RequiredHeader = "date,time,stage,task_id,task_name,planned_steps,completed_steps,percent_complete,status,blocked,blocker,next_action,checkpoint_file,commit_hash,git_status,notes"

$Results = foreach ($RelativePath in $RequiredFiles) {
    $FullPath = Join-Path $RepoRoot $RelativePath
    [PSCustomObject]@{
        Path = $RelativePath
        Exists = Test-Path -LiteralPath $FullPath -PathType Leaf
    }
}

$Missing = $Results | Where-Object { -not $_.Exists }
$CsvPath = Join-Path $RepoRoot "Reports\progress\AIOS_PROGRESS_LEDGER_TEMPLATE.csv"
$CsvHeaderMatches = $false

if (Test-Path -LiteralPath $CsvPath -PathType Leaf) {
    $ActualHeader = Get-Content -LiteralPath $CsvPath -TotalCount 1
    $CsvHeaderMatches = $ActualHeader -eq $RequiredHeader
}

Write-Host "AI_OS Progress Ledger Readiness DRY_RUN"
$Results | Format-Table -AutoSize
Write-Host "CSV header matches required schema: $CsvHeaderMatches"

if ($Missing -or -not $CsvHeaderMatches) {
    Write-Host "Result: FAIL"
    exit 1
}

Write-Host "Result: PASS"
exit 0
