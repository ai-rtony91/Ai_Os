$ErrorActionPreference = "Stop"

$root = Resolve-Path (Join-Path $PSScriptRoot "..")
$jsonFiles = Get-ChildItem -Path $root -Recurse -Filter "*.json"
$requiredOutputs = @("FAVORABLE_CONDITION", "UNFAVORABLE_CONDITION", "REDUCE_SIZE", "INCREASE_CONFIDENCE", "BLOCK_TRADE", "WAIT_FOR_CONFIRMATION")
$requiredMetrics = @("rolling_win_rate", "rolling_expectancy", "strategy_strength_score", "pair_stability_score", "confidence_adjustment", "regime_reliability_score", "session_efficiency_score", "drawdown_pressure", "paper_only_status")

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

$learningPath = Join-Path $root "adaptive\FOREX_STRATEGY_LEARNING_MODEL_001.json"
$learning = Get-Content -LiteralPath $learningPath -Raw | ConvertFrom-Json
foreach ($output in $requiredOutputs) {
  if ($learning.adaptive_outputs -notcontains $output) {
    Write-Host "FAIL: Missing adaptive output: $output"
    exit 1
  }
}

foreach ($metric in $requiredMetrics) {
  if (-not ($learning.adaptive_metrics.PSObject.Properties.Name -contains $metric)) {
    Write-Host "FAIL: Missing adaptive metric: $metric"
    exit 1
  }
}

if ($learning.learning_safeguards.adaptation_mode -ne "recommendation_only") {
  Write-Host "FAIL: adaptation mode must be recommendation_only."
  exit 1
}

$files = Get-ChildItem -Path $root -Recurse -File
foreach ($file in $files) {
  $text = Get-Content -LiteralPath $file.FullName -Raw
  $unsafePattern = "live_execution_status`"\s*:\s*`"ALLOWED|" +
    "broker_access_status`"\s*:\s*`"ALLOWED|" +
    "external_api_status`"\s*:\s*`"ALLOWED|" +
    "internet_learning_status`"\s*:\s*`"ALLOWED|" +
    "self_modifying_code_status`"\s*:\s*`"ALLOWED|" +
    "auto_deployment_status`"\s*:\s*`"ALLOWED"
  if ($text -match $unsafePattern) {
    Write-Host "FAIL: Unsafe adaptive permission found: $($file.FullName)"
    exit 1
  }
}

Write-Host "PASS: Forex adaptive engine DRY_RUN validation passed."
Write-Host "Paper-only recommendation safeguards confirmed."
