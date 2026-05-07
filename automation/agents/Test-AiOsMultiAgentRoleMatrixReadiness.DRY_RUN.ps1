$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$RequiredFiles = @(
  "docs\AI_OS\agents\AIOS_CHATGPT_ROLE_DRAFT.md",
  "docs\AI_OS\agents\AIOS_CODEX_ROLE_DRAFT.md",
  "docs\AI_OS\agents\AIOS_CLAUDE_ROLE_DRAFT.md",
  "docs\AI_OS\agents\AIOS_HUMAN_OPERATOR_APPROVAL_DRAFT.md",
  "docs\AI_OS\agents\AIOS_ALLOWED_BLOCKED_AGENT_ACTIONS_DRAFT.md"
)
$Results = foreach ($RelativePath in $RequiredFiles) {
  $FullPath = Join-Path $RepoRoot $RelativePath
  [PSCustomObject]@{ Path = $RelativePath; Exists = Test-Path -LiteralPath $FullPath -PathType Leaf }
}
$Missing = $Results | Where-Object { -not $_.Exists }
Write-Host "AI_OS Multi-Agent Role Matrix Readiness DRY_RUN"
$Results | Format-Table -AutoSize
if ($Missing) { Write-Host "Result: FAIL"; exit 1 }
Write-Host "Result: PASS"
exit 0
