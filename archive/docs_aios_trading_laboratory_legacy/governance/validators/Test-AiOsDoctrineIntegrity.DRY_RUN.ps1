$ErrorActionPreference = "Stop"

$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
$JsonFiles = Get-ChildItem -Path $Root -Recurse -Filter "*.json"
$TextFiles = Get-ChildItem -Path $Root -Recurse -Include "*.md", "*.json"

$RequiredFiles = @(
  "AIOS_TRADING_DOCTRINE_001.md",
  "AIOS_RISK_PHILOSOPHY_001.md",
  "AIOS_EXECUTION_ISOLATION_CANON_001.md",
  "AIOS_CONFIDENCE_GOVERNANCE_001.md",
  "AIOS_SKEPTICAL_INTELLIGENCE_MODEL_001.md",
  "risk_language\AIOS_DANGER_DEFINITION_001.json",
  "risk_language\AIOS_EDGE_DEFINITION_001.json",
  "risk_language\AIOS_STABILITY_DEFINITION_001.json",
  "risk_language\AIOS_RECOVERY_DEFINITION_001.json",
  "risk_language\AIOS_LOCKDOWN_DEFINITION_001.json",
  "reports\AIOS_SYSTEM_SURVIVABILITY_REPORT_001.md",
  "reports\AIOS_LONG_TERM_RISK_GOVERNANCE_001.md"
)

$RequiredPrinciples = @(
  "intelligence may recommend but not execute",
  "no LLM in direct live order path",
  "confidence rises slowly and falls quickly",
  "strategies must continuously re-prove edge",
  "reject unstable strategies",
  "rolling stability required",
  "macro awareness modifies risk only",
  "execution isolation remains permanent",
  "replay testing required before trust increases",
  "edge validation required before confidence increases",
  "portfolio survivability prioritized over profit chasing",
  "skepticism is a strength",
  "preventing chaos is better than reacting late"
)

$RequiredPhilosophy = @(
  "survivability first",
  "controlled adaptation",
  "statistical skepticism",
  "evidence-gated trust",
  "confidence hysteresis",
  "portfolio-first risk thinking",
  "defensive architecture",
  "controlled complexity",
  "cautious intelligence behavior"
)

foreach ($RelativePath in $RequiredFiles) {
  $Path = Join-Path $Root $RelativePath
  if (-not (Test-Path -LiteralPath $Path)) {
    throw "Missing required file: $RelativePath"
  }
}

$AllText = ""
foreach ($File in $TextFiles) {
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

foreach ($Principle in $RequiredPrinciples) {
  if ($AllTextLower -notmatch [regex]::Escape($Principle.ToLowerInvariant())) {
    throw "Missing doctrine principle: $Principle"
  }
}

foreach ($Item in $RequiredPhilosophy) {
  if ($AllTextLower -notmatch [regex]::Escape($Item.ToLowerInvariant())) {
    throw "Missing governance philosophy: $Item"
  }
}

Write-Host "PASS: AI_OS Stage 15.13 doctrine integrity validation passed."
Write-Host "Doctrine principles, governance philosophy, and paper-only execution isolation are present."

