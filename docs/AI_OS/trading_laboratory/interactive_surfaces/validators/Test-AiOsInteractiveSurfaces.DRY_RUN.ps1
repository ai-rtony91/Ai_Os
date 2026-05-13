$ErrorActionPreference = "Stop"

$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
$RepoRoot = Resolve-Path (Join-Path $Root "..\..\..\..")
$MockRoot = Join-Path $RepoRoot "apps\dashboard\mock-data"

$RequiredDocs = @(
  "AIOS_INTERACTIVE_INTELLIGENCE_SURFACES_001.md",
  "AIOS_LOW_CHAOS_INTERACTION_MODEL_001.md",
  "reports\AIOS_INTERACTION_ERGONOMICS_REPORT_001.md",
  "reports\AIOS_SURVIVABILITY_INTERACTION_REPORT_001.md"
)

$RequiredMocks = @(
  "aios-freeze-timeline.example.json",
  "aios-edge-decay-visibility.example.json",
  "aios-survivability-timeline.example.json",
  "aios-replay-scenarios.example.json",
  "aios-risk-escalation.example.json",
  "aios-next-safe-action-flow.example.json"
)

$RequiredSurfaces = @(
  "confidence freeze timeline",
  "replay scrubber placeholder",
  "portfolio heat interaction",
  "edge decay inspection",
  "macro-risk overlay toggles",
  "survivability timeline",
  "freeze-trigger drilldown",
  "replay scenario switching",
  "risk escalation playback",
  "Next Safe Action interaction surface"
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

foreach ($RelativePath in $RequiredDocs) {
  $Path = Join-Path $Root $RelativePath
  if (-not (Test-Path -LiteralPath $Path)) {
    throw "Missing required doc: $RelativePath"
  }
}

$AllText = ""
foreach ($RelativePath in $RequiredDocs) {
  $AllText += Get-Content -LiteralPath (Join-Path $Root $RelativePath) -Raw
}

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
  if ($Json.live_execution_status -ne "BLOCKED") {
    throw "live_execution_status must be BLOCKED: $RelativePath"
  }
  if ($Json.broker_api_status -ne "BLOCKED") {
    throw "broker_api_status must be BLOCKED: $RelativePath"
  }
}

foreach ($Surface in $RequiredSurfaces) {
  if ($AllText -notmatch [regex]::Escape($Surface)) {
    throw "Missing interactive surface: $Surface"
  }
}

foreach ($State in $RequiredStates) {
  if ($AllText -notmatch [regex]::Escape($State)) {
    throw "Missing visible state: $State"
  }
}

Write-Host "PASS: AI_OS Stage 16.3 interactive surfaces validation passed."
Write-Host "Interactive surfaces, visible states, mock data, and paper-only safeguards are present."

