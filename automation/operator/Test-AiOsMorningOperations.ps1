param()

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path ".").Path
$failures = New-Object System.Collections.Generic.List[string]

function Add-Failure {
  param([string]$Message)
  $script:failures.Add($Message) | Out-Null
  Write-Host "FAIL: $Message" -ForegroundColor Red
}

Write-Host "AI_OS Morning Operations Validator" -ForegroundColor Cyan
Write-Host "Repo: $RepoRoot"

$morningScriptPath = Join-Path $RepoRoot "automation/operator/Start-AiOsMorningOperations.ps1"
$docPath = Join-Path $RepoRoot "docs/AI_OS/operator/AIOS_MORNING_OPERATOR_STARTUP_FLOW.md"

if (-not (Test-Path -LiteralPath $morningScriptPath)) {
  Add-Failure "Morning script missing."
}
if (-not (Test-Path -LiteralPath $docPath)) {
  Add-Failure "Morning startup doc missing."
}

if (Test-Path -LiteralPath $morningScriptPath) {
  $scriptText = Get-Content -LiteralPath $morningScriptPath -Raw
  if ($scriptText -match "git\s+commit") {
    Add-Failure "Morning script must not contain git commit."
  }
  if ($scriptText -match "git\s+push") {
    Add-Failure "Morning script must not contain git push."
  }
  if ($scriptText -match "git\s+add\s+\.") {
    Add-Failure "Morning script must not contain git add dot."
  }
  if ($scriptText -match "(?i)(Invoke-Expression|&|powershell).*APPLY") {
    Add-Failure "Morning script must not execute APPLY."
  }
  if ($scriptText -notmatch "-SaveSnapshot") {
    Add-Failure "Morning script must include -SaveSnapshot."
  }
  if ($scriptText -notmatch "-GenerateBriefing") {
    Add-Failure "Morning script must include -GenerateBriefing."
  }
  if (-not $scriptText.Contains('[switch]$LaunchWorkers')) {
    Add-Failure "Morning script must keep LaunchWorkers optional."
  }
  if ($scriptText -notmatch "Start-AiOsParallelDryRunCrew\.ps1") {
    Add-Failure "Morning script must reference Start-AiOsParallelDryRunCrew.ps1."
  }
}

if ($failures.Count -gt 0) {
  Write-Host ""
  Write-Host "AI_OS MORNING OPERATIONS VALIDATION: FAIL" -ForegroundColor Red
  exit 1
}

Write-Host ""
Write-Host "AI_OS MORNING OPERATIONS VALIDATION: PASS" -ForegroundColor Green
exit 0
