$ErrorActionPreference = "Stop"

$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
$RepoRoot = Resolve-Path (Join-Path $Root "..\..\..\..")
$MockRoot = Join-Path $RepoRoot "apps\dashboard\mock-data"
$CssPath = Join-Path $RepoRoot "apps\dashboard\css\aios-static-preview.css"
$JsPath = Join-Path $RepoRoot "apps\dashboard\js\aios-static-preview.js"

$RequiredMocks = @(
  "aios-freeze-timeline.example.json",
  "aios-edge-decay-visibility.example.json",
  "aios-survivability-timeline.example.json",
  "aios-replay-scenarios.example.json",
  "aios-risk-escalation.example.json",
  "aios-next-safe-action-flow.example.json"
)

$RequiredUx = @(
  "low chaos",
  "compact by default",
  "progressive disclosure",
  "interaction reveals depth",
  "advanced diagnostics collapsed",
  "survivability-first interaction",
  "visibility reduces hidden chaos",
  "operator-first ergonomics"
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
  "interaction_reason",
  "paper_only_status"
)

$AllText = Get-Content -LiteralPath (Join-Path $Root "AIOS_INTERACTIVE_INTELLIGENCE_SURFACES_001.md") -Raw
$AllText += Get-Content -LiteralPath (Join-Path $Root "AIOS_LOW_CHAOS_INTERACTION_MODEL_001.md") -Raw
$AllText += Get-Content -LiteralPath (Join-Path $Root "reports\AIOS_INTERACTION_ERGONOMICS_REPORT_001.md") -Raw
$AllText += Get-Content -LiteralPath (Join-Path $Root "reports\AIOS_SURVIVABILITY_INTERACTION_REPORT_001.md") -Raw

foreach ($RelativePath in $RequiredMocks) {
  $Path = Join-Path $MockRoot $RelativePath
  if (-not (Test-Path -LiteralPath $Path)) {
    throw "Missing required mock file: $RelativePath"
  }
  $Raw = Get-Content -LiteralPath $Path -Raw
  $AllText += $Raw
  $Json = $Raw | ConvertFrom-Json
  if ($Json.paper_only_status -ne "PAPER_ONLY") {
    throw "paper_only_status must be PAPER_ONLY: $RelativePath"
  }
  if ($Json.execution_controls_status -ne "BLOCKED") {
    throw "execution_controls_status must be BLOCKED: $RelativePath"
  }
  if ($Json.autonomous_controls_status -ne "BLOCKED") {
    throw "autonomous_controls_status must be BLOCKED: $RelativePath"
  }
  if ($Json.network_order_routing_status -ne "BLOCKED") {
    throw "network_order_routing_status must be BLOCKED: $RelativePath"
  }
}

$AllTextLower = $AllText.ToLowerInvariant()
foreach ($Concept in $RequiredUx) {
  if ($AllTextLower -notmatch [regex]::Escape($Concept.ToLowerInvariant())) {
    throw "Missing low-chaos interaction concept: $Concept"
  }
}
foreach ($Field in $RequiredTelemetry) {
  if ($AllText -notmatch [regex]::Escape($Field)) {
    throw "Missing telemetry field: $Field"
  }
}

$Css = Get-Content -LiteralPath $CssPath -Raw
$Js = Get-Content -LiteralPath $JsPath -Raw
if ($Css -notmatch "interactive-surfaces") {
  throw "Dashboard CSS does not include interactive-surfaces styles."
}
if ($Js -notmatch "renderInteractiveSurfaces") {
  throw "Dashboard JS does not render interactive surfaces."
}
if ($Js -notmatch "aios-freeze-timeline.example.json") {
  throw "Dashboard JS does not load Stage 16.3 interactive fixtures."
}
if ($Js -notmatch "No autoplay") {
  throw "Dashboard JS must preserve no-autoplay interaction text."
}

Write-Host "PASS: AI_OS Stage 16.3 low-chaos interaction validation passed."
Write-Host "Low-chaos interaction concepts, telemetry, blocked controls, and dashboard hooks are present."

