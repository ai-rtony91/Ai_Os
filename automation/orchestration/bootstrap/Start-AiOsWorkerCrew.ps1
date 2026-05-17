param(
    [ValidateSet("Core", "Standard", "All")]
    [string]$Crew = "Standard",
    [switch]$Preview,
    [int]$MaxWindows = 10,
    [string]$RegistryPath = "automation/orchestration/terminal_workstations/AIOS_WORKTREE_LANE_REGISTRY.json"
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

function Resolve-AiOsPath {
    param([Parameter(Mandatory = $true)][string]$Path)

    if ([System.IO.Path]::IsPathRooted($Path)) {
        return $Path
    }

    return Join-Path (Get-Location).Path $Path
}

function Get-LaneById {
    param(
        [Parameter(Mandatory = $true)]$Registry,
        [Parameter(Mandatory = $true)][string]$LaneId
    )

    return @($Registry.lanes) | Where-Object { $_.lane_id -eq $LaneId } | Select-Object -First 1
}

function Get-LaneCommand {
    param(
        [Parameter(Mandatory = $true)]$Lane,
        [Parameter(Mandatory = $true)][string]$IdentityScriptPath
    )

    $escapedPath = $Lane.path.Replace("'", "''")
    $escapedIdentityScriptPath = $IdentityScriptPath.Replace("'", "''")
    $laneJson = $Lane | ConvertTo-Json -Depth 12 -Compress
    $laneJsonBase64 = [System.Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($laneJson))

    return "Set-Location -LiteralPath '$escapedPath'; & '$escapedIdentityScriptPath' -LaneJsonBase64 '$laneJsonBase64'; Write-Host 'Trust path + branch first. Window title is only a label.' -ForegroundColor Yellow; git status --short --branch"
}

function Get-OpenArgs {
    param(
        [Parameter(Mandatory = $true)]$Lane,
        [Parameter(Mandatory = $true)][string]$IdentityScriptPath
    )

    $args = @(
        "-w", "0",
        "new-tab",
        "--title", $Lane.tab_title
    )

    if (($Lane.PSObject.Properties.Name -contains "tab_color") -and -not [string]::IsNullOrWhiteSpace($Lane.tab_color)) {
        $args += @("--tabColor", $Lane.tab_color)
    }

    $args += @(
        "powershell.exe",
        "-NoExit",
        "-ExecutionPolicy",
        "Bypass",
        "-Command",
        (Get-LaneCommand -Lane $Lane -IdentityScriptPath $IdentityScriptPath)
    )

    return $args
}

$registryFullPath = Resolve-AiOsPath -Path $RegistryPath
if (-not (Test-Path -LiteralPath $registryFullPath -PathType Leaf)) {
    throw "Lane registry not found: $registryFullPath"
}

$identityScriptPath = Join-Path $PSScriptRoot "Set-AiOsTerminalIdentity.ps1"
if (-not (Test-Path -LiteralPath $identityScriptPath -PathType Leaf)) {
    throw "Terminal identity helper not found: $identityScriptPath"
}

$registry = Get-Content -LiteralPath $registryFullPath -Raw | ConvertFrom-Json

$coreLaneIds = @(
    "main_control",
    "codex_build_lane",
    "validator_worker",
    "packet_queue",
    "approval_inbox",
    "save_git"
)

$standardLaneIds = @(
    "main_control",
    "codex_build_lane",
    "validator_worker",
    "packet_queue",
    "approval_inbox",
    "recovery_health",
    "watch_state",
    "save_git",
    "standby_worker"
)

$allLaneIds = @($registry.lanes | ForEach-Object { $_.lane_id })

$selectedLaneIds = switch ($Crew) {
    "Core" { $coreLaneIds }
    "Standard" { $standardLaneIds }
    "All" { $allLaneIds }
}

$selectedLanes = @()
foreach ($laneId in $selectedLaneIds) {
    $lane = Get-LaneById -Registry $registry -LaneId $laneId
    if ($null -eq $lane) {
        throw "Missing lane in registry: $laneId"
    }
    $selectedLanes += $lane
}

Write-Host "AI_OS Worker Crew Launcher" -ForegroundColor Cyan
Write-Host "Crew: $Crew"
Write-Host "Mode: $(if ($Preview) { 'PREVIEW - no windows opened' } else { 'LAUNCH - opens colored Windows Terminal tabs' })"
Write-Host "Registry: $registryFullPath"
Write-Host "MaxWindows: $MaxWindows"
Write-Host "Safety: no Codex auto-run, no commits, no pushes, no startup tasks, no scheduled tasks."
Write-Host ""
Write-Host "Selected crew:" -ForegroundColor Yellow
foreach ($lane in $selectedLanes) {
    $color = if ($lane.PSObject.Properties.Name -contains "tab_color") { $lane.tab_color } else { "none" }
    Write-Host "  $($lane.emoji_marker) $($lane.lane_id) | $($lane.display_title) | $color | $($lane.role)"
}

if ($Preview) {
    Write-Host ""
    Write-Host "Preview complete. Windows opened: 0" -ForegroundColor Green
    exit 0
}

$wtCommand = Get-Command wt.exe -ErrorAction SilentlyContinue
if ($null -eq $wtCommand) {
    throw "Windows Terminal wt.exe not found. Install/open Windows Terminal, then rerun."
}

$opened = 0
foreach ($lane in $selectedLanes) {
    if ($opened -ge $MaxWindows) {
        Write-Host "Skipped due to MaxWindows: $($lane.display_title)" -ForegroundColor Yellow
        continue
    }

    if (-not (Test-Path -LiteralPath $lane.path -PathType Container)) {
        Write-Host "Skipped missing path: $($lane.display_title) -> $($lane.path)" -ForegroundColor Yellow
        continue
    }

    Start-Process -FilePath "wt.exe" -ArgumentList (Get-OpenArgs -Lane $lane -IdentityScriptPath $identityScriptPath)
    Write-Host "Opened: $($lane.display_title)"
    $opened += 1
}

Write-Host ""
Write-Host "Crew launch complete. Windows/tabs opened: $opened" -ForegroundColor Green
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
