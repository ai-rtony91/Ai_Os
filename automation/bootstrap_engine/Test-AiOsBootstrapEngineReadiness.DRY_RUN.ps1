$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$RequiredFiles = @(
  "docs\AI_OS\bootstrap_engine\AIOS_PROJECT_IDENTITY_INFERENCE_DRAFT.md",
  "docs\AI_OS\bootstrap_engine\AIOS_FOLDER_OWNERSHIP_INFERENCE_DRAFT.md",
  "docs\AI_OS\bootstrap_engine\AIOS_PROTECTED_FILE_INFERENCE_DRAFT.md",
  "docs\AI_OS\bootstrap_engine\AIOS_SCAFFOLD_PROPOSAL_GENERATION_DRAFT.md",
  "docs\AI_OS\bootstrap_engine\AIOS_HUMAN_APPROVAL_BEFORE_APPLY_DRAFT.md"
)
$Results = foreach ($RelativePath in $RequiredFiles) {
  $FullPath = Join-Path $RepoRoot $RelativePath
  [PSCustomObject]@{ Path = $RelativePath; Exists = Test-Path -LiteralPath $FullPath -PathType Leaf }
}
$Missing = $Results | Where-Object { -not $_.Exists }
Write-Host "AI_OS Bootstrap Engine Readiness DRY_RUN"
$Results | Format-Table -AutoSize
if ($Missing) { Write-Host "Result: FAIL"; exit 1 }
Write-Host "Result: PASS"
exit 0
