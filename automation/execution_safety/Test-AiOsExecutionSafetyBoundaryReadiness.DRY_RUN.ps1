$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$RequiredFiles = @(
  "docs\AI_OS\execution\AIOS_NO_LIVE_TRADE_ENFORCEMENT_DRAFT.md",
  "docs\AI_OS\execution\AIOS_BROKER_ADAPTER_BOUNDARY_DRAFT.md",
  "docs\AI_OS\brokers\oanda\AIOS_OANDA_SANDBOX_ONLY_POLICY_DRAFT.md",
  "docs\AI_OS\execution\AIOS_WEBHOOK_VALIDATION_BOUNDARY_DRAFT.md",
  "docs\AI_OS\execution\AIOS_EXECUTION_KILL_SWITCH_DRAFT.md"
)
$Results = foreach ($RelativePath in $RequiredFiles) {
  $FullPath = Join-Path $RepoRoot $RelativePath
  [PSCustomObject]@{ Path = $RelativePath; Exists = Test-Path -LiteralPath $FullPath -PathType Leaf }
}
$Missing = $Results | Where-Object { -not $_.Exists }
Write-Host "AI_OS Execution Safety Boundary Readiness DRY_RUN"
$Results | Format-Table -AutoSize
if ($Missing) { Write-Host "Result: FAIL"; exit 1 }
Write-Host "Result: PASS"
exit 0
