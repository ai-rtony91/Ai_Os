param(
  [string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
)

$ErrorActionPreference = "Stop"
$failures = New-Object System.Collections.Generic.List[string]
# Archive Trading Lab docs referenced below are historical/reference-only evidence, not current authority.
# Dashboard mock data remains fixture-only and this validator does not approve live trading, broker execution, real webhooks, real orders, credentials, APPLY, commit, push, merge, or deployment.

function Add-Failure {
  param([string]$Message)
  $script:failures.Add($Message) | Out-Null
}

Push-Location $RepoRoot
try {
  $runtimeRoot = "archive/docs_aios_trading_laboratory_legacy/paper_bot_core/runtime_simulation"
  $requiredFiles = @(
    "$runtimeRoot/README.md",
    "$runtimeRoot/PAPER_RUNTIME_SIMULATION_SPEC.md",
    "$runtimeRoot/PAPER_RUNTIME_DECISION_SEQUENCE.md",
    "$runtimeRoot/PAPER_RUNTIME_RISK_RULES.md",
    "$runtimeRoot/PAPER_RUNTIME_SCORECARD_UPDATE_RULES.md",
    "$runtimeRoot/PAPER_RUNTIME_NEXT_ACTION.md",
    "$runtimeRoot/PAPER_RUNTIME_INPUT_001.json",
    "$runtimeRoot/PAPER_RUNTIME_REGIME_RESULT_001.json",
    "$runtimeRoot/PAPER_RUNTIME_RISK_RESULT_001.json",
    "$runtimeRoot/PAPER_RUNTIME_DECISION_RESULT_001.json",
    "$runtimeRoot/PAPER_RUNTIME_TRADE_RESULT_001.json",
    "$runtimeRoot/PAPER_RUNTIME_SCORECARD_RESULT_001.json",
    "$runtimeRoot/PAPER_RUNTIME_REVIEW_REPORT_001.json",
    "$runtimeRoot/PAPER_RUNTIME_STATUS.json",
    "apps/dashboard/mock-data/paper-bot-runtime.example.json"
  )

  foreach ($file in $requiredFiles) {
    if (-not (Test-Path -LiteralPath $file)) {
      Add-Failure "Missing required file: $file"
    }
  }

  $jsonFiles = Get-ChildItem -LiteralPath $runtimeRoot -Filter "*.json" -File
  $jsonFiles += Get-Item -LiteralPath "apps/dashboard/mock-data/paper-bot-runtime.example.json"
  foreach ($jsonFile in $jsonFiles) {
    try {
      Get-Content -Raw -LiteralPath $jsonFile.FullName | ConvertFrom-Json | Out-Null
    } catch {
      Add-Failure "JSON parse failed: $($jsonFile.FullName)"
    }
  }

  $scorecard = Get-Content -Raw -LiteralPath "$runtimeRoot/PAPER_RUNTIME_SCORECARD_RESULT_001.json" | ConvertFrom-Json
  foreach ($field in @("trade_count", "win_rate", "average_win", "average_loss", "expectancy", "profit_factor", "max_drawdown", "confidence_score", "blocked_reason", "review_status")) {
    if (-not ($scorecard.PSObject.Properties.Name -contains $field)) {
      Add-Failure "Missing scorecard field: $field"
    }
  }

  $combinedText = foreach ($file in $requiredFiles) {
    if (Test-Path -LiteralPath $file) {
      Get-Content -Raw -LiteralPath $file
    }
  }
  $text = ($combinedText -join "`n")

  foreach ($marker in @("BLOCKED", "No broker", "No OANDA", "No API keys", "No credentials", "No real webhooks", "No real orders")) {
    if ($text -notmatch [regex]::Escape($marker)) {
      Add-Failure "Missing safety marker: $marker"
    }
  }

  foreach ($unsafePattern in @("live_execution_status.*allowed", "broker_status.*connected", "oanda_status.*connected", "api_key_status.*enabled", "credential_status.*enabled", "real_webhook_status.*enabled", "real_order_status.*enabled")) {
    if ($text -match $unsafePattern) {
      Add-Failure "Unsafe enabled pattern found: $unsafePattern"
    }
  }

  $secretPattern = "(?i)(api[_-]?key\s*[:=]\s*[A-Za-z0-9_\-]{12,}|secret\s*[:=]\s*[A-Za-z0-9_\-]{12,}|token\s*[:=]\s*[A-Za-z0-9_\-]{12,}|password\s*[:=]\s*\S+)"
  if ($text -match $secretPattern) {
    Add-Failure "Possible secret-like value found in runtime files."
  }

  if ($failures.Count -gt 0) {
    Write-Output "AI_OS Paper Bot Runtime Simulation: FAIL"
    $failures | ForEach-Object { Write-Output "FAIL: $_" }
    exit 1
  }

  Write-Output "AI_OS Paper Bot Runtime Simulation: PASS"
  Write-Output "Paper Trade JSON parse: PASS"
  Write-Output "Required files: PASS"
  Write-Output "Paper Scorecard fields: PASS"
  Write-Output "Paper Trade safety boundary: PASS"
  Write-Output "Paper Trade sample data: PASS"
} finally {
  Pop-Location
}
