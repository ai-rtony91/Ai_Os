$ErrorActionPreference = "Stop"

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$EvidenceModelPath = Join-Path $RepoRoot "docs\AI_OS\telemetry\AIOS_LIFETIME_DEVELOPMENT_TELEMETRY_EVIDENCE_MODEL_DRAFT.md"
$StorageContractPath = Join-Path $RepoRoot "docs\AI_OS\telemetry\AIOS_LIFETIME_DEVELOPMENT_TELEMETRY_STORAGE_CONTRACT_DRAFT.md"
$FixturePath = Join-Path $RepoRoot "apps\dashboard\mock-data\lifetime-telemetry-fixture.example.json"

$Failures = New-Object System.Collections.Generic.List[string]

function Add-Failure {
  param([string]$Message)
  $Failures.Add($Message) | Out-Null
}

function Read-RequiredFile {
  param(
    [string]$Path,
    [string]$Label
  )

  if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
    Add-Failure "$Label missing: $Path"
    return ""
  }

  return Get-Content -LiteralPath $Path -Raw
}

$EvidenceModel = Read-RequiredFile -Path $EvidenceModelPath -Label "Lifetime telemetry evidence model"
$StorageContract = Read-RequiredFile -Path $StorageContractPath -Label "Lifetime telemetry storage contract"
$FixtureRaw = Read-RequiredFile -Path $FixturePath -Label "Lifetime telemetry fixture"
$Fixture = $null

if ($FixtureRaw) {
  try {
    $Fixture = $FixtureRaw | ConvertFrom-Json
  } catch {
    Add-Failure "Lifetime telemetry fixture is not valid JSON: $($_.Exception.Message)"
  }
}

if ($EvidenceModel -and $EvidenceModel -notlike "*Complete lifetime time spent*UNKNOWN*") {
  Add-Failure "Evidence model must mark complete lifetime time spent as UNKNOWN."
}

if ($StorageContract -and $StorageContract -notlike "*No Real Collectors*") {
  Add-Failure "Storage contract must include no-real-collectors boundary."
}

if ($Fixture) {
  if ($Fixture.time_spent.complete_lifetime_minutes -ne "UNKNOWN") {
    Add-Failure "Fixture must keep complete_lifetime_minutes as UNKNOWN."
  }

  if ($Fixture.time_spent.complete_lifetime_hours -ne "UNKNOWN") {
    Add-Failure "Fixture must keep complete_lifetime_hours as UNKNOWN."
  }

  if ($Fixture.size_totals.complete_lifetime_bytes_changed -ne "UNKNOWN") {
    Add-Failure "Fixture must keep complete_lifetime_bytes_changed as UNKNOWN."
  }

  if ($Fixture.size_totals.complete_lifetime_kb_changed -ne "UNKNOWN") {
    Add-Failure "Fixture must keep complete_lifetime_kb_changed as UNKNOWN."
  }

  if ($Fixture.safety.real_telemetry_collector -ne $false) {
    Add-Failure "Fixture must confirm real_telemetry_collector is false."
  }

  if ($Fixture.git_totals.commit_count -ne 187) {
    Add-Failure "Fixture commit_count does not match Stage 37 observed evidence."
  }
}

$ForbiddenPatterns = @(
  "api_key\s*[:=]",
  "password\s*[:=]",
  "secret\s*[:=]",
  "bearer\s+[A-Za-z0-9_\.-]+",
  "private_key\s*[:=]",
  "oanda\s+(order|trade|account|token)",
  "broker\s+order",
  "live\s+trading\s*[:=]\s*(true|enabled|on)",
  "deploy\s+(now|prod|production)",
  "winget\s+install"
)

$ScopedText = @($EvidenceModel, $StorageContract, $FixtureRaw) -join "`n"
foreach ($Pattern in $ForbiddenPatterns) {
  if ($ScopedText -match $Pattern) {
    Add-Failure "Forbidden lifetime telemetry pattern found: $Pattern"
  }
}

$Result = [ordered]@{
  validator = "Test-AiOsLifetimeDevelopmentTelemetry.DRY_RUN.ps1"
  mode = "DRY_RUN"
  modifies_files = "NO"
  pass = ($Failures.Count -eq 0)
  checked_files = @(
    "docs/AI_OS/telemetry/AIOS_LIFETIME_DEVELOPMENT_TELEMETRY_EVIDENCE_MODEL_DRAFT.md",
    "docs/AI_OS/telemetry/AIOS_LIFETIME_DEVELOPMENT_TELEMETRY_STORAGE_CONTRACT_DRAFT.md",
    "apps/dashboard/mock-data/lifetime-telemetry-fixture.example.json"
  )
  required_unknowns = @{
    complete_lifetime_time = "UNKNOWN"
    complete_lifetime_bytes = "UNKNOWN"
  }
  safety = @{
    real_telemetry_collectors = "BLOCKED"
    apis = "BLOCKED"
    secrets = "BLOCKED"
    deployment = "BLOCKED"
    broker_trading_execution = "BLOCKED"
    live_ai_execution = "BLOCKED"
  }
  failures = @($Failures)
}

if ($Failures.Count -eq 0) {
  Write-Host "PASS: Lifetime development telemetry fixture and contracts are evidence-safe."
  $Result | ConvertTo-Json -Depth 5
  exit 0
}

Write-Host "FAIL: Lifetime development telemetry validation failed."
$Result | ConvertTo-Json -Depth 5
exit 1
