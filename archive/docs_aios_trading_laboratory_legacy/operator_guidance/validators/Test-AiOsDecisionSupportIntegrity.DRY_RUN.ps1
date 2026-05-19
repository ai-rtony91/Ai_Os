$ErrorActionPreference = "Stop"

$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
$RepoRoot = Resolve-Path (Join-Path $Root "..\..\..\..")
$MockRoot = Join-Path $RepoRoot "apps\dashboard\mock-data"
$CssPath = Join-Path $RepoRoot "apps\dashboard\css\aios-static-preview.css"
$JsPath = Join-Path $RepoRoot "apps\dashboard\js\aios-static-preview.js"

$RequiredMocks = @(
  "aios-operator-guidance.example.json",
  "aios-survivability-guidance.example.json",
  "aios-confidence-guidance.example.json",
  "aios-risk-reduction-guidance.example.json",
  "aios-next-safe-action-guidance.example.json"
)

$RequiredExplanations = @(
  "why confidence is restricted",
  "why replay failed",
  "why ranking decreased",
  "why portfolio exposure reduced",
  "why WATCH activated",
  "why LOCKDOWN activated",
  "why Next Safe Action changed",
  "why edge distrust increased",
  "why macro risk reduced confidence"
)

$RequiredConcepts = @(
  "adaptive operator guidance",
  "explainable survivability guidance",
  "constrained-action explanation",
  "low-chaos guidance visibility",
  "replay-informed recommendations",
  "confidence-aware guidance",
  "macro-aware guidance",
  "portfolio survivability guidance"
)

$RequiredTelemetry = @(
  "guidance_state",
  "confidence_state",
  "macro_state",
  "portfolio_state",
  "warning_state",
  "replay_state",
  "next_safe_action",
  "guidance_reason",
  "freeze_triggered",
  "lockdown_triggered",
  "paper_only_status"
)

$RequiredUx = @(
  "guidance without pressure",
  "explainability before authority",
  "survivability-first recommendations",
  "calm operator workflow",
  "low cognitive overload",
  "defensive guidance behavior",
  "no hype language",
  "no execution urgency"
)

$AllText = Get-Content -LiteralPath (Join-Path $Root "AIOS_ADAPTIVE_OPERATOR_GUIDANCE_001.md") -Raw
$AllText += Get-Content -LiteralPath (Join-Path $Root "AIOS_SURVIVABILITY_DECISION_SUPPORT_001.md") -Raw
$AllText += Get-Content -LiteralPath (Join-Path $Root "reports\AIOS_GUIDANCE_EXPLAINABILITY_REPORT_001.md") -Raw
$AllText += Get-Content -LiteralPath (Join-Path $Root "reports\AIOS_OPERATOR_SURVIVABILITY_GUIDANCE_REPORT_001.md") -Raw

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
  if ($Json.hidden_live_routing_status -ne "BLOCKED") {
    throw "hidden_live_routing_status must be BLOCKED: $RelativePath"
  }
  if ($Json.network_order_routing_status -ne "BLOCKED") {
    throw "network_order_routing_status must be BLOCKED: $RelativePath"
  }
}

$AllTextLower = $AllText.ToLowerInvariant()
foreach ($Item in $RequiredExplanations + $RequiredConcepts + $RequiredUx) {
  if ($AllTextLower -notmatch [regex]::Escape($Item.ToLowerInvariant())) {
    throw "Missing required guidance language: $Item"
  }
}
foreach ($Field in $RequiredTelemetry) {
  if ($AllText -notmatch [regex]::Escape($Field)) {
    throw "Missing telemetry field: $Field"
  }
}

$Css = Get-Content -LiteralPath $CssPath -Raw
$Js = Get-Content -LiteralPath $JsPath -Raw
if ($Css -notmatch "operator-guidance") {
  throw "Dashboard CSS does not include operator-guidance styles."
}
if ($Js -notmatch "renderOperatorGuidance") {
  throw "Dashboard JS does not render operator guidance."
}
if ($Js -notmatch "aios-operator-guidance.example.json") {
  throw "Dashboard JS does not load Stage 16.4 guidance fixtures."
}

Write-Host "PASS: AI_OS Stage 16.4 decision support integrity validation passed."
Write-Host "Guidance explanations, telemetry, UX philosophy, blocked controls, and dashboard hooks are present."

