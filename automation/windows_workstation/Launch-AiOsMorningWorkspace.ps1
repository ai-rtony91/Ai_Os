param(
    [string]$RepoRoot = "C:\Users\mylab\OneDrive\GitHub\ai-rtony91_Ai_Os_CLEAN"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $RepoRoot)) {
    throw "RepoRoot not found: $RepoRoot"
}

$IdentityScript = Join-Path $RepoRoot "automation\window_identity\Set-AiOsWindowIdentity.ps1"

function Start-AiOsLane {
    param(
        [Parameter(Mandatory=$true)][string]$Marker
    )

    $Command = "if (Test-Path '$IdentityScript') { & '$IdentityScript' -Marker '$Marker' }; Set-Location '$RepoRoot'; git status"

    Start-Process powershell.exe `
        -WorkingDirectory $RepoRoot `
        -ArgumentList @(
            "-NoExit",
            "-ExecutionPolicy", "Bypass",
            "-Command", $Command
        )
}

Write-Host "Launching AI_OS morning workspace..."
Write-Host "RepoRoot: $RepoRoot"
Write-Host "Mode: DRY_RUN workstation launch only"
Write-Host "No commits. No pushes. No broker execution."

Start-AiOsLane -Marker "AI_OS MAIN CONTROL"
Start-Sleep -Milliseconds 500

Start-AiOsLane -Marker "CODEX BUILD LANE"
Start-Sleep -Milliseconds 500

Start-AiOsLane -Marker "VALIDATOR WORKER"
Start-Sleep -Milliseconds 500

Start-AiOsLane -Marker "APPROVAL INBOX"

Write-Host "Launch requested."
Write-Host "Use PowerToys FancyZones to snap windows into the saved morning layout."
