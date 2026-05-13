$ErrorActionPreference = "Stop"

$root = Resolve-Path (Join-Path $PSScriptRoot "..")
$jsonFiles = Get-ChildItem -Path $root -Recurse -Filter "*.json"
$requiredReactions = @("reduce_confidence", "freeze_confidence_increases", "reduce_ranking_priority", "reduce_simulated_size", "move_to_watch_state", "block_unstable_edge_promotion", "require_recovery_evidence")
$requiredTelemetry = @("scenario_id", "scenario_type", "stability_score", "drawdown_pressure", "edge_state", "confidence_state", "ranking_state", "portfolio_state", "freeze_triggered", "paper_only_status")

foreach ($file in $jsonFiles) {
  $json = Get-Content -LiteralPath $file.FullName -Raw | ConvertFrom-Json
  foreach ($reaction in $requiredReactions) {
    if ($json.stress_reactions -notcontains $reaction) {
      Write-Host "FAIL: Missing stress reaction $reaction in $($file.FullName)"
      exit 1
    }
  }
  foreach ($field in $requiredTelemetry) {
    if (-not ($json.telemetry.PSObject.Properties.Name -contains $field)) {
      Write-Host "FAIL: Missing telemetry field $field in $($file.FullName)"
      exit 1
    }
  }
  if ($json.broker_api_status -ne "BLOCKED" -or $json.real_execution_status -ne "BLOCKED" -or $json.network_call_status -ne "BLOCKED" -or $json.autonomous_execution_status -ne "BLOCKED") {
    Write-Host "FAIL: Unsafe execution status in $($file.FullName)"
    exit 1
  }
}

Write-Host "PASS: AI_OS stress integrity DRY_RUN validation passed."
Write-Host "Stress reactions, telemetry fields, and blocked execution confirmed."
