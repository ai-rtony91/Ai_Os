$ErrorActionPreference = "Stop"

$root = Resolve-Path (Join-Path $PSScriptRoot "..")
$jsonFiles = Get-ChildItem -Path $root -Recurse -Filter "*.json"
$requiredStates = @("NORMAL", "WATCH", "UNSTABLE", "EDGE_COLLAPSE", "DRAWDOWN_CRITICAL", "RECOVERY_REQUIRED", "CONFIDENCE_FROZEN")

foreach ($file in $jsonFiles) {
  $json = Get-Content -LiteralPath $file.FullName -Raw | ConvertFrom-Json
  if ($json.paper_only_status -ne "PAPER_ONLY") {
    Write-Host "FAIL: paper_only_status must be PAPER_ONLY: $($file.FullName)"
    exit 1
  }
  if ($json.live_execution_status -ne "BLOCKED") {
    Write-Host "FAIL: live_execution_status must remain BLOCKED: $($file.FullName)"
    exit 1
  }
  foreach ($state in $requiredStates) {
    if ($json.scenario_states -notcontains $state) {
      Write-Host "FAIL: Missing scenario state $state in $($file.FullName)"
      exit 1
    }
  }
}

Write-Host "PASS: AI_OS replay engine DRY_RUN validation passed."
Write-Host "Scenario states, JSON parsing, and paper-only replay isolation confirmed."
