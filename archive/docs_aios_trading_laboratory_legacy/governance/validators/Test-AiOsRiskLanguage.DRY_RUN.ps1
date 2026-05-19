$ErrorActionPreference = "Stop"

$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
$JsonFiles = Get-ChildItem -Path (Join-Path $Root "risk_language") -Filter "*.json"

$RequiredDefinitions = @(
  "DANGEROUS",
  "SAFE",
  "UNSTABLE",
  "STABLE",
  "GOOD_EDGE",
  "WEAK_EDGE",
  "NO_EDGE",
  "RECOVERY",
  "LOCKDOWN",
  "ELEVATED_RISK",
  "PORTFOLIO_OVERLOAD",
  "FAKE_RECOVERY"
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

foreach ($Definition in $RequiredDefinitions) {
  if ($AllText -notmatch [regex]::Escape($Definition)) {
    throw "Missing risk-language definition: $Definition"
  }
}

Write-Host "PASS: AI_OS Stage 15.13 risk language validation passed."
Write-Host "Risk language definitions and blocked execution states are present."

