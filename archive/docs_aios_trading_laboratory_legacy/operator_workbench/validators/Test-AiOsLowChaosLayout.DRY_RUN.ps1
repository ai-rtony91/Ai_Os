$ErrorActionPreference = "Stop"

$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
$RepoRoot = Resolve-Path (Join-Path $Root "..\..\..\..")
$MockRoot = Join-Path $RepoRoot "apps\dashboard\mock-data"
$CssPath = Join-Path $RepoRoot "apps\dashboard\css\aios-static-preview.css"
$JsPath = Join-Path $RepoRoot "apps\dashboard\js\aios-static-preview.js"

$RequiredMocks = @(
  "aios-operator-workbench.example.json",
  "aios-confidence-timeline.example.json",
  "aios-portfolio-heat.example.json",
  "aios-macro-overlay.example.json",
  "aios-chaos-alerts.example.json",
  "aios-replay-workbench.example.json"
)

$RequiredConcepts = @(
  "explainable intelligence",
  "confidence visibility",
  "macro-risk visibility",
  "replay survivability visibility",
  "portfolio heat visibility",
  "confidence freeze visibility",
  "edge decay visibility",
  "chaos-prevention visibility",
  "replay timeline visibility",
  "Next Safe Action visibility"
)

$RequiredUx = @(
  "low chaos",
  "progressive disclosure",
  "simple front surface",
  "deep drill-downs",
  "visibility reduces hidden chaos",
  "operator-first ergonomics",
  "cognitive-load reduction",
  "survivability-first UX"
)

$AllText = Get-Content -LiteralPath (Join-Path $Root "AIOS_OPERATOR_WORKBENCH_001.md") -Raw
$AllText += Get-Content -LiteralPath (Join-Path $Root "AIOS_LOW_CHAOS_OPERATOR_MODEL_001.md") -Raw
$AllText += Get-Content -LiteralPath (Join-Path $Root "reports\AIOS_OPERATOR_ERGONOMICS_REPORT_001.md") -Raw
$AllText += Get-Content -LiteralPath (Join-Path $Root "reports\AIOS_LOW_COGNITIVE_LOAD_REPORT_001.md") -Raw

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
foreach ($Concept in $RequiredConcepts) {
  if ($AllTextLower -notmatch [regex]::Escape($Concept.ToLowerInvariant())) {
    throw "Missing UI concept: $Concept"
  }
}
foreach ($Concept in $RequiredUx) {
  if ($AllTextLower -notmatch [regex]::Escape($Concept.ToLowerInvariant())) {
    throw "Missing UX philosophy: $Concept"
  }
}

$Css = Get-Content -LiteralPath $CssPath -Raw
$Js = Get-Content -LiteralPath $JsPath -Raw
if ($Css -notmatch "operator-workbench") {
  throw "Dashboard CSS does not include operator-workbench styles."
}
if ($Js -notmatch "renderOperatorWorkbench") {
  throw "Dashboard JS does not render the operator workbench."
}
if ($Js -notmatch "operator-workbench.example.json") {
  throw "Dashboard JS does not load the operator workbench fixture."
}

Write-Host "PASS: AI_OS Stage 16.2 low-chaos layout validation passed."
Write-Host "Low-chaos concepts, blocked controls, collapsed detail behavior, and dashboard workbench hooks are present."

