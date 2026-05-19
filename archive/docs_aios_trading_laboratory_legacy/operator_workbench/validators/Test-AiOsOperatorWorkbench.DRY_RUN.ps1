$ErrorActionPreference = "Stop"

$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
$RepoRoot = Resolve-Path (Join-Path $Root "..\..\..\..")
$MockRoot = Join-Path $RepoRoot "apps\dashboard\mock-data"

$RequiredDocs = @(
  "AIOS_OPERATOR_WORKBENCH_001.md",
  "AIOS_LOW_CHAOS_OPERATOR_MODEL_001.md",
  "reports\AIOS_OPERATOR_ERGONOMICS_REPORT_001.md",
  "reports\AIOS_LOW_COGNITIVE_LOAD_REPORT_001.md"
)

$RequiredMocks = @(
  "aios-operator-workbench.example.json",
  "aios-confidence-timeline.example.json",
  "aios-portfolio-heat.example.json",
  "aios-macro-overlay.example.json",
  "aios-chaos-alerts.example.json",
  "aios-replay-workbench.example.json"
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

$RequiredSurfaces = @(
  "top status strip",
  "replay timeline",
  "confidence timeline",
  "portfolio heat panel",
  "macro-risk overlay",
  "chaos alert surface",
  "replay scrubber placeholder",
  "edge survivability visibility",
  "Next Safe Action surface"
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

foreach ($State in $RequiredStates) {
  if ($AllText -notmatch [regex]::Escape($State)) {
    throw "Missing visible state: $State"
  }
}

foreach ($Surface in $RequiredSurfaces) {
  if ($AllText -notmatch [regex]::Escape($Surface)) {
    throw "Missing operator surface: $Surface"
  }
}

Write-Host "PASS: AI_OS Stage 16.2 operator workbench validation passed."
Write-Host "Workbench docs, mock data, visible states, operator surfaces, and paper-only safeguards are present."

