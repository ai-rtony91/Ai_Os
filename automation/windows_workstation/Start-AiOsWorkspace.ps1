param(
    [string]$Preset = "morning"
)

$RepoRoot = "C:\Users\mylab\OneDrive\GitHub\ai-rtony91_Ai_Os_CLEAN"

$PresetPath = Join-Path $RepoRoot "automation\windows_workstation\presets\$Preset.json"

if (-not (Test-Path $PresetPath)) {
    throw "Preset not found: $PresetPath"
}

$PresetData = Get-Content $PresetPath | ConvertFrom-Json

$IdentityScript = Join-Path $RepoRoot "automation\window_identity\Set-AiOsWindowIdentity.ps1"

Write-Host ""
Write-Host "AI_OS Workspace Launcher"
Write-Host "Preset: $($PresetData.name)"
Write-Host ""

foreach ($Worker in $PresetData.workers) {

    Write-Host "Launching: $Worker"

    Start-Process powershell.exe `
        -WorkingDirectory $RepoRoot `
        -ArgumentList @(
            "-NoExit",
            "-ExecutionPolicy", "Bypass",
            "-Command",
            "& '$IdentityScript' -Marker '$Worker'"
        )

    Start-Sleep -Milliseconds 120
}

Write-Host ""
Write-Host "Workspace launch complete."
