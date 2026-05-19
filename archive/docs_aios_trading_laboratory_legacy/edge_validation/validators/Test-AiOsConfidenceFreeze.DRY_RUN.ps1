$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..\..\..\..")
$files = @(
  (Join-Path $repoRoot "docs\AI_OS\trading_laboratory\edge_validation\statistics\AIOS_CONFIDENCE_FREEZE_MODEL_001.json"),
  (Join-Path $repoRoot "docs\AI_OS\trading_laboratory\edge_validation\evidence\AIOS_CONFIDENCE_RECOVERY_EVIDENCE_001.json"),
  (Join-Path $repoRoot "docs\AI_OS\trading_laboratory\forex_money_bot\adaptive\FOREX_CONFIDENCE_FREEZE_RULE_001.json"),
  (Join-Path $repoRoot "docs\AI_OS\trading_laboratory\core_intelligence\AIOS_CORE_CONFIDENCE_FREEZE_POLICY_001.json")
)

$requiredTriggers = @(
  "stability_score_below_threshold",
  "drawdown_pressure_above_threshold",
  "regime_reliability_score_below_threshold",
  "rolling_expectancy_below_threshold",
  "sample_size_below_minimum",
  "edge_state_is_watch",
  "edge_state_is_weak_edge",
  "edge_state_is_no_edge"
)

$requiredBehavior = @(
  "block_confidence_increases",
  "allow_confidence_decreases",
  "lower_ranking_priority",
  "reduce_recommended_paper_size",
  "require_stronger_confirmations",
  "require_more_paper_evidence",
  "prevent_fast_re_promotion",
  "force_watch_state_when_unstable"
)

$requiredRecovery = @(
  "rolling_stability_recovered",
  "drawdown_pressure_reduced",
  "rolling_expectancy_positive",
  "minimum_sample_size_met",
  "regime_reliability_recovered",
  "edge_confidence_recovered",
  "multiple_paper_sessions_confirmed"
)

$requiredStates = @(
  "CONFIDENCE_ACTIVE",
  "CONFIDENCE_FROZEN",
  "RECOVERY_REQUIRED",
  "WATCH",
  "WEAK_EDGE",
  "NO_EDGE"
)

foreach ($file in $files) {
  if (-not (Test-Path -LiteralPath $file)) {
    Write-Host "FAIL: Missing confidence freeze file: $file"
    exit 1
  }

  $json = Get-Content -LiteralPath $file -Raw | ConvertFrom-Json

  if ($json.paper_only_status -ne "PAPER_ONLY") {
    Write-Host "FAIL: paper_only_status must be PAPER_ONLY: $file"
    exit 1
  }
  if ($json.live_execution_status -ne "BLOCKED") {
    Write-Host "FAIL: live_execution_status must remain BLOCKED: $file"
    exit 1
  }
  if ($json.broker_api_status -ne "BLOCKED") {
    Write-Host "FAIL: broker_api_status must remain BLOCKED: $file"
    exit 1
  }

  foreach ($trigger in $requiredTriggers) {
    if (-not ($json.freeze_triggers.PSObject.Properties.Name -contains $trigger)) {
      Write-Host "FAIL: Missing freeze trigger $trigger in $file"
      exit 1
    }
  }

  foreach ($behavior in $requiredBehavior) {
    if (-not ($json.freeze_behavior.PSObject.Properties.Name -contains $behavior)) {
      Write-Host "FAIL: Missing freeze behavior $behavior in $file"
      exit 1
    }
  }

  foreach ($condition in $requiredRecovery) {
    if (-not ($json.recovery_conditions.PSObject.Properties.Name -contains $condition)) {
      Write-Host "FAIL: Missing recovery condition $condition in $file"
      exit 1
    }
  }

  foreach ($state in $requiredStates) {
    if ($json.required_states -notcontains $state) {
      Write-Host "FAIL: Missing required state $state in $file"
      exit 1
    }
  }
}

Write-Host "PASS: AI_OS confidence freeze DRY_RUN validation passed."
Write-Host "Confidence increases are evidence-gated; paper-only isolation remains BLOCKED."
