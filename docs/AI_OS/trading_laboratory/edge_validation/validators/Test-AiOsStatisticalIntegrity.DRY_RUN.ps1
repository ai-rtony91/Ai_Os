$ErrorActionPreference = "Stop"

$root = Resolve-Path (Join-Path $PSScriptRoot "..")
$jsonFiles = Get-ChildItem -Path $root -Recurse -Filter "*.json"
$requiredMetrics = @("expectancy", "profit_factor", "win_rate", "average_win", "average_loss", "max_drawdown", "sample_size", "edge_confidence_score", "regime_reliability_score", "stability_score", "paper_only_status")
$requiredRegimes = @("TRENDING", "RANGING", "HIGH_VOLATILITY", "LOW_VOLATILITY", "SESSION_TRANSITION", "NEWS_RISK")

foreach ($file in $jsonFiles) {
  $json = Get-Content -LiteralPath $file.FullName -Raw | ConvertFrom-Json
  if ($json.PSObject.Properties.Name -contains "metrics") {
    foreach ($metric in $requiredMetrics) {
      if (-not ($json.metrics.PSObject.Properties.Name -contains $metric)) {
        Write-Host "FAIL: Missing metric $metric in $($file.FullName)"
        exit 1
      }
    }
  }
}

$regimeSource = Get-Content -LiteralPath (Join-Path $root "regime_analysis\AIOS_VOLATILITY_EDGE_001.json") -Raw | ConvertFrom-Json
foreach ($regime in $requiredRegimes) {
  if ($regimeSource.regime_states -notcontains $regime) {
    Write-Host "FAIL: Missing regime state: $regime"
    exit 1
  }
}

$files = Get-ChildItem -Path $root -Recurse -File
foreach ($file in $files) {
  $text = Get-Content -LiteralPath $file.FullName -Raw
  $unsafePattern = "live_execution_status`"\s*:\s*`"ALLOWED|" +
    "broker_api_status`"\s*:\s*`"CONNECTED|" +
    "real_execution_status`"\s*:\s*`"ENABLED|" +
    "internet_call_status`"\s*:\s*`"ALLOWED|" +
    "self_modifying_logic_status`"\s*:\s*`"ENABLED|" +
    "autonomous_execution_status`"\s*:\s*`"ENABLED"
  if ($text -match $unsafePattern) {
    Write-Host "FAIL: Unsafe execution state found: $($file.FullName)"
    exit 1
  }
}

Write-Host "PASS: AI_OS statistical integrity DRY_RUN passed."
Write-Host "Required metrics, regime states, and blocked execution confirmed."
