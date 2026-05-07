$ErrorActionPreference = "Stop"

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$RequiredFiles = @(
    "docs\AI_OS\signal_intelligence\AIOS_SIGNAL_INTELLIGENCE_SOURCE_OF_TRUTH.md",
    "docs\AI_OS\signal_intelligence\AIOS_CONFLUENCE_SCORING_MODEL_DRAFT.md",
    "docs\AI_OS\signal_intelligence\AIOS_MARKET_REGIME_ANALYSIS_DRAFT.md",
    "docs\AI_OS\signal_intelligence\AIOS_SIGNAL_VALIDATION_RULES_DRAFT.md",
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

Write-Host "AI_OS Signal Intelligence Readiness DRY_RUN"
$Results | Format-Table -AutoSize

if ($Missing) {
    Write-Host "Result: FAIL"
    exit 1
}

Write-Host "Result: PASS"
exit 0
