$ErrorActionPreference = "Stop"

$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
$JsonFiles = Get-ChildItem -Path $Root -Recurse -Filter "*.json"

$RequiredFiles = @(
  "AIOS_MACRO_AWARENESS_ENGINE_001.md",
  "events\AIOS_HIGH_IMPACT_EVENT_MODEL_001.json",
  "events\AIOS_CENTRAL_BANK_EVENT_MODEL_001.json",
  "events\AIOS_SESSION_TRANSITION_EVENT_MODEL_001.json",
  "events\AIOS_NEWS_RISK_CLASSIFICATION_001.json",
  "liquidity\AIOS_SPREAD_INSTABILITY_MODEL_001.json",
  "liquidity\AIOS_LIQUIDITY_STRESS_MODEL_001.json",
  "liquidity\AIOS_VOLATILITY_EXPANSION_MODEL_001.json",
  "regimes\AIOS_MACRO_REGIME_CLASSIFIER_001.json",
  "regimes\AIOS_RISK_ON_RISK_OFF_MODEL_001.json",
  "telemetry\AIOS_MACRO_WARNING_TELEMETRY_001.json",
  "telemetry\AIOS_EVENT_RISK_TRACKER_001.json",
  "reports\AIOS_MACRO_RISK_REPORT_001.md",
  "reports\AIOS_MARKET_INSTABILITY_REPORT_001.md"
)

$RequiredStates = @(
  "NORMAL",
  "ELEVATED_RISK",
  "HIGH_IMPACT_EVENT",
  "VOLATILITY_EXPANSION",
  "LIQUIDITY_WARNING",
  "RISK_OFF",
  "UNSTABLE",
  "LOCKDOWN"
)

$RequiredReactions = @(
  "reduce confidence",
  "freeze confidence increases",
  "reduce simulated size",
  "reduce portfolio exposure",
  "suppress unstable pair ranking",
  "activate WATCH state",
  "activate LOCKDOWN during severe instability"
)

$RequiredTelemetry = @(
  "event_risk_state",
  "macro_state",
  "volatility_state",
  "liquidity_state",
  "spread_state",
  "confidence_state",
  "portfolio_state",
  "freeze_triggered",
  "lockdown_triggered",
  "paper_only_status"
)

foreach ($RelativePath in $RequiredFiles) {
  $Path = Join-Path $Root $RelativePath
  if (-not (Test-Path -LiteralPath $Path)) {
    throw "Missing required file: $RelativePath"
  }
}

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

foreach ($State in $RequiredStates) {
  if ($AllText -notmatch [regex]::Escape($State)) {
    throw "Missing macro state: $State"
  }
}

foreach ($Reaction in $RequiredReactions) {
  if ($AllText -notmatch [regex]::Escape($Reaction)) {
    throw "Missing risk reaction: $Reaction"
  }
}

foreach ($Field in $RequiredTelemetry) {
  if ($AllText -notmatch [regex]::Escape($Field)) {
    throw "Missing telemetry field: $Field"
  }
}

Write-Host "PASS: AI_OS Phase 15.12 macro awareness validation passed."
Write-Host "Paper-only macro risk-awareness layer is operational."
Write-Host "Live execution, broker APIs, autonomous execution, and network order routing remain BLOCKED."

