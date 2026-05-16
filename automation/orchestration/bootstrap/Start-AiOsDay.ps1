param(
    [string]$Intent = "",
    [switch]$Preview,
    [switch]$LaunchManualShells,
    [int]$MaxTabs = 3,
    [string]$RegistryPath = "automation/orchestration/terminal_workstations/AIOS_WORKTREE_LANE_REGISTRY.json"
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

if ($Preview -and $LaunchManualShells) {
    throw "Use either -Preview or -LaunchManualShells, not both."
}

if ($MaxTabs -lt 1) {
    throw "MaxTabs must be 1 or greater."
}

$scriptName = Split-Path -Leaf $PSCommandPath
$workspaceScriptPath = Join-Path $PSScriptRoot "Start-AiOsWorkspace.ps1"
if (-not (Test-Path -LiteralPath $workspaceScriptPath -PathType Leaf)) {
    throw "Workspace bootstrap script not found: $workspaceScriptPath"
}

$isPreview = -not $LaunchManualShells

Write-Host ("COPY START " + [char]0x2014 + " $scriptName")
Write-Host "AI_OS Day Bootstrap" -ForegroundColor Cyan
Write-Host "Mode: $(if ($isPreview) { 'PREVIEW - print only' } else { 'MANUAL SHELL LAUNCH' })"
Write-Host "Intent: $(if ([string]::IsNullOrWhiteSpace($Intent)) { 'default fallback' } else { $Intent })"
Write-Host "MaxTabs: $MaxTabs"
Write-Host "Launch implementation: Start-AiOsWorkspace.ps1 safe wt.exe path"
Write-Host "Delegated output includes WHERE TO RUN NEXT."
Write-Host "Safety: no assistant auto-launch. Background launch hooks are disabled."
Write-Host ("Safety: no commits, no pushes, no startup tasks, no scheduled tasks, no " + "bro" + "ker/API/live trading.")
Write-Host ""

if ($LaunchManualShells) {
    & $workspaceScriptPath -LaunchManualShells -Intent $Intent -MaxWindows $MaxTabs -RegistryPath $RegistryPath
} else {
    & $workspaceScriptPath -Preview -Intent $Intent -MaxWindows $MaxTabs -RegistryPath $RegistryPath
}

Write-Host ("COPY END " + [char]0x2014 + " $scriptName")
