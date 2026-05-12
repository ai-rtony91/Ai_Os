$ErrorActionPreference = "Stop"

$RepoRoot = (Get-Location).Path
$JsonPath = Join-Path $RepoRoot "apps\trading_lab\mock-data\market_regime_engine.example.json"
$DocPath = Join-Path $RepoRoot "docs\AI_OS\trading_laboratory\phase_14_13\PHASE_14_13_MARKET_REGIME_ENGINE.md"
$CheckpointPath = Join-Path $RepoRoot "Reports\checkpoints\CHECKPOINT_PHASE_14_13_MARKET_REGIME.md"

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
  Write-Host "FAIL: market regime JSON did not parse."
  Write-Host $_.Exception.Message
  exit 1
}

if ($Data.live_execution_status -ne "BLOCKED") {
  Write-Host "FAIL: live_execution_status must be BLOCKED."
  exit 1
}

if ([string]::IsNullOrWhiteSpace($Data.regime_state)) {
  Write-Host "FAIL: regime_state must exist."
  exit 1
}

if (-not ($Data.confidence_score -is [double] -or $Data.confidence_score -is [int] -or $Data.confidence_score -is [decimal])) {
  Write-Host "FAIL: confidence_score must be numeric."
  exit 1
}

if ($Data.regime_allowed -eq $true -and $Data.live_execution_status -ne "BLOCKED") {
  Write-Host "FAIL: regime_allowed cannot bypass blocked live execution."
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

Write-Host "PASS: AI_OS Phase 14.13 market regime engine passed."
Write-Host "Paper-only regime classification operational."
Write-Host "Unsafe execution paths remain BLOCKED."
exit 0
