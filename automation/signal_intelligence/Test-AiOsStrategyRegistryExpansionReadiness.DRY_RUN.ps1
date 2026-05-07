$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$RequiredFiles = @(
  "docs\AI_OS\strategy_registry\AIOS_STRATEGY_VERSIONING_DRAFT.md",
  "docs\AI_OS\strategy_registry\AIOS_STRATEGY_APPROVAL_STATE_DRAFT.md",
  "docs\AI_OS\strategy_registry\AIOS_STRATEGY_EVIDENCE_REQUIREMENTS_DRAFT.md",
  "docs\AI_OS\strategy_registry\AIOS_BACKTEST_ATTACHMENT_RULES_DRAFT.md",
  "docs\AI_OS\strategy_registry\AIOS_INVALID_STRATEGY_HANDLING_DRAFT.md"
)
$Results = foreach ($RelativePath in $RequiredFiles) {
  $FullPath = Join-Path $RepoRoot $RelativePath
  [PSCustomObject]@{ Path = $RelativePath; Exists = Test-Path -LiteralPath $FullPath -PathType Leaf }
}
$Missing = $Results | Where-Object { -not $_.Exists }
Write-Host "AI_OS Strategy Registry Expansion Readiness DRY_RUN"
$Results | Format-Table -AutoSize
if ($Missing) { Write-Host "Result: FAIL"; exit 1 }
Write-Host "Result: PASS"
exit 0
