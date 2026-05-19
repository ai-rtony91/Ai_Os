$ErrorActionPreference = "Stop"

$root = Resolve-Path (Join-Path $PSScriptRoot "..")
$jsonFiles = Get-ChildItem -Path $root -Recurse -Filter "*.json"
$requiredTradeStates = @("PENDING", "ACTIVE", "PARTIAL", "CLOSED_WIN", "CLOSED_LOSS", "SCRATCH", "REJECTED", "EXPIRED")

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

$lifecyclePath = Join-Path $root "simulation\FOREX_TRADE_LIFECYCLE_001.json"
$lifecycle = Get-Content -LiteralPath $lifecyclePath -Raw | ConvertFrom-Json
foreach ($state in $requiredTradeStates) {
  if ($lifecycle.trade_states -notcontains $state) {
    Write-Host "FAIL: Missing trade state: $state"
    exit 1
  }
}

$flowPath = Join-Path $root "simulation\FOREX_SIMULATED_TRADE_FLOW_001.json"
$flow = Get-Content -LiteralPath $flowPath -Raw | ConvertFrom-Json
if (($flow.simulation_flow | Measure-Object).Count -lt 11) {
  Write-Host "FAIL: Simulation flow must include all required steps."
  exit 1
}

$files = Get-ChildItem -Path $root -Recurse -File
foreach ($file in $files) {
  $text = Get-Content -LiteralPath $file.FullName -Raw
  $unsafePattern = "broker APIs " + "ALLOWED|" +
    "webhook_status`"\s*:\s*`"SENT|" +
    "internet_call_status`"\s*:\s*`"ALLOWED|" +
    "real_order_status`"\s*:\s*`"SENT|" +
    "live_execution_status`"\s*:\s*`"ALLOWED|" +
    "secret" + "_value"
  if ($text -match $unsafePattern) {
    Write-Host "FAIL: Unsafe execution pattern found: $($file.FullName)"
    exit 1
  }
}

Write-Host "PASS: Forex paper execution loop DRY_RUN validation passed."
Write-Host "Paper-only simulated trade lifecycle confirmed."
