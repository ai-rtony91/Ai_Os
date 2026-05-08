$ErrorActionPreference = "Stop"

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$HtmlPath = Join-Path $RepoRoot "apps\dashboard\AIOS_STATIC_PREVIEW.html"
$JsPath = Join-Path $RepoRoot "apps\dashboard\js\aios-static-preview.js"
$CssPath = Join-Path $RepoRoot "apps\dashboard\css\aios-static-preview.css"
$FixturePath = Join-Path $RepoRoot "apps\dashboard\mock-data\lifetime-telemetry-fixture.example.json"
$BaseValidatorPath = Join-Path $RepoRoot "automation\status\Test-AiOsLifetimeDevelopmentTelemetry.DRY_RUN.ps1"

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

$Html = Read-RequiredFile -Path $HtmlPath -Label "Static dashboard HTML"
$Js = Read-RequiredFile -Path $JsPath -Label "Static dashboard JS"
$Css = Read-RequiredFile -Path $CssPath -Label "Static dashboard CSS"
$FixtureRaw = Read-RequiredFile -Path $FixturePath -Label "Lifetime telemetry fixture"
$Fixture = $null

if ($FixtureRaw) {
  try {
    $Fixture = $FixtureRaw | ConvertFrom-Json
  } catch {
    Add-Failure "Lifetime telemetry fixture is not valid JSON: $($_.Exception.Message)"
  }
}

if ($Html -and $Html -notlike '*data-status-panel-button="lifetimeTelemetry"*') {
  Add-Failure "Lifetime Telemetry status tab is missing."
}

if ($Html -and $Html -notlike '*data-status-card="lifetimeTelemetry"*') {
  Add-Failure "Lifetime Telemetry status card is missing."
}

if ($Html -and $Html -notlike '*data-lifetime-telemetry-grid*') {
  Add-Failure "Lifetime Telemetry evidence grid is missing."
}

if ($Html -and $Html -notlike '*data-lifetime-telemetry-unknowns*') {
  Add-Failure "Lifetime Telemetry UNKNOWN boundary container is missing."
}

if ($Html -and $Html -notlike '*data-lifetime-telemetry-safety*') {
  Add-Failure "Lifetime Telemetry safety container is missing."
}

$ExpectedFallbackPrefix = "Lifetime telemetry fixture unavailable"
$ExpectedFallbackSuffix = "mock data only."
if (
  ($Html -and ($Html -notlike "*$ExpectedFallbackPrefix*" -or $Html -notlike "*$ExpectedFallbackSuffix*")) -or
  ($Js -and ($Js -notlike "*$ExpectedFallbackPrefix*" -or $Js -notlike "*$ExpectedFallbackSuffix*"))
) {
  Add-Failure "Lifetime Telemetry fallback text is missing from HTML or JS."
}

if ($Js -and $Js -notlike '*const lifetimeTelemetryFixturePath = "mock-data/lifetime-telemetry-fixture.example.json"*') {
  Add-Failure "Lifetime Telemetry JS fixture path is missing or not local mock-data."
}

if ($Js -and $Js -notlike '*lifetimeTelemetry:*') {
  Add-Failure "Lifetime Telemetry status fixture registration is missing."
}

if ($Js -and $Js -notlike '*renderLifetimeTelemetryPanel*') {
  Add-Failure "Lifetime Telemetry render function is missing."
}

if ($Js -and $Js -notlike '*Complete minutes*UNKNOWN*' -and $Js -notlike '*complete_lifetime_minutes*') {
  Add-Failure "Lifetime Telemetry JS must preserve complete lifetime time as UNKNOWN from fixture data."
}

if ($Js -and $Js -notlike '*Bytes changed*' -and $Js -notlike '*complete_lifetime_bytes_changed*') {
  Add-Failure "Lifetime Telemetry JS must display complete lifetime bytes boundary."
}

if ($Css -and $Css -notlike '*.lifetime-telemetry-grid*') {
  Add-Failure "Lifetime Telemetry CSS grid class is missing."
}

if ($Css -and $Css -notlike '*.lifetime-telemetry-chip.unknown*') {
  Add-Failure "Lifetime Telemetry UNKNOWN chip styling is missing."
}

if ($Css -and $Css -notlike '*.lifetime-telemetry-chip.blocked*') {
  Add-Failure "Lifetime Telemetry blocked chip styling is missing."
}

if ($Fixture) {
  if ($Fixture.time_spent.complete_lifetime_minutes -ne "UNKNOWN") {
    Add-Failure "Fixture complete_lifetime_minutes must remain UNKNOWN."
  }

  if ($Fixture.time_spent.complete_lifetime_hours -ne "UNKNOWN") {
    Add-Failure "Fixture complete_lifetime_hours must remain UNKNOWN."
  }

  if ($Fixture.size_totals.complete_lifetime_bytes_changed -ne "UNKNOWN") {
    Add-Failure "Fixture complete_lifetime_bytes_changed must remain UNKNOWN."
  }

  if ($Fixture.size_totals.complete_lifetime_kb_changed -ne "UNKNOWN") {
    Add-Failure "Fixture complete_lifetime_kb_changed must remain UNKNOWN."
  }

  if ($Fixture.safety.fixture_only -ne $true) {
    Add-Failure "Fixture must confirm fixture_only true."
  }

  if ($Fixture.safety.real_telemetry_collector -ne $false) {
    Add-Failure "Fixture must confirm real_telemetry_collector false."
  }
}

if (-not (Test-Path -LiteralPath $BaseValidatorPath -PathType Leaf)) {
  Add-Failure "Base lifetime telemetry validator is missing."
} else {
  $BaseOutput = & powershell -ExecutionPolicy Bypass -File $BaseValidatorPath 2>&1
  if ($LASTEXITCODE -ne 0) {
    Add-Failure "Base lifetime telemetry validator failed: $($BaseOutput -join ' ')"
  }
}

$ForbiddenPatterns = @(
  "api_key\s*[:=]",
  "password\s*[:=]",
  "bearer\s+[A-Za-z0-9_\.-]+",
  "private_key\s*[:=]",
  "oanda\s+(order|trade|account|token)",
  "broker\s+order",
  "live\s+trading\s*[:=]\s*(true|enabled|on)",
  "deploy\s+(now|prod|production)",
  "winget\s+install",
  "https?://"
)

$ScopedText = @($Html, $Js, $Css) -join "`n"
foreach ($Pattern in $ForbiddenPatterns) {
  if ($ScopedText -match $Pattern) {
    Add-Failure "Forbidden dashboard lifetime telemetry pattern found: $Pattern"
  }
}

$Result = [ordered]@{
  validator = "Test-AiOsLifetimeTelemetryDashboardPanel.DRY_RUN.ps1"
  mode = "DRY_RUN"
  modifies_files = "NO"
  pass = ($Failures.Count -eq 0)
  checked_files = @(
    "apps/dashboard/AIOS_STATIC_PREVIEW.html",
    "apps/dashboard/js/aios-static-preview.js",
    "apps/dashboard/css/aios-static-preview.css",
    "apps/dashboard/mock-data/lifetime-telemetry-fixture.example.json",
    "automation/status/Test-AiOsLifetimeDevelopmentTelemetry.DRY_RUN.ps1"
  )
  fixture_path = "mock-data/lifetime-telemetry-fixture.example.json"
  fallback = "$ExpectedFallbackPrefix - $ExpectedFallbackSuffix"
  required_unknowns = @{
    complete_lifetime_time = "UNKNOWN"
    complete_lifetime_bytes = "UNKNOWN"
  }
  safety = @{
    fixture_only = "REQUIRED"
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
  Write-Host "PASS: Lifetime Telemetry dashboard panel is fixture-only and evidence-safe."
  $Result | ConvertTo-Json -Depth 5
  exit 0
}

Write-Host "FAIL: Lifetime Telemetry dashboard panel validation failed."
$Result | ConvertTo-Json -Depth 5
exit 1
