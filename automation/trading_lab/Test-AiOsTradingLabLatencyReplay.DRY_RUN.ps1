$ErrorActionPreference = "Stop"

Write-Host "AI_OS Trading Lab Latency Replay DRY_RUN"
Write-Host "Mode: read-only"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$resultDir = Join-Path $repoRoot "apps\trading_lab\trading_lab\results\paper_runner"
$specPath = Join-Path $repoRoot "docs\specs\trading-lab-latency-contract.md"
$dashboardFixture = Join-Path $repoRoot "apps\dashboard\mock-data\trading-lab-latency-replay.example.json"

$requiredFiles = @(
  "apps\trading_lab\trading_lab\results\paper_runner\PAPER_RESULT_LEDGER_001.json",
  "apps\trading_lab\trading_lab\results\paper_runner\PAPER_LATENCY_REPORT_001.json",
  "apps\trading_lab\trading_lab\results\paper_runner\PAPER_REGIME_RESULT_001.json",
  "apps\trading_lab\trading_lab\results\paper_runner\PAPER_RISK_GATE_RESULT_001.json",
  "apps\trading_lab\trading_lab\results\paper_runner\PAPER_SCORECARD_001.json",
  "apps\trading_lab\trading_lab\results\paper_runner\PAPER_REPLAY_LEDGER_001.json",
  "apps\trading_lab\trading_lab\results\paper_runner\PAPER_REPLAY_RESULT_001.json",
  "apps\trading_lab\trading_lab\results\paper_runner\PAPER_REPLAY_REVIEW_SUMMARY.md",
  "docs\specs\trading-lab-latency-contract.md",
  "apps\dashboard\mock-data\trading-lab-latency-replay.example.json"
)

$failures = New-Object System.Collections.Generic.List[string]

foreach ($relativePath in $requiredFiles) {
  $fullPath = Join-Path $repoRoot $relativePath
  if (-not (Test-Path -LiteralPath $fullPath)) {
    $failures.Add("Missing required file: $relativePath")
  }
}

$jsonFiles = @(
  "apps\trading_lab\trading_lab\results\paper_runner\PAPER_RESULT_LEDGER_001.json",
  "apps\trading_lab\trading_lab\results\paper_runner\PAPER_LATENCY_REPORT_001.json",
  "apps\trading_lab\trading_lab\results\paper_runner\PAPER_REGIME_RESULT_001.json",
  "apps\trading_lab\trading_lab\results\paper_runner\PAPER_RISK_GATE_RESULT_001.json",
  "apps\trading_lab\trading_lab\results\paper_runner\PAPER_SCORECARD_001.json",
  "apps\trading_lab\trading_lab\results\paper_runner\PAPER_REPLAY_LEDGER_001.json",
  "apps\trading_lab\trading_lab\results\paper_runner\PAPER_REPLAY_RESULT_001.json",
  "apps\dashboard\mock-data\trading-lab-latency-replay.example.json"
)

foreach ($relativePath in $jsonFiles) {
  $fullPath = Join-Path $repoRoot $relativePath
  if (Test-Path -LiteralPath $fullPath) {
    try {
      Get-Content -LiteralPath $fullPath -Raw | ConvertFrom-Json | Out-Null
    } catch {
      $failures.Add("JSON parse failed: $relativePath")
    }
  }
}

$specText = Get-Content -LiteralPath $specPath -Raw
$requiredSpecMarkers = @(
  "does not authorize live trading",
  "Generated Trading Lab latency results are evidence only",
  "Dashboard mock latency files are fixture-only",
  "Archive files are historical reference only",
  "Future timestamps, negative delays, and clock skew must not be treated as PASS"
)

foreach ($marker in $requiredSpecMarkers) {
  if ($specText -notmatch [regex]::Escape($marker)) {
    $failures.Add("Canonical latency spec missing required boundary marker: $marker")
  }
}

$latencyReportPath = Join-Path $resultDir "PAPER_LATENCY_REPORT_001.json"
if (Test-Path -LiteralPath $latencyReportPath) {
  $latencyReport = Get-Content -LiteralPath $latencyReportPath -Raw | ConvertFrom-Json
  $ageSeconds = [int]$latencyReport.stale_signal_check.age_seconds
  if ($ageSeconds -lt 0) {
    $expectedReplayStatus = "CLOCK_SKEW_DETECTED"
  } elseif ($ageSeconds -ge 900) {
    $expectedReplayStatus = "STALE"
  } elseif ($ageSeconds -ge 300) {
    $expectedReplayStatus = "DELAYED"
  } else {
    $expectedReplayStatus = "PASS"
  }
} else {
  $expectedReplayStatus = "MISSING_TIME_FIELD"
}

$replayResultPath = Join-Path $resultDir "PAPER_REPLAY_RESULT_001.json"
if (Test-Path -LiteralPath $replayResultPath) {
  $replayResult = Get-Content -LiteralPath $replayResultPath -Raw | ConvertFrom-Json
  if ($replayResult.clock_skew_status -ne $expectedReplayStatus -and $expectedReplayStatus -eq "CLOCK_SKEW_DETECTED") {
    $failures.Add("Replay result did not mark negative age as CLOCK_SKEW_DETECTED.")
  }
  if ($replayResult.live_execution_status -ne "BLOCKED") { $failures.Add("Replay live_execution_status is not BLOCKED.") }
  if ($replayResult.broker_status -ne "BLOCKED") { $failures.Add("Replay broker_status is not BLOCKED.") }
  if ($replayResult.oanda_status -ne "BLOCKED") { $failures.Add("Replay oanda_status is not BLOCKED.") }
  if ($replayResult.api_key_status -ne "BLOCKED") { $failures.Add("Replay api_key_status is not BLOCKED.") }
  if ($replayResult.secrets_status -ne "BLOCKED") { $failures.Add("Replay secrets_status is not BLOCKED.") }
  if ($replayResult.real_webhook_status -ne "BLOCKED") { $failures.Add("Replay real_webhook_status is not BLOCKED.") }
  if ($replayResult.real_order_status -ne "BLOCKED") { $failures.Add("Replay real_order_status is not BLOCKED.") }
}

if (Test-Path -LiteralPath $dashboardFixture) {
  $dashboard = Get-Content -LiteralPath $dashboardFixture -Raw | ConvertFrom-Json
  if ($dashboard.live_execution_status -ne "BLOCKED") { $failures.Add("Dashboard live_execution_status is not BLOCKED.") }
  if ($dashboard.broker_status -ne "BLOCKED") { $failures.Add("Dashboard broker_status is not BLOCKED.") }
  if ($dashboard.oanda_status -ne "BLOCKED") { $failures.Add("Dashboard oanda_status is not BLOCKED.") }
  if ($dashboard.api_key_status -ne "BLOCKED") { $failures.Add("Dashboard api_key_status is not BLOCKED.") }
  if ($dashboard.secrets_status -ne "BLOCKED") { $failures.Add("Dashboard secrets_status is not BLOCKED.") }
}

$scanFiles = @()
if (Test-Path -LiteralPath $resultDir) { $scanFiles += Get-ChildItem -LiteralPath $resultDir -File }
if (Test-Path -LiteralPath $specPath) { $scanFiles += Get-Item -LiteralPath $specPath }
if (Test-Path -LiteralPath $dashboardFixture) { $scanFiles += Get-Item -LiteralPath $dashboardFixture }

$combinedText = ""
foreach ($file in $scanFiles) {
  $combinedText += "`n"
  $combinedText += Get-Content -LiteralPath $file.FullName -Raw
}

$unsafePatterns = @(
  '"live_execution_status"\s*:\s*"ENABLED"',
  '"broker_status"\s*:\s*"ENABLED"',
  '"oanda_status"\s*:\s*"ENABLED"',
  '"api_key_status"\s*:\s*"ENABLED"',
  '"secrets_status"\s*:\s*"ENABLED"',
  '"real_webhook_status"\s*:\s*"ENABLED"',
  '"real_order_status"\s*:\s*"ENABLED"'
)

foreach ($pattern in $unsafePatterns) {
  if ($combinedText -match $pattern) {
    $failures.Add("Unsafe ENABLED status found for pattern: $pattern")
  }
}

if ($failures.Count -eq 0) {
  Write-Host "PASS: Latency replay files parse, clock skew is detected, and live execution remains blocked."
  exit 0
}

Write-Host "FAIL: Latency replay validation found issues."
foreach ($failure in $failures) {
  Write-Host "- $failure"
}
exit 1

