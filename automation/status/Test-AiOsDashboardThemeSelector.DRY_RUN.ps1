$ErrorActionPreference = "Stop"

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$HtmlPath = Join-Path $RepoRoot "apps\dashboard\AIOS_STATIC_PREVIEW.html"
$JsPath = Join-Path $RepoRoot "apps\dashboard\js\aios-static-preview.js"
$CssPath = Join-Path $RepoRoot "apps\dashboard\css\aios-static-preview.css"

$ApprovedThemeClasses = @(
  "theme-terminal-green",
  "theme-cyan-command",
  "theme-amber-warning",
  "theme-high-contrast"
)

$RequiredCssClasses = @(
  "body.theme-terminal-green",
  "body.theme-cyan-command",
  "body.theme-amber-warning",
  "body.theme-high-contrast"
)

$ForbiddenTerms = @(
  "api_key",
  "password",
  "secret",
  "bearer",
  "private_key",
  "oanda",
  "broker",
  "deploy",
  "winget"
)

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

function Get-SelectorScopedText {
  param(
    [string]$Html,
    [string]$Js,
    [string]$Css
  )

  $HtmlLines = ($Html -split "`r?`n") | Where-Object { $_ -match "theme-selector|dashboardThemeSelector|Default AI_OS Dark|Terminal Green|Cyan Command|Amber Warning|High Contrast" }
  $JsLines = ($Js -split "`r?`n") | Where-Object { $_ -match "dashboardTheme|theme-terminal-green|theme-cyan-command|theme-amber-warning|theme-high-contrast|\[data-theme-selector\]" }
  $CssLines = ($Css -split "`r?`n") | Where-Object { $_ -match "theme-selector|theme-terminal-green|theme-cyan-command|theme-amber-warning|theme-high-contrast" }

  return @($HtmlLines + $JsLines + $CssLines) -join "`n"
}

$Html = Read-RequiredFile -Path $HtmlPath -Label "Static dashboard HTML"
$Js = Read-RequiredFile -Path $JsPath -Label "Static dashboard JS"
$Css = Read-RequiredFile -Path $CssPath -Label "Static dashboard CSS"

if ($Html) {
  Test-Contains -Content $Html -Needle 'data-theme-selector' -Message "Theme selector control markup missing."
  Test-Contains -Content $Html -Needle 'Default AI_OS Dark' -Message "Default theme option missing."
}

if ($Js) {
  Test-Contains -Content $Js -Needle '[data-theme-selector]' -Message "Theme selector JS binding missing."
  Test-Contains -Content $Js -Needle 'document.body.classList.remove(...dashboardThemeClasses)' -Message "Theme reset behavior missing."

  $ThemeRefs = [regex]::Matches($Js, "theme-[a-z-]+") | ForEach-Object { $_.Value } | Sort-Object -Unique
  $UnexpectedThemeRefs = $ThemeRefs | Where-Object { $ApprovedThemeClasses -notcontains $_ -and $_ -ne "theme-selector" }
  foreach ($ThemeRef in $UnexpectedThemeRefs) {
    Add-Failure "Unexpected JS theme reference: $ThemeRef"
  }

  foreach ($ThemeClass in $ApprovedThemeClasses) {
    Test-Contains -Content $Js -Needle $ThemeClass -Message "Approved JS theme class missing: $ThemeClass"
  }
}

if ($Css) {
  foreach ($CssClass in $RequiredCssClasses) {
    Test-Contains -Content $Css -Needle $CssClass -Message "CSS theme class missing: $CssClass"
  }
}

$SelectorScopedText = Get-SelectorScopedText -Html $Html -Js $Js -Css $Css
foreach ($Term in $ForbiddenTerms) {
  if ($SelectorScopedText -match [regex]::Escape($Term)) {
    Add-Failure "Forbidden term found in selector-specific dashboard content: $Term"
  }
}

$Result = [ordered]@{
  validator = "Test-AiOsDashboardThemeSelector.DRY_RUN.ps1"
  mode = "DRY_RUN"
  modifies_files = "NO"
  pass = ($Failures.Count -eq 0)
  checked_files = @(
    "apps/dashboard/AIOS_STATIC_PREVIEW.html",
    "apps/dashboard/js/aios-static-preview.js",
    "apps/dashboard/css/aios-static-preview.css"
  )
  approved_theme_classes = $ApprovedThemeClasses
  selector_scope_for_forbidden_terms = "theme selector/control snippets only"
  failures = @($Failures)
}

if ($Failures.Count -eq 0) {
  Write-Host "PASS: Dashboard theme selector is local-only and matches approved classes."
  $Result | ConvertTo-Json -Depth 4
  exit 0
}

Write-Host "FAIL: Dashboard theme selector validation failed."
$Result | ConvertTo-Json -Depth 4
exit 1
