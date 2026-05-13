$ErrorActionPreference = "Stop"

$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
$RepoRoot = Resolve-Path (Join-Path $Root "..\..\..\..")
$MockRoot = Join-Path $RepoRoot "apps\dashboard\mock-data"
$AllFiles = Get-ChildItem -Path $Root -Recurse -Include "*.md", "*.json"

$RequiredFiles = @(
  "AIOS_EXPLAINABLE_INTELLIGENCE_LAYER_001.md",
  "AIOS_OPERATOR_VISIBILITY_MODEL_001.md",
  "telemetry\AIOS_VISUAL_INTELLIGENCE_TELEMETRY_001.json",
  "telemetry\AIOS_OPERATOR_EXPLANATION_TRACKER_001.json",
  "reports\AIOS_OPERATOR_EXPLAINABILITY_REPORT_001.md",
  "reports\AIOS_VISUAL_SURVIVABILITY_REPORT_001.md"
)

$RequiredMockFiles = @(
  "aios-confidence-visibility.example.json",
  "aios-edge-verification.example.json",
  "aios-macro-risk-visibility.example.json",
  "aios-chaos-prevention-visibility.example.json",
  "aios-replay-stress-visibility.example.json",
  "aios-portfolio-heatmap.example.json"
)

$RequiredStates = @(
  "CONFIDENCE_ACTIVE",
  "CONFIDENCE_FROZEN",
  "WATCH",
  "UNSTABLE",
  "LOCKDOWN",
  "GOOD_EDGE",
  "WEAK_EDGE",
  "NO_EDGE",
  "ELEVATED_RISK",
  "PORTFOLIO_OVERLOAD"
)

$RequiredTelemetry = @(
  "confidence_state",
  "edge_state",
  "macro_state",
  "portfolio_state",
  "replay_state",
  "warning_state",
  "freeze_triggered",
  "lockdown_triggered",
  "explanation_reason",
  "paper_only_status"
)

foreach ($RelativePath in $RequiredFiles) {
  $Path = Join-Path $Root $RelativePath
  if (-not (Test-Path -LiteralPath $Path)) {
    throw "Missing required file: $RelativePath"
  }
}

foreach ($RelativePath in $RequiredMockFiles) {
  $Path = Join-Path $MockRoot $RelativePath
  if (-not (Test-Path -LiteralPath $Path)) {
    throw "Missing required mock file: $RelativePath"
  }
}

$JsonFiles = @()
$JsonFiles += Get-ChildItem -Path $Root -Recurse -Filter "*.json"
foreach ($RelativePath in $RequiredMockFiles) {
  $JsonFiles += Get-Item -LiteralPath (Join-Path $MockRoot $RelativePath)
}

$AllMockFiles = @()
foreach ($RelativePath in $RequiredMockFiles) {
  $AllMockFiles += Get-Item -LiteralPath (Join-Path $MockRoot $RelativePath)
}

$AllText = ""
foreach ($File in $AllFiles) {
  $AllText += Get-Content -LiteralPath $File.FullName -Raw
}
foreach ($File in $AllMockFiles) {
  $AllText += Get-Content -LiteralPath $File.FullName -Raw
}

foreach ($File in $JsonFiles) {
  $Json = Get-Content -LiteralPath $File.FullName -Raw | ConvertFrom-Json
  if ($Json.paper_only_status -ne "PAPER_ONLY") {
    throw "paper_only_status must be PAPER_ONLY: $($File.Name)"
  }
  if ($Json.live_execution_status -ne "BLOCKED") {
    throw "live_execution_status must be BLOCKED: $($File.Name)"
  }
  if ($Json.broker_api_status -ne "BLOCKED") {
    throw "broker_api_status must be BLOCKED: $($File.Name)"
  }
}

foreach ($State in $RequiredStates) {
  if ($AllText -notmatch [regex]::Escape($State)) {
    throw "Missing visible operator state: $State"
  }
}

foreach ($Field in $RequiredTelemetry) {
  if ($AllText -notmatch [regex]::Escape($Field)) {
    throw "Missing telemetry field: $Field"
  }
}

Write-Host "PASS: AI_OS Stage 16.1 visualization layer validation passed."
Write-Host "Explainable mock data, visible states, telemetry, and paper-only safeguards are present."
