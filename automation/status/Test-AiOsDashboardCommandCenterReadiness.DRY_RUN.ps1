$ErrorActionPreference = "Stop"

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$HtmlPath = Join-Path $RepoRoot "apps\dashboard\AIOS_STATIC_PREVIEW.html"
$JsPath = Join-Path $RepoRoot "apps\dashboard\js\aios-static-preview.js"
$CssPath = Join-Path $RepoRoot "apps\dashboard\css\aios-static-preview.css"
$Stage29DocPath = Join-Path $RepoRoot "docs\concepts\aios-dashboard-and-interface-concepts.md"
$Stage30DocPath = Join-Path $RepoRoot "docs\specs\aios-dashboard-data-contracts.md"

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

function Test-Contains {
  param(
    [string]$Content,
    [string]$Needle,
    [string]$Message
  )

  if ($Content -notlike "*$Needle*") {
    Add-Failure $Message
  }
}

$Html = Read-RequiredFile -Path $HtmlPath -Label "Static dashboard HTML"
$Js = Read-RequiredFile -Path $JsPath -Label "Static dashboard JS"
$Css = Read-RequiredFile -Path $CssPath -Label "Static dashboard CSS"
$Stage29Doc = Read-RequiredFile -Path $Stage29DocPath -Label "canonical dashboard concept summary"
$Stage30Doc = Read-RequiredFile -Path $Stage30DocPath -Label "canonical dashboard data contract spec"

if ($Html) {
  $RequiredHtmlMarkers = @(
    "command-sidebar",
    "status-strip",
    "status-panel-system",
    "work-table",
    "work-table-ai-panel",
    "registry-section",
    "assistant-rail",
    "console-panel"
  )

  foreach ($Marker in $RequiredHtmlMarkers) {
    Test-Contains -Content $Html -Needle $Marker -Message "Static dashboard control area missing: $Marker"
  }

  $RequiredSafeLabels = @(
    "No backend/API calls",
    "No persistence or service-worker registration",
    "No broker/trading automation",
    "LOCAL MOCK ONLY"
  )

  foreach ($Label in $RequiredSafeLabels) {
    Test-Contains -Content $Html -Needle $Label -Message "Required dashboard safety label missing: $Label"
  }
}

if ($Stage29Doc) {
  Test-Contains -Content $Stage29Doc -Needle "command-center" -Message "Canonical dashboard concept summary missing command-center concept."
  Test-Contains -Content $Stage29Doc -Needle "approval" -Message "Canonical dashboard concept summary missing approval concept."
}

if ($Stage30Doc) {
  Test-Contains -Content $Stage30Doc -Needle "Command Center" -Message "Canonical dashboard data contract missing command center contract."
  Test-Contains -Content $Stage30Doc -Needle "AI Assistant Panel Contract" -Message "Canonical dashboard data contract missing AI assistant panel contract."
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

$CommandCenterScopedText = @(
  $Stage29Doc,
  $Stage30Doc,
  ($Html -split "`r?`n" | Where-Object { $_ -match "command-sidebar|status-strip|status-panel-system|work-table|work-table-ai-panel|registry-section|assistant-rail|console-panel|No backend/API calls|No persistence|No broker|LOCAL MOCK ONLY" }) -join "`n",
  ($Js -split "`r?`n" | Where-Object { $_ -match "data-action|statusPanel|messages|send-message|loadStatusOverview|loadToolRegistryStatus|loadWorkTableAiInsights" }) -join "`n",
  ($Css -split "`r?`n" | Where-Object { $_ -match "status-strip|status-panel|work-table|assistant-rail|registry-section|console-panel" }) -join "`n"
) -join "`n"

foreach ($Pattern in $ForbiddenPatterns) {
  if ($CommandCenterScopedText -match $Pattern) {
    Add-Failure "Forbidden command-center pattern found: $Pattern"
  }
}

$Result = [ordered]@{
  validator = "Test-AiOsDashboardCommandCenterReadiness.DRY_RUN.ps1"
  mode = "DRY_RUN"
  modifies_files = "NO"
  pass = ($Failures.Count -eq 0)
  checked_files = @(
    "apps/dashboard/AIOS_STATIC_PREVIEW.html",
    "apps/dashboard/js/aios-static-preview.js",
    "apps/dashboard/css/aios-static-preview.css",
    "docs/concepts/aios-dashboard-and-interface-concepts.md",
    "docs/specs/aios-dashboard-data-contracts.md"
  )
  safety = @{
    apis = "BLOCKED"
    secrets = "BLOCKED"
    deployment = "BLOCKED"
    broker_trading_execution = "BLOCKED"
    live_ai_execution = "BLOCKED"
  }
  failures = @($Failures)
}

if ($Failures.Count -eq 0) {
  Write-Host "PASS: Dashboard command-center readiness checks passed."
  $Result | ConvertTo-Json -Depth 5
  exit 0
}

Write-Host "FAIL: Dashboard command-center readiness checks failed."
$Result | ConvertTo-Json -Depth 5
exit 1
