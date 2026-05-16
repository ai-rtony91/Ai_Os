param(
    [Parameter(Mandatory = $true)][string]$Pack,
    [switch]$Apply
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

$packPath = "automation/command_packs/packs/$Pack.json"

Write-Host "COPY START - Run-AiOsCommandPack.ps1"
Write-Host "AI_OS Command Pack Runner" -ForegroundColor Cyan
Write-Host "Mode: $(if ($Apply) { 'APPLY' } else { 'DRY_RUN' })"
Write-Host "Pack: $Pack"

if (-not (Test-Path $packPath)) {
    throw "Command pack not found: $packPath"
}

$packData = Get-Content -Raw $packPath | ConvertFrom-Json

Write-Host ""
Write-Host "Pack title: $($packData.title)"
Write-Host "Steps: $(@($packData.steps).Count)"

foreach ($step in @($packData.steps)) {
    Write-Host ""
    Write-Host "STEP $($step.id): $($step.title)" -ForegroundColor Yellow
    Write-Host "command: $($step.command)"

    if ($step.requires_apply -and -not $Apply) {
        Write-Host "Skipped: requires -Apply"
        continue
    }

    if ($Apply -or -not $step.requires_apply) {
        Invoke-Expression $step.command
    }
}

Write-Host ""
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host "COPY END - Run-AiOsCommandPack.ps1"
