$ErrorActionPreference = "Stop"

$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
$RepoRoot = Resolve-Path (Join-Path $Root "..\..\..\..")
$MockRoot = Join-Path $RepoRoot "apps\dashboard\mock-data"

$RequiredDocs = @(
  "AIOS_ADAPTIVE_OPERATOR_GUIDANCE_001.md",
  "AIOS_SURVIVABILITY_DECISION_SUPPORT_001.md",
  "reports\AIOS_GUIDANCE_EXPLAINABILITY_REPORT_001.md",
  "reports\AIOS_OPERATOR_SURVIVABILITY_GUIDANCE_REPORT_001.md"
)

$RequiredMocks = @(
  "aios-operator-guidance.example.json",
  "aios-survivability-guidance.example.json",
  "aios-confidence-guidance.example.json",
  "aios-risk-reduction-guidance.example.json",
  "aios-next-safe-action-guidance.example.json"
)

$RequiredStates = @(
  "NORMAL",
  "CAUTION",
  "WATCH",
  "UNSTABLE",
  "LOCKDOWN",
  "CONFIDENCE_FROZEN",
  "RECOVERY_REQUIRED",
  "ELEVATED_RISK"
)

$RequiredRecommendations = @(
  "reduce simulated exposure",
  "wait for replay recovery",
  "require additional evidence",
  "avoid unstable edge",
  "reduce confidence",
  "avoid concentrated portfolio risk",
  "wait for macro stabilization",
  "maintain paper-only mode"
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
    throw "Missing guidance state: $State"
  }
}

$AllTextLower = $AllText.ToLowerInvariant()
foreach ($Recommendation in $RequiredRecommendations) {
  if ($AllTextLower -notmatch [regex]::Escape($Recommendation.ToLowerInvariant())) {
    throw "Missing recommendation: $Recommendation"
  }
}

Write-Host "PASS: AI_OS Stage 16.4 operator guidance validation passed."
Write-Host "Guidance states, recommendations, mock data, and paper-only safeguards are present."

