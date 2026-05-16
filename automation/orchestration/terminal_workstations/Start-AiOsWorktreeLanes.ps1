param(
    [switch]$Preview
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$lanes = @(
    [ordered]@{
        Role = "MAIN CONTROL"
        Path = "C:\Users\mylab\OneDrive\GitHub\ai-rtony91_Ai_Os_CLEAN"
        Branch = "main"
        Color = "Magenta"
    },
    [ordered]@{
        Role = "BUILD ENGINE"
        Path = "C:\Users\mylab\OneDrive\GitHub\aios-worker-mission-json"
        Branch = "phase-221-260-mission-json-dashboard-ready"
        Color = "Green"
    },
    [ordered]@{
        Role = "VALIDATION"
        Path = "C:\Users\mylab\OneDrive\GitHub\aios-worker-validation"
        Branch = "phase-validation-cleanup"
        Color = "Cyan"
    }
)

function Write-Section {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Title
    )

    Write-Host ""
    Write-Host "== $Title ==" -ForegroundColor Yellow
}

function Get-LaneCommand {
    param(
        [Parameter(Mandatory = $true)]
        [hashtable]$Lane
    )

    $escapedPath = $Lane.Path.Replace("'", "''")
    $escapedRole = $Lane.Role.Replace("'", "''")
    $escapedBranch = $Lane.Branch.Replace("'", "''")

    return "Set-Location -LiteralPath '$escapedPath'; `$Host.UI.RawUI.WindowTitle = 'AI_OS $escapedRole'; Write-Host 'AI_OS $escapedRole' -ForegroundColor $($Lane.Color); Write-Host 'ROLE: $escapedRole'; Write-Host 'PATH: $escapedPath'; Write-Host 'BRANCH: $escapedBranch'; Write-Host 'No Codex auto-launch. No startup tasks. No scheduled tasks. No broker/API/live trading.' -ForegroundColor Red; git status --short --branch"
}

Write-Host "AI_OS WORKTREE LANE RESTORE" -ForegroundColor Yellow
Write-Host "Mode: $(if ($Preview) { 'Preview only - no windows opened' } else { 'Open PowerShell lane windows only' })"
Write-Host "No Codex auto-launch. No startup tasks. No scheduled tasks. No commits. No pushes."
Write-Host "No installs. No broker/API/live trading."

Write-Section -Title "Git Worktree List"
git worktree list

Write-Section -Title "Role / Path / Branch Mapping"
foreach ($lane in $lanes) {
    Write-Host "ROLE: $($lane.Role)" -ForegroundColor $lane.Color
    Write-Host "PATH: $($lane.Path)"
    Write-Host "BRANCH: $($lane.Branch)"
    Write-Host ""
}

Write-Section -Title "Lane Commands"
foreach ($lane in $lanes) {
    $laneCommand = Get-LaneCommand -Lane $lane
    $startCommand = "Start-Process powershell.exe -ArgumentList @('-NoExit','-ExecutionPolicy','Bypass','-Command',`"$laneCommand`")"

    Write-Host "ROLE: $($lane.Role)" -ForegroundColor $lane.Color
    Write-Host $startCommand

    if (-not $Preview) {
        if (-not (Test-Path -LiteralPath $lane.Path -PathType Container)) {
            throw "Lane path not found for $($lane.Role): $($lane.Path)"
        }

        Start-Process powershell.exe -ArgumentList @(
            "-NoExit",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            $laneCommand
        )
    }
}

if ($Preview) {
    Write-Host ""
    Write-Host "Preview complete. No PowerShell windows opened." -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "Lane windows opened. Codex was not launched." -ForegroundColor Green
}
