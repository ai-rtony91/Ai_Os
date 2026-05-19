$ErrorActionPreference = "Stop"

$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
$JsonFiles = Get-ChildItem -Path $Root -Recurse -Filter "*.json"

$RequiredTelemetry = @(
  "proof_state",
  "edge_state",
  "confidence_state",
  "stability_state",
  "drawdown_pressure",
  "replay_survivability",
  "regime_reliability",
  "portfolio_survivability",
  "freeze_triggered",
  "paper_only_status"
)

$RequiredPromotionRules = @(
  "confidence cannot increase without evidence",
  "replay validation required",
  "minimum sample size required",
  "rolling stability required",
  "regime reliability required",
  "survivability audit required",
  "drawdown pressure must remain acceptable"
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
  if ($Json.autonomous_execution_status -ne "BLOCKED") {
    throw "autonomous_execution_status must be BLOCKED: $($File.Name)"
  }
  if ($Json.network_order_routing_status -ne "BLOCKED") {
    throw "network_order_routing_status must be BLOCKED: $($File.Name)"
  }
}

$AllTextLower = $AllText.ToLowerInvariant()

foreach ($Field in $RequiredTelemetry) {
  if ($AllText -notmatch [regex]::Escape($Field)) {
    throw "Missing telemetry field: $Field"
  }
}

foreach ($Rule in $RequiredPromotionRules) {
  if ($AllTextLower -notmatch [regex]::Escape($Rule.ToLowerInvariant())) {
    throw "Missing confidence promotion rule: $Rule"
  }
}

Write-Host "PASS: AI_OS Stage 15.15 performance verification validation passed."
Write-Host "Telemetry, confidence promotion rules, and blocked execution states are present."

