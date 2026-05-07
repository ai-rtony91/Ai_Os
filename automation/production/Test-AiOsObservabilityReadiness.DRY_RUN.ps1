$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$RequiredFiles = @(
  "docs\AI_OS\observability\AIOS_HEALTH_CHECKS_DRAFT.md",
  "docs\AI_OS\observability\AIOS_UPTIME_STATUS_DRAFT.md",
  "docs\AI_OS\observability\AIOS_TELEMETRY_SNAPSHOTS_DRAFT.md",
  "docs\AI_OS\observability\AIOS_ERROR_REPORTING_DRAFT.md",
  "docs\AI_OS\observability\AIOS_ROLLBACK_MARKER_DRAFT.md"
)
$Results = foreach ($RelativePath in $RequiredFiles) {
  $FullPath = Join-Path $RepoRoot $RelativePath
  [PSCustomObject]@{ Path = $RelativePath; Exists = Test-Path -LiteralPath $FullPath -PathType Leaf }
}
$Missing = $Results | Where-Object { -not $_.Exists }
Write-Host "AI_OS Observability Readiness DRY_RUN"
$Results | Format-Table -AutoSize
if ($Missing) { Write-Host "Result: FAIL"; exit 1 }
Write-Host "Result: PASS"
exit 0
