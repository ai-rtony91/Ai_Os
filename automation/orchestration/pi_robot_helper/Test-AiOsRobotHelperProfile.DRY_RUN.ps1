[CmdletBinding()]
param([switch]$QuietJson)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$errors = @()

function Add-Error {
    param([string]$Message)
    $script:errors += $Message
}

function Test-ParsePowerShell {
    param([string]$Path)
    $lexemes = $null
    $parseErrors = $null
    [System.Management.Automation.Language.Parser]::ParseFile($Path, [ref]$lexemes, [ref]$parseErrors) | Out-Null
    if ($parseErrors.Count -gt 0) { Add-Error "PowerShell parse failed: $Path" }
}

$profilePath = Join-Path $PSScriptRoot "AIOS_ROBOT_HELPER_PROFILE.example.json"
$previewPath = Join-Path $PSScriptRoot "Invoke-AiOsRobotHelperPreview.DRY_RUN.ps1"
$profile = Get-Content -Raw -LiteralPath $profilePath | ConvertFrom-Json
Test-ParsePowerShell $previewPath

if ([bool]$profile.hardware_enabled) { Add-Error "hardware_enabled must be false" }
if ([bool]$profile.tts_enabled) { Add-Error "tts_enabled must be false" }
if ([bool]$profile.wol_enabled) { Add-Error "wol_enabled must be false" }
if ([bool]$profile.gpio_enabled) { Add-Error "gpio_enabled must be false" }
$brightness = [int]$profile.dark_room.brightness_percent
if ($brightness -lt 0 -or $brightness -gt 100) { Add-Error "brightness_percent must be 0-100" }

$result = [ordered]@{
    schema = "AIOS_ROBOT_HELPER_PROFILE_TEST.v1"
    mode = "DRY_RUN"
    status = if ($errors.Count -eq 0) { "PASS" } else { "FAIL" }
    errors = $errors
    mutation = "NONE"
}
$result | ConvertTo-Json -Depth 8
if ($errors.Count -gt 0) { exit 1 }
exit 0
