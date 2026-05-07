$ErrorActionPreference = "Stop"

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$RequiredFiles = @(
    "docs\AI_OS\backtesting\AIOS_BACKTEST_INGESTION_DRAFT.md",
    "docs\AI_OS\backtesting\AIOS_BACKTEST_IMPORT_RULES_DRAFT.md",
    "docs\AI_OS\strategy_registry\AIOS_STRATEGY_REGISTRY_SCHEMA_DRAFT.md"
)

$Results = foreach ($RelativePath in $RequiredFiles) {
    $FullPath = Join-Path $RepoRoot $RelativePath
    [PSCustomObject]@{
        Path = $RelativePath
        Exists = Test-Path -LiteralPath $FullPath -PathType Leaf
    }
}

$Missing = $Results | Where-Object { -not $_.Exists }

Write-Host "AI_OS Backtest Ingestion Readiness DRY_RUN"
$Results | Format-Table -AutoSize

if ($Missing) {
    Write-Host "Result: FAIL"
    exit 1
}

Write-Host "Result: PASS"
exit 0
