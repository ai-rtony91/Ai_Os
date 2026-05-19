$ErrorActionPreference = "Stop"

$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
$DefinitionPath = Join-Path $Root "definitions"
$DefinitionFiles = Get-ChildItem -Path $DefinitionPath -Filter "*.json"

$RequiredDefinitions = @(
  "DANGEROUS",
  "SAFE",
  "UNSTABLE",
  "STABLE",
  "GOOD_EDGE",
  "WEAK_EDGE",
  "NO_EDGE",
  "RECOVERY",
  "FAKE_RECOVERY",
  "LOCKDOWN",
  "PORTFOLIO_OVERLOAD",
  "CONFIDENCE_FREEZE"
)

$RequiredFields = @(
  "term",
  "category",
  "definition",
  "risk_implications",
  "related_terms",
  "validation_triggers",
  "behavioral_effects",
  "paper_only_status",
  "live_execution_status"
)

$SeenDefinitions = @{}

foreach ($File in $DefinitionFiles) {
  $Json = Get-Content -LiteralPath $File.FullName -Raw | ConvertFrom-Json
  foreach ($Field in $RequiredFields) {
    if (-not ($Json.PSObject.Properties.Name -contains $Field)) {
      throw "Missing field '$Field' in $($File.Name)"
    }
  }
  if ($Json.paper_only_status -ne "PAPER_ONLY") {
    throw "paper_only_status must be PAPER_ONLY: $($File.Name)"
  }
  if ($Json.live_execution_status -ne "BLOCKED") {
    throw "live_execution_status must be BLOCKED: $($File.Name)"
  }
  $SeenDefinitions[$Json.term] = $true
}

foreach ($Definition in $RequiredDefinitions) {
  if (-not $SeenDefinitions.ContainsKey($Definition)) {
    throw "Missing operational definition: $Definition"
  }
}

Write-Host "PASS: AI_OS Stage 15.14 definition integrity validation passed."
Write-Host "Operational definitions, required fields, and blocked live execution status are present."

