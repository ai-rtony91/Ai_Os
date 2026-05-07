$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$RequiredFiles = @(
  "docs\AI_OS\azure\AIOS_AZURE_DEPLOYMENT_TARGET_DRAFT.md",
  "docs\AI_OS\azure\AIOS_AZURE_RESOURCE_GROUP_BOUNDARY_DRAFT.md",
  "docs\AI_OS\azure\AIOS_NO_SECRET_IN_CODE_RULE_DRAFT.md",
  "docs\AI_OS\azure\AIOS_ENVIRONMENT_VARIABLE_POLICY_DRAFT.md",
  "docs\AI_OS\azure\AIOS_DEPLOYMENT_READINESS_STATUS_DRAFT.md"
)
$Results = foreach ($RelativePath in $RequiredFiles) {
  $FullPath = Join-Path $RepoRoot $RelativePath
  [PSCustomObject]@{ Path = $RelativePath; Exists = Test-Path -LiteralPath $FullPath -PathType Leaf }
}
$Missing = $Results | Where-Object { -not $_.Exists }
Write-Host "AI_OS Azure Production Boundary Readiness DRY_RUN"
$Results | Format-Table -AutoSize
if ($Missing) { Write-Host "Result: FAIL"; exit 1 }
Write-Host "Result: PASS"
exit 0
