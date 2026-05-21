param(
    [string]$Preset = "morning"
)

$ErrorActionPreference = "Stop"

$RepoRoot = "C:\Dev\Ai-Os"
$PresetPath = Join-Path $RepoRoot "automation\windows_workstation\presets\$Preset.json"
$IdentityScript = Join-Path $RepoRoot "automation\window_identity\Set-AiOsWindowIdentity.ps1"

if (-not (Test-Path $PresetPath)) {
    throw "Preset not found: $PresetPath"
}

$PresetData = Get-Content $PresetPath | ConvertFrom-Json

Write-Host ""
Write-Host "AI_OS Workspace Launcher"
Write-Host "Preset: $($PresetData.name)"
Write-Host ""

foreach ($Worker in $PresetData.workers) {
    if ($Worker -is [string]) {
        $Marker = $Worker
    } else {
        $Marker = $Worker.marker
    }

    if ([string]::IsNullOrWhiteSpace($Marker)) {
        throw "Worker entry missing marker in preset: $PresetPath"
    }

    Write-Host "Launching: $Marker"

    Start-Process powershell.exe `
        -WorkingDirectory $RepoRoot `
        -ArgumentList @(
            "-NoExit",
            "-ExecutionPolicy", "Bypass",
            "-Command",
            "& '$IdentityScript' -Marker '$Marker'"
        )

    Start-Sleep -Milliseconds 120
}

Write-Host ""
Write-Host "Workspace launch complete."
