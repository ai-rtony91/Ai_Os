$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$RequiredFiles = @(
  "docs\AI_OS\risk_controls\AIOS_MAX_RISK_PLACEHOLDER_DRAFT.md",
  "docs\AI_OS\risk_controls\AIOS_ORDER_VALIDATION_GATES_DRAFT.md",
  "docs\AI_OS\risk_controls\AIOS_TRADE_PERMISSION_STATUS_DRAFT.md",
  "docs\AI_OS\risk_controls\AIOS_PAPER_TRADE_JOURNAL_DRAFT.md",
  "docs\AI_OS\risk_controls\AIOS_BLOCKED_LIVE_EXECUTION_RULES_DRAFT.md"
)
$Results = foreach ($RelativePath in $RequiredFiles) {
  $FullPath = Join-Path $RepoRoot $RelativePath
  [PSCustomObject]@{ Path = $RelativePath; Exists = Test-Path -LiteralPath $FullPath -PathType Leaf }
}
$Missing = $Results | Where-Object { -not $_.Exists }
Write-Host "AI_OS Risk Control Design Readiness DRY_RUN"
$Results | Format-Table -AutoSize
if ($Missing) { Write-Host "Result: FAIL"; exit 1 }
Write-Host "Result: PASS"
exit 0
