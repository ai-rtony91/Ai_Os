$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$RequiredFiles = @(
  "docs\AI_OS\multi_agent\AIOS_AGENT_TASK_ID_DRAFT.md",
  "docs\AI_OS\multi_agent\AIOS_AGENT_DECISION_LOG_DRAFT.md",
  "docs\AI_OS\multi_agent\AIOS_AGENT_FILES_TOUCHED_LOG_DRAFT.md",
  "docs\AI_OS\multi_agent\AIOS_PROTECTED_ACTION_DETECTION_DRAFT.md",
  "docs\AI_OS\multi_agent\AIOS_AGENT_APPROVAL_REQUIRED_FLAG_DRAFT.md"
)
$Results = foreach ($RelativePath in $RequiredFiles) {
  $FullPath = Join-Path $RepoRoot $RelativePath
  [PSCustomObject]@{ Path = $RelativePath; Exists = Test-Path -LiteralPath $FullPath -PathType Leaf }
}
$Missing = $Results | Where-Object { -not $_.Exists }
Write-Host "AI_OS Agent Audit Log Readiness DRY_RUN"
$Results | Format-Table -AutoSize
if ($Missing) { Write-Host "Result: FAIL"; exit 1 }
Write-Host "Result: PASS"
exit 0
