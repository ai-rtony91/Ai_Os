$ErrorActionPreference = "Stop"

$root = Resolve-Path (Join-Path $PSScriptRoot "..")
$regimePath = Join-Path $root "regimes\FOREX_MARKET_REGIME_ENGINE_001.json"
$regime = Get-Content -LiteralPath $regimePath -Raw | ConvertFrom-Json
$requiredRegimes = @("TRENDING", "RANGING", "HIGH_VOLATILITY", "LOW_VOLATILITY", "NEWS_RISK", "SESSION_TRANSITION")

foreach ($state in $requiredRegimes) {
  if ($regime.regime_states -notcontains $state) {
    Write-Host "FAIL: Missing regime state: $state"
    exit 1
  }
}

$regimeFiles = Get-ChildItem -Path (Join-Path $root "regimes") -Filter "*.json"
foreach ($file in $regimeFiles) {
  $json = Get-Content -LiteralPath $file.FullName -Raw | ConvertFrom-Json
  if ($json.paper_only_status -ne "PAPER_ONLY") {
    Write-Host "FAIL: regime file paper_only_status must be PAPER_ONLY: $($file.FullName)"
    exit 1
  }
  if ($json.live_execution_status -ne "BLOCKED") {
    Write-Host "FAIL: regime file live_execution_status must remain BLOCKED: $($file.FullName)"
    exit 1
  }
}

Write-Host "PASS: Forex regime integrity DRY_RUN validation passed."
Write-Host "Regime states and blocked execution confirmed."
