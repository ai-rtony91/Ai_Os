param(
  [string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
)

$ErrorActionPreference = "Stop"

# Archive docs referenced below are historical/reference-only evidence, not current authority.
# This DRY_RUN validator does not approve live trading, broker execution, real webhooks, real orders, credentials, APPLY, commit, push, merge, or deployment.
$failures = New-Object System.Collections.Generic.List[string]

function Add-Failure {
  param([string]$Message)
  $script:failures.Add($Message) | Out-Null
}

Push-Location $RepoRoot
try {
  $fixtureRoot = "apps/trading_lab/trading_lab/fixtures/paper_runner"
  $resultRoot = "apps/trading_lab/trading_lab/results/paper_runner"
  $requiredFiles = @(
    "apps/trading_lab/trading_lab/runner/__init__.py",
    "apps/trading_lab/trading_lab/runner/paper_bot_runner.py",
    "$fixtureRoot/PAPER_SIGNAL_FIXTURE_001.json",
    "$fixtureRoot/PAPER_CANDLE_FIXTURE_001.json",
    "$fixtureRoot/PAPER_REGIME_FIXTURE_001.json",
    "$fixtureRoot/PAPER_EVIDENCE_FIXTURE_001.json",
    "$fixtureRoot/README.md",
    "$resultRoot/PAPER_RESULT_LEDGER_001.json",
    "$resultRoot/PAPER_SCORECARD_001.json",
    "$resultRoot/PAPER_LATENCY_REPORT_001.json",
    "$resultRoot/PAPER_RISK_GATE_RESULT_001.json",
    "$resultRoot/PAPER_REGIME_RESULT_001.json",
    "$resultRoot/PAPER_VALIDATION_REPORT_001.json",
    "$resultRoot/PAPER_NEXT_ACTION.md",
    "archive/docs_aios_trading_laboratory_legacy/phase_15_4/PHASE_15_4_TRADING_LAB_PAPER_BOT_RUNNER.md",
    "archive/docs_aios_trading_laboratory_legacy/phase_15_4/PAPER_RUNNER_CONTRACT.json",
    "apps/dashboard/mock-data/trading-lab-paper-runner.example.json"
  )

  foreach ($file in $requiredFiles) {
    if (-not (Test-Path -LiteralPath $file)) {
      Add-Failure "Missing required file: $file"
    }
  }

  if ($failures.Count -eq 0) {
    $env:PYTHONPATH = (Join-Path $RepoRoot "apps/trading_lab")
    python -m trading_lab.runner.paper_bot_runner --json | Out-Null
    if ($LASTEXITCODE -ne 0) {
      Add-Failure "Paper runner returned non-zero exit code: $LASTEXITCODE"
    }
  }

  $jsonFiles = @()
  foreach ($root in @($fixtureRoot, $resultRoot, "archive/docs_aios_trading_laboratory_legacy/phase_15_4")) {
    if (Test-Path -LiteralPath $root) {
      $jsonFiles += Get-ChildItem -LiteralPath $root -Filter "*.json" -File
    }
  }
  $jsonFiles += Get-Item -LiteralPath "apps/dashboard/mock-data/trading-lab-paper-runner.example.json"

  foreach ($jsonFile in $jsonFiles) {
    try {
      Get-Content -Raw -LiteralPath $jsonFile.FullName | ConvertFrom-Json | Out-Null
    } catch {
      Add-Failure "JSON parse failed: $($jsonFile.FullName)"
    }
  }

  $validation = Get-Content -Raw -LiteralPath "$resultRoot/PAPER_VALIDATION_REPORT_001.json" | ConvertFrom-Json
  $ledger = Get-Content -Raw -LiteralPath "$resultRoot/PAPER_RESULT_LEDGER_001.json" | ConvertFrom-Json
  $scorecard = Get-Content -Raw -LiteralPath "$resultRoot/PAPER_SCORECARD_001.json" | ConvertFrom-Json
  $risk = Get-Content -Raw -LiteralPath "$resultRoot/PAPER_RISK_GATE_RESULT_001.json" | ConvertFrom-Json
  $regime = Get-Content -Raw -LiteralPath "$resultRoot/PAPER_REGIME_RESULT_001.json" | ConvertFrom-Json
  $latency = Get-Content -Raw -LiteralPath "$resultRoot/PAPER_LATENCY_REPORT_001.json" | ConvertFrom-Json

  if ($validation.result -ne "PASS") { Add-Failure "Validation report result is not PASS." }
  if ($ledger.paper_decision -notin @("BLOCKED", "PAPER_SIMULATED")) { Add-Failure "Ledger paper decision is invalid." }
  if ($scorecard.review_status -notin @("READY_FOR_REVIEW", "BLOCKED")) { Add-Failure "Scorecard review status is invalid." }
  if ($risk.risk_gate_status -notin @("PASS", "BLOCKED")) { Add-Failure "Risk gate status is invalid." }
  if ($regime.regime_check_status -notin @("PASS", "BLOCKED")) { Add-Failure "Regime status is invalid." }
  if ($latency.stale_signal_check.stale_signal_status -notin @("PASS", "BLOCKED")) { Add-Failure "Stale signal status is invalid." }

  $combinedText = foreach ($file in $requiredFiles) {
    if (Test-Path -LiteralPath $file) {
      Get-Content -Raw -LiteralPath $file
    }
  }
  $text = ($combinedText -join "`n")

  foreach ($marker in @("BLOCKED", "No broker", "No external account connection", "No API keys", "No real webhooks", "No real orders")) {
    if ($text -notmatch [regex]::Escape($marker)) {
      Add-Failure "Missing safety marker: $marker"
    }
  }

  foreach ($unsafePattern in @("live_execution_status.*ENABLED", "broker_status.*ENABLED", "place_order", "real_order.*ENABLED", "real_webhook.*ENABLED")) {
    if ($text -match $unsafePattern) {
      Add-Failure "Unsafe enabled pattern found: $unsafePattern"
    }
  }

  if ($failures.Count -gt 0) {
    Write-Output "AI_OS Trading Lab Paper Runner DRY_RUN: FAIL"
    $failures | ForEach-Object { Write-Output "FAIL: $_" }
    exit 1
  }

  Write-Output "AI_OS Trading Lab Paper Runner DRY_RUN: PASS"
  Write-Output "Required files: PASS"
  Write-Output "Runner execution: PASS"
  Write-Output "JSON parse: PASS"
  Write-Output "Paper decision: $($ledger.paper_decision)"
  Write-Output "Risk gate: $($risk.risk_gate_status)"
  Write-Output "Regime check: $($regime.regime_check_status)"
  Write-Output "Safety: paper-only local fixtures; execution remains blocked."
} finally {
  Pop-Location
}
