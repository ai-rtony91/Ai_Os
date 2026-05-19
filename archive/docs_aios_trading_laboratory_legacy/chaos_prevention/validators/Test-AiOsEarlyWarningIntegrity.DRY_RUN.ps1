$ErrorActionPreference = "Stop"

$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
$JsonFiles = Get-ChildItem -Path $Root -Recurse -Filter "*.json"

$RequiredDetectionLogic = @(
  "detect rolling stability degradation",
  "detect rapid drawdown expansion",
  "detect fake confidence recovery",
  "detect unstable edge transitions",
  "detect volatility spikes",
  "detect correlation overload",
  "detect portfolio stress concentration",
  "detect repeated weak-edge behavior"
)

$RequiredTelemetry = @(
  "warning_state",
  "edge_state",
  "confidence_state",
  "drawdown_pressure",
  "volatility_state",
  "portfolio_state",
  "correlation_risk",
  "freeze_triggered",
  "lockdown_triggered",
  "paper_only_status"
)

$AllText = ""

foreach ($File in $JsonFiles) {
  $Raw = Get-Content -LiteralPath $File.FullName -Raw
  $AllText += $Raw
  $Json = $Raw | ConvertFrom-Json

  if ($Json.paper_only_status -ne "PAPER_ONLY") {
    throw "paper_only_status must be PAPER_ONLY: $($File.Name)"
  }
  if ($Json.live_execution_status -ne "BLOCKED") {
    throw "live_execution_status must be BLOCKED: $($File.Name)"
  }
  if ($Json.broker_api_status -ne "BLOCKED") {
    throw "broker_api_status must be BLOCKED: $($File.Name)"
  }
}

foreach ($Logic in $RequiredDetectionLogic) {
  if ($AllText -notmatch [regex]::Escape($Logic)) {
    throw "Missing detection logic: $Logic"
  }
}

foreach ($Field in $RequiredTelemetry) {
  if ($AllText -notmatch [regex]::Escape($Field)) {
    throw "Missing telemetry field: $Field"
  }
}

if ($AllText -notmatch "LOCKDOWN") {
  throw "LOCKDOWN state must be present."
}
if ($AllText -notmatch "CONFIDENCE_FROZEN") {
  throw "CONFIDENCE_FROZEN state must be present."
}
if ($AllText -notmatch "freeze confidence increases") {
  throw "Confidence freeze action must be present."
}

Write-Host "PASS: AI_OS Phase 15.11 early warning integrity validation passed."
Write-Host "Warning states, detection logic, telemetry, freeze behavior, and lockdown behavior are present."
Write-Host "Unsafe execution paths remain BLOCKED."

