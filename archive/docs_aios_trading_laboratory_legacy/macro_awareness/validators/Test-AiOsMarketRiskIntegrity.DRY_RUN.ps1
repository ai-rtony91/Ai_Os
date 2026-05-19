$ErrorActionPreference = "Stop"

$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
$JsonFiles = Get-ChildItem -Path $Root -Recurse -Filter "*.json"

$RequiredEvents = @(
  "CPI placeholder",
  "FOMC placeholder",
  "NFP placeholder",
  "ECB placeholder",
  "BOJ placeholder",
  "session overlap awareness",
  "pre-event caution window",
  "post-event stabilization window"
)

$RequiredPrinciples = @(
  "macro awareness informs risk",
  "macro awareness does not directly execute trades",
  "no LLM in direct live order path",
  "no autonomous headline trading",
  "market context modifies confidence only",
  "execution isolation remains permanent"
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

$AllText = Get-Content -LiteralPath (Join-Path $Root "AIOS_MACRO_AWARENESS_ENGINE_001.md") -Raw
$AllText += Get-Content -LiteralPath (Join-Path $Root "reports\AIOS_MACRO_RISK_REPORT_001.md") -Raw
$AllText += Get-Content -LiteralPath (Join-Path $Root "reports\AIOS_MARKET_INSTABILITY_REPORT_001.md") -Raw

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

foreach ($Event in $RequiredEvents) {
  if ($AllText -notmatch [regex]::Escape($Event)) {
    throw "Missing event awareness item: $Event"
  }
}

foreach ($Principle in $RequiredPrinciples) {
  if ($AllText -notmatch [regex]::Escape($Principle)) {
    throw "Missing architecture principle: $Principle"
  }
}

foreach ($Field in $RequiredTelemetry) {
  if ($AllText -notmatch [regex]::Escape($Field)) {
    throw "Missing telemetry field: $Field"
  }
}

if ($AllText -notmatch "risk-awareness only") {
  throw "Risk-awareness only boundary must be documented."
}
if ($AllText -notmatch "LOCKDOWN") {
  throw "LOCKDOWN macro state must be present."
}

Write-Host "PASS: AI_OS Phase 15.12 market risk integrity validation passed."
Write-Host "Event awareness, macro states, risk reactions, telemetry, and execution isolation are present."
Write-Host "Unsafe execution paths remain BLOCKED."

