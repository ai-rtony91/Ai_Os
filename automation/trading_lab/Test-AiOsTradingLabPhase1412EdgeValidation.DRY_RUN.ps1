$ErrorActionPreference = "Stop"

$RepoRoot = (Get-Location).Path
$JsonPath = Join-Path $RepoRoot "apps\trading_lab\mock-data\edge_validation_engine.example.json"
# Historical/reference-only evidence. These archive files are not current authority
# and are not active Reports/checkpoints output.
$DocPath = Join-Path $RepoRoot "archive\docs_aios_trading_laboratory_legacy\phase_14_12\PHASE_14_12_EDGE_VALIDATION_ENGINE.md"
$CheckpointPath = Join-Path $RepoRoot "archive\reports_legacy\checkpoints\CHECKPOINT_PHASE_14_12_EDGE_VALIDATION.md"

# This validator provides evidence only. It does not approve live trading, broker
# execution, real webhooks, real orders, credentials, APPLY, commit, push, merge,
# or deployment.

$RequiredFiles = @(
  $JsonPath,
  $DocPath,
  $CheckpointPath
)

foreach ($Path in $RequiredFiles) {
  if (-not (Test-Path -LiteralPath $Path)) {
    Write-Host "FAIL: Missing required file: $Path"
    exit 1
  }
}

try {
  $JsonText = Get-Content -LiteralPath $JsonPath -Raw
  $Data = $JsonText | ConvertFrom-Json
} catch {
  Write-Host "FAIL: edge validation JSON did not parse."
  Write-Host $_.Exception.Message
  exit 1
}

if ($Data.live_execution_status -ne "BLOCKED") {
  Write-Host "FAIL: live_execution_status must be BLOCKED."
  exit 1
}

if ($Data.trade_allowed -eq $true) {
  Write-Host "FAIL: trade_allowed must not be true."
  exit 1
}

if (-not ($Data.expectancy_score -is [double] -or $Data.expectancy_score -is [int] -or $Data.expectancy_score -is [decimal])) {
  Write-Host "FAIL: expectancy_score must be numeric."
  exit 1
}

if (-not ($Data.confidence_score -is [double] -or $Data.confidence_score -is [int] -or $Data.confidence_score -is [decimal])) {
  Write-Host "FAIL: confidence_score must be numeric."
  exit 1
}

$ForbiddenPatterns = @(
  "broker\s*[:=]\s*(connected|enabled|true)",
  "webhook\s*[:=]\s*(sent|enabled|true)",
  "oanda\s*[:=]\s*(connected|enabled|true)",
  "api[_ -]?key\s*[:=]",
  "secret\s*[:=]",
  "live[_ -]?execution\s*[:=]\s*(enabled|allowed|true)"
)

foreach ($Pattern in $ForbiddenPatterns) {
  if ($JsonText -match $Pattern) {
    Write-Host "FAIL: Forbidden unsafe execution pattern found in JSON: $Pattern"
    exit 1
  }
}

Write-Host "PASS: AI_OS Phase 14.12 edge validation engine passed."
Write-Host "Paper-only edge scoring operational."
Write-Host "Unsafe execution paths remain BLOCKED."
exit 0
