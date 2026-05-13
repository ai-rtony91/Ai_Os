$ErrorActionPreference = "Stop"

$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
$JsonFiles = Get-ChildItem -Path $Root -Recurse -Filter "*.json"

$RequiredFiles = @(
  "AIOS_CHAOS_PREVENTION_ENGINE_001.md",
  "alerts\AIOS_EDGE_DETERIORATION_ALERT_001.json",
  "alerts\AIOS_FAKE_RECOVERY_ALERT_001.json",
  "alerts\AIOS_DRAWDOWN_PRESSURE_ALERT_001.json",
  "alerts\AIOS_REGIME_INSTABILITY_ALERT_001.json",
  "alerts\AIOS_PORTFOLIO_OVERLOAD_ALERT_001.json",
  "alerts\AIOS_CONFIDENCE_DEGRADATION_ALERT_001.json",
  "telemetry\AIOS_WARNING_TELEMETRY_001.json",
  "telemetry\AIOS_CASCADING_RISK_TRACKER_001.json",
  "reports\AIOS_EARLY_WARNING_REPORT_001.md",
  "reports\AIOS_SYSTEM_STABILITY_REPORT_001.md"
)

$RequiredStates = @("NORMAL", "CAUTION", "WATCH", "UNSTABLE", "CRITICAL", "LOCKDOWN")
$RequiredActions = @(
  "freeze confidence increases",
  "reduce ranking priority",
  "reduce simulated exposure",
  "reduce recommended paper size",
  "require stronger confirmations",
  "block unstable strategy promotion",
  "trigger WATCH state",
  "trigger LOCKDOWN state during severe instability"
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
  if ($Json.real_execution_status -ne "BLOCKED") {
    throw "real_execution_status must be BLOCKED: $($File.Name)"
  }
  if ($Json.network_call_status -ne "BLOCKED") {
    throw "network_call_status must be BLOCKED: $($File.Name)"
  }
  if ($Json.autonomous_execution_status -ne "BLOCKED") {
    throw "autonomous_execution_status must be BLOCKED: $($File.Name)"
  }
}

foreach ($State in $RequiredStates) {
  if ($AllText -notmatch [regex]::Escape($State)) {
    throw "Missing warning state: $State"
  }
}

foreach ($Action in $RequiredActions) {
  if ($AllText -notmatch [regex]::Escape($Action)) {
    throw "Missing prevention action: $Action"
  }
}

foreach ($Field in $RequiredTelemetry) {
  if ($AllText -notmatch [regex]::Escape($Field)) {
    throw "Missing telemetry field: $Field"
  }
}

Write-Host "PASS: AI_OS Phase 15.11 chaos prevention validation passed."
Write-Host "Paper-only early warning layer is operational."
Write-Host "Live execution, broker APIs, network calls, autonomous execution, and real execution remain BLOCKED."

