$ErrorActionPreference = "Stop"

$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
$RepoRoot = Resolve-Path (Join-Path $Root "..\..\..\..")
$MockRoot = Join-Path $RepoRoot "apps\dashboard\mock-data"
$AllFiles = Get-ChildItem -Path $Root -Recurse -Include "*.md", "*.json"

$RequiredMockFiles = @(
  "aios-confidence-visibility.example.json",
  "aios-edge-verification.example.json",
  "aios-macro-risk-visibility.example.json",
  "aios-chaos-prevention-visibility.example.json",
  "aios-replay-stress-visibility.example.json",
  "aios-portfolio-heatmap.example.json"
)

$RequiredExplanations = @(
  "why confidence changed",
  "why confidence froze",
  "why ranking dropped",
  "why edge degraded",
  "why replay failed",
  "why macro risk increased",
  "why WATCH activated",
  "why LOCKDOWN activated",
  "why portfolio exposure reduced"
)

$RequiredDashboardConcepts = @(
  "explainable intelligence",
  "readable confidence state",
  "replay survivability visibility",
  "macro risk visibility",
  "portfolio heat visibility",
  "chaos prevention visibility",
  "confidence freeze timeline",
  "edge decay visibility",
  "regime reliability visibility"
)

$RequiredPhilosophy = @(
  "explainability before autonomy",
  "visible risk escalation",
  "visible confidence degradation",
  "operator-readable survivability",
  "visibility reduces hidden chaos",
  "skepticism must remain visible"
)

$JsonFiles = @()
$JsonFiles += Get-ChildItem -Path $Root -Recurse -Filter "*.json"
foreach ($RelativePath in $RequiredMockFiles) {
  $Path = Join-Path $MockRoot $RelativePath
  if (-not (Test-Path -LiteralPath $Path)) {
    throw "Missing required mock file: $RelativePath"
  }
  $JsonFiles += Get-Item -LiteralPath $Path
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
$AllTextLower = $AllText.ToLowerInvariant()

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

foreach ($Item in $RequiredExplanations) {
  if ($AllTextLower -notmatch [regex]::Escape($Item.ToLowerInvariant())) {
    throw "Missing visual explanation: $Item"
  }
}

foreach ($Item in $RequiredDashboardConcepts) {
  if ($AllTextLower -notmatch [regex]::Escape($Item.ToLowerInvariant())) {
    throw "Missing dashboard concept: $Item"
  }
}

foreach ($Item in $RequiredPhilosophy) {
  if ($AllTextLower -notmatch [regex]::Escape($Item.ToLowerInvariant())) {
    throw "Missing governance philosophy: $Item"
  }
}

Write-Host "PASS: AI_OS Stage 16.1 explainability integrity validation passed."
Write-Host "Explanations, dashboard concepts, governance philosophy, and blocked execution states are present."
