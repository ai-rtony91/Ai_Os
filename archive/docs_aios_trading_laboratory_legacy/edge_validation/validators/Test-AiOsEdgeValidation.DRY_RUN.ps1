$ErrorActionPreference = "Stop"

$root = Resolve-Path (Join-Path $PSScriptRoot "..")
$jsonFiles = Get-ChildItem -Path $root -Recurse -Filter "*.json"
$requiredEdgeStates = @("NO_EDGE", "WEAK_EDGE", "MODERATE_EDGE", "STRONG_EDGE", "UNVERIFIED")

foreach ($file in $jsonFiles) {
  $json = Get-Content -LiteralPath $file.FullName -Raw | ConvertFrom-Json
  if (-not ($json.PSObject.Properties.Name -contains "paper_only_status")) {
    Write-Host "FAIL: Missing paper_only_status: $($file.FullName)"
    exit 1
  }
  if ($json.paper_only_status -ne "PAPER_ONLY") {
    Write-Host "FAIL: paper_only_status must be PAPER_ONLY: $($file.FullName)"
    exit 1
  }
  if ($json.live_execution_status -ne "BLOCKED") {
    Write-Host "FAIL: live_execution_status must remain BLOCKED: $($file.FullName)"
    exit 1
  }
}

$stateSource = Get-Content -LiteralPath (Join-Path $root "statistics\AIOS_EXPECTANCY_MODEL_001.json") -Raw | ConvertFrom-Json
foreach ($state in $requiredEdgeStates) {
  if ($stateSource.edge_states -notcontains $state) {
    Write-Host "FAIL: Missing edge state: $state"
    exit 1
  }
}

Write-Host "PASS: AI_OS edge validation DRY_RUN passed."
Write-Host "Edge states, JSON parsing, and paper-only isolation confirmed."
