[CmdletBinding()]
param([switch]$QuietJson)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$errors = @()

function Add-Error {
    param([string]$Message)
    $script:errors += $Message
}

function Read-Json {
    param([string]$Path)
    return Get-Content -Raw -LiteralPath $Path | ConvertFrom-Json
}

function Test-ParsePowerShell {
    param([string]$Path)
    $lexemes = $null
    $parseErrors = $null
    [System.Management.Automation.Language.Parser]::ParseFile($Path, [ref]$lexemes, [ref]$parseErrors) | Out-Null
    if ($parseErrors.Count -gt 0) { Add-Error "PowerShell parse failed: $Path" }
}

$profile12Path = Join-Path $PSScriptRoot "AIOS_12H_MODE_PROFILE.example.json"
$profile24Path = Join-Path $PSScriptRoot "AIOS_24H_VACATION_MODE_PROFILE.example.json"
$preview12Path = Join-Path $PSScriptRoot "Invoke-AiOs12HModePreview.DRY_RUN.ps1"
$preview24Path = Join-Path $PSScriptRoot "Invoke-AiOsVacationModePreview.DRY_RUN.ps1"

$p12 = Read-Json $profile12Path
$p24 = Read-Json $profile24Path
Test-ParsePowerShell $preview12Path
Test-ParsePowerShell $preview24Path

if ([int]$p12.duration_hours -ne 12) { Add-Error "12H duration is not 12" }
if ([int]$p24.duration_hours -ne 24) { Add-Error "24H duration is not 24" }
foreach ($flag in @("paper_mode_only", "no_executor", "no_scheduler", "no_hardware")) {
    if (-not [bool]$p12.$flag) { Add-Error "12H safety flag false: $flag" }
}
foreach ($flag in @("paper_mode_only", "report_only", "no_executor", "no_scheduler", "no_broker")) {
    if (-not [bool]$p24.$flag) { Add-Error "24H safety flag false: $flag" }
}

$blocked = @($p12.blocked_actions) -join "|"
foreach ($term in @("scheduler_registration", "hardware_access", "real_notification_delivery", "live_trading", "paper_trading_execution", "backtest_execution", "strategy_optimization")) {
    if ($blocked -notmatch [regex]::Escape($term)) { Add-Error "blocked action missing: $term" }
}

$result = [ordered]@{
    schema = "AIOS_12H_24H_MODE_READINESS.v1"
    mode = "DRY_RUN"
    status = if ($errors.Count -eq 0) { "PASS" } else { "FAIL" }
    errors = $errors
    checked_files = @($profile12Path, $profile24Path, $preview12Path, $preview24Path)
    mutation = "NONE"
}
$result | ConvertTo-Json -Depth 8
if ($errors.Count -gt 0) { exit 1 }
exit 0
