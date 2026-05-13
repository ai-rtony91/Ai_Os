$ErrorActionPreference = "Stop"

$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
$JsonFiles = Get-ChildItem -Path $Root -Recurse -Filter "*.json"
$AllFiles = Get-ChildItem -Path $Root -Recurse -Include "*.md", "*.json"

$RequiredFiles = @(
  "AIOS_SEMANTIC_GOVERNANCE_ENGINE_001.md",
  "AIOS_CANONICAL_DEFINITION_SYSTEM_001.md",
  "definitions\AIOS_DANGEROUS_DEFINITION_001.json",
  "definitions\AIOS_SAFE_DEFINITION_001.json",
  "definitions\AIOS_UNSTABLE_DEFINITION_001.json",
  "definitions\AIOS_STABLE_DEFINITION_001.json",
  "definitions\AIOS_GOOD_EDGE_DEFINITION_001.json",
  "definitions\AIOS_WEAK_EDGE_DEFINITION_001.json",
  "definitions\AIOS_NO_EDGE_DEFINITION_001.json",
  "definitions\AIOS_RECOVERY_DEFINITION_001.json",
  "definitions\AIOS_FAKE_RECOVERY_DEFINITION_001.json",
  "definitions\AIOS_LOCKDOWN_DEFINITION_001.json",
  "definitions\AIOS_PORTFOLIO_OVERLOAD_DEFINITION_001.json",
  "definitions\AIOS_CONFIDENCE_FREEZE_DEFINITION_001.json",
  "index\AIOS_CANONICAL_DEFINITION_INDEX_001.json",
  "index\AIOS_RISK_LANGUAGE_REGISTRY_001.json",
  "index\AIOS_SEMANTIC_ALIGNMENT_MODEL_001.json",
  "reports\AIOS_SEMANTIC_CONSISTENCY_REPORT_001.md",
  "reports\AIOS_GOVERNANCE_MEMORY_REPORT_001.md"
)

$RequiredConcepts = @(
  "shared meaning consistency",
  "cross-module terminology alignment",
  "validation-reference compatibility",
  "adaptive reasoning anchors",
  "governance memory persistence",
  "machine-readable definitions",
  "skepticism consistency",
  "survivability-first semantics"
)

$RequiredCategories = @(
  "RISK",
  "CONFIDENCE",
  "EDGE",
  "REGIME",
  "PORTFOLIO",
  "EXECUTION",
  "SURVIVABILITY",
  "INSTABILITY",
  "RECOVERY",
  "MACRO"
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

foreach ($Concept in $RequiredConcepts) {
  if ($AllText -notmatch [regex]::Escape($Concept)) {
    throw "Missing governance concept: $Concept"
  }
}

foreach ($Category in $RequiredCategories) {
  if ($AllText -notmatch [regex]::Escape($Category)) {
    throw "Missing semantic category: $Category"
  }
}

Write-Host "PASS: AI_OS Stage 15.14 semantic governance validation passed."
Write-Host "Canonical semantic governance, categories, concepts, and paper-only isolation are present."

