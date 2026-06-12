$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
# Historical/reference-only evidence. These archive files are not current authority
# and are not active Reports/checkpoints output.
$docPath = Join-Path $repoRoot "archive\docs_aios_trading_laboratory_legacy\phase_14_14\PHASE_14_14_STRATEGY_MEMORY_ENGINE.md"
$jsonPath = Join-Path $repoRoot "apps\trading_lab\mock-data\strategy_memory_engine.example.json"
$checkpointPath = Join-Path $repoRoot "archive\reports_legacy\checkpoints\CHECKPOINT_PHASE_14_14_STRATEGY_MEMORY.md"

# This validator provides evidence only. It does not approve live trading, broker
# execution, real webhooks, real orders, credentials, APPLY, commit, push, merge,
# or deployment.

$requiredFiles = @($docPath, $jsonPath, $checkpointPath)

foreach ($file in $requiredFiles) {
  if (-not (Test-Path -LiteralPath $file)) {
    Write-Host "FAIL: Missing required file: $file"
    exit 1
  }
}

try {
  $jsonText = Get-Content -LiteralPath $jsonPath -Raw
  $data = $jsonText | ConvertFrom-Json
} catch {
  Write-Host "FAIL: Strategy memory JSON did not parse."
  Write-Host $_.Exception.Message
  exit 1
}

if ($data.live_execution_status -ne "BLOCKED") {
  Write-Host "FAIL: live_execution_status must remain BLOCKED."
  exit 1
}

$numericFields = @(
  "recent_expectancy",
  "recent_profit_factor",
  "latency_penalty",
  "confidence_adjustment"
)

foreach ($field in $numericFields) {
  if (-not ($data.PSObject.Properties.Name -contains $field)) {
    Write-Host "FAIL: Missing numeric field: $field"
    exit 1
  }

  if (-not ($data.$field -is [int] -or $data.$field -is [long] -or $data.$field -is [double] -or $data.$field -is [decimal])) {
    Write-Host "FAIL: Field must be numeric: $field"
    exit 1
  }
}

if (-not $data.degradation_state) {
  Write-Host "FAIL: degradation_state must exist."
  exit 1
}

if ($data.PSObject.Properties.Name -contains "execution_allowed") {
  if ($data.execution_allowed -eq $true) {
    Write-Host "FAIL: execution_allowed must not be true."
    exit 1
  }
}

$scanFiles = @($docPath, $jsonPath, $checkpointPath)
$dangerPatterns = @(
  "api_key",
  "client_secret",
  "private_key",
  "password",
  "token",
  "webhook_url",
  "real_order",
  "order_id",
  "account_id",
  "oanda_status.*CONNECTED",
  "webhook_status.*SENT",
  "broker_status.*CONNECTED",
  "live_execution_status.*ALLOWED",
  "live_execution_enabled.*true"
)

foreach ($file in $scanFiles) {
  $content = Get-Content -LiteralPath $file -Raw
  foreach ($pattern in $dangerPatterns) {
    if ($content -match $pattern) {
      Write-Host "FAIL: Unsafe execution or credential pattern found in $file : $pattern"
      exit 1
    }
  }
}

Write-Host "PASS: AI_OS Phase 14.14 strategy memory engine passed."
Write-Host "Paper-only adaptive memory operational."
Write-Host "Unsafe execution paths remain BLOCKED."
