$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$RequiredFiles = @(
  "docs\AI_OS\signal_intelligence\AIOS_SIGNAL_INPUT_SCHEMA_DRAFT.md",
  "docs\AI_OS\signal_intelligence\AIOS_SIGNAL_CONFIDENCE_SCORE_DRAFT.md",
  "docs\AI_OS\signal_intelligence\AIOS_SIGNAL_LIFECYCLE_STATES_DRAFT.md",
  "docs\AI_OS\signal_intelligence\AIOS_SIGNAL_REJECTION_REASONS_DRAFT.md",
  "docs\AI_OS\signal_intelligence\AIOS_PAPER_TRADING_SIGNAL_QUEUE_DRAFT.md"
)
$Results = foreach ($RelativePath in $RequiredFiles) {
  $FullPath = Join-Path $RepoRoot $RelativePath
  [PSCustomObject]@{ Path = $RelativePath; Exists = Test-Path -LiteralPath $FullPath -PathType Leaf }
}
$Missing = $Results | Where-Object { -not $_.Exists }
Write-Host "AI_OS Signal Pipeline Readiness DRY_RUN"
$Results | Format-Table -AutoSize
if ($Missing) { Write-Host "Result: FAIL"; exit 1 }
Write-Host "Result: PASS"
exit 0
