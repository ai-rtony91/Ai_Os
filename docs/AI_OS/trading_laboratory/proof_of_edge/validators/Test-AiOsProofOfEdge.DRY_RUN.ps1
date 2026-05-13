$ErrorActionPreference = "Stop"

$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
$JsonFiles = Get-ChildItem -Path $Root -Recurse -Filter "*.json"
$AllFiles = Get-ChildItem -Path $Root -Recurse -Include "*.md", "*.json"

$RequiredFiles = @(
  "AIOS_PROOF_OF_EDGE_LAB_001.md",
  "verification\AIOS_EDGE_VERIFICATION_MODEL_001.json",
  "verification\AIOS_EDGE_TRUST_REQUIREMENTS_001.json",
  "verification\AIOS_CONFIDENCE_PROMOTION_RULES_001.json",
  "performance\AIOS_LONG_TERM_PERFORMANCE_TRACKER_001.json",
  "performance\AIOS_EDGE_DECAY_MONITOR_001.json",
  "performance\AIOS_PORTFOLIO_SURVIVABILITY_MODEL_001.json",
  "stability\AIOS_ROLLING_STABILITY_ENGINE_001.json",
  "stability\AIOS_REGIME_STABILITY_TRACKER_001.json",
  "stability\AIOS_RECOVERY_VALIDATION_MODEL_001.json",
  "telemetry\AIOS_EDGE_PROOF_TELEMETRY_001.json",
  "telemetry\AIOS_CONFIDENCE_EVIDENCE_TRACKER_001.json",
  "reports\AIOS_EDGE_PROOF_REPORT_001.md",
  "reports\AIOS_SURVIVABILITY_AUDIT_001.md"
)

$RequiredProofStates = @(
  "UNVERIFIED",
  "PARTIALLY_VERIFIED",
  "VERIFIED_PAPER_EDGE",
  "EDGE_DECAY_DETECTED",
  "UNSTABLE",
  "RECOVERY_REQUIRED",
  "CONFIDENCE_RESTRICTED"
)

$RequiredVerificationLogic = @(
  "verify rolling expectancy",
  "verify rolling stability",
  "verify drawdown survivability",
  "verify replay survivability",
  "verify regime reliability",
  "verify portfolio survivability",
  "verify confidence freeze compliance",
  "detect edge decay",
  "detect fake recovery",
  "restrict unstable promotion"
)

$RequiredPhilosophy = @(
  "prove edge before trusting edge",
  "survivability over aggressive profit",
  "confidence must be earned slowly",
  "unstable edge must be distrusted",
  "replay survival required before promotion",
  "portfolio survivability prioritized",
  "skepticism remains permanent"
)

foreach ($RelativePath in $RequiredFiles) {
  $Path = Join-Path $Root $RelativePath
  if (-not (Test-Path -LiteralPath $Path)) {
    throw "Missing required file: $RelativePath"
  }
}

$AllText = ""
foreach ($File in $AllFiles) {
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

foreach ($State in $RequiredProofStates) {
  if ($AllText -notmatch [regex]::Escape($State)) {
    throw "Missing proof state: $State"
  }
}

foreach ($Rule in $RequiredVerificationLogic) {
  if ($AllTextLower -notmatch [regex]::Escape($Rule.ToLowerInvariant())) {
    throw "Missing verification rule: $Rule"
  }
}

foreach ($Item in $RequiredPhilosophy) {
  if ($AllTextLower -notmatch [regex]::Escape($Item.ToLowerInvariant())) {
    throw "Missing governance philosophy: $Item"
  }
}

Write-Host "PASS: AI_OS Stage 15.15 proof-of-edge validation passed."
Write-Host "Proof states, verification rules, governance philosophy, and paper-only safeguards are present."

