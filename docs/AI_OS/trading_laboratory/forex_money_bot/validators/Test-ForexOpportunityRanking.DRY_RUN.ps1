$ErrorActionPreference = "Stop"

$root = Resolve-Path (Join-Path $PSScriptRoot "..")
$requiredOutputs = @("TOP_PRIORITY", "MEDIUM_PRIORITY", "LOW_PRIORITY", "BLOCK_TRADE", "WAIT_FOR_BETTER_SETUP", "REDUCE_EXPOSURE", "REDUCE_SIZE", "ALLOW_PAPER_ENTRY")
$requiredQueueFields = @("signal_id", "pair", "direction", "confidence_score", "priority_state", "queue_rank", "session_name", "market_regime", "portfolio_state", "risk_state", "paper_only_status", "live_execution_status")

$jsonFiles = Get-ChildItem -Path $root -Recurse -Filter "*.json"
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

$rankingPath = Join-Path $root "ranking\FOREX_OPPORTUNITY_RANKING_ENGINE_001.json"
$ranking = Get-Content -LiteralPath $rankingPath -Raw | ConvertFrom-Json
foreach ($output in $requiredOutputs) {
  if ($ranking.ranking_outputs -notcontains $output) {
    Write-Host "FAIL: Missing ranking output: $output"
    exit 1
  }
}

$queuePath = Join-Path $root "queue\FOREX_SIGNAL_QUEUE_001.json"
$queue = Get-Content -LiteralPath $queuePath -Raw | ConvertFrom-Json
foreach ($item in $queue.queue) {
  foreach ($field in $requiredQueueFields) {
    if (-not ($item.PSObject.Properties.Name -contains $field)) {
      Write-Host "FAIL: Missing queue field $field"
      exit 1
    }
  }
  if ($item.live_execution_status -ne "BLOCKED") {
    Write-Host "FAIL: Queue item live_execution_status must be BLOCKED."
    exit 1
  }
}

$ranks = @($queue.queue | ForEach-Object { $_.queue_rank })
$sortedRanks = @($ranks | Sort-Object)
if (($sortedRanks -join ",") -ne ($ranks -join ",")) {
  Write-Host "FAIL: Queue ranks must be ordered ascending."
  exit 1
}

Write-Host "PASS: Forex opportunity ranking DRY_RUN validation passed."
Write-Host "Ranking outputs and paper queue ordering confirmed."
