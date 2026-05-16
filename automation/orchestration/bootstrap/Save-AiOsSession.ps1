param(
    [switch]$Apply,
    [string]$RegistryPath = "automation/orchestration/terminal_workstations/AIOS_WORKTREE_LANE_REGISTRY.json",
    [string]$SessionPath = "automation/orchestration/terminal_workstations/AIOS_SESSION_STATE.json"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Resolve-AiOsPath {
    param([Parameter(Mandatory = $true)][string]$Path)

    if ([System.IO.Path]::IsPathRooted($Path)) {
        return $Path
    }

    return Join-Path (Get-Location).Path $Path
}

$fullRegistryPath = Resolve-AiOsPath -Path $RegistryPath
$fullSessionPath = Resolve-AiOsPath -Path $SessionPath

if (-not (Test-Path -LiteralPath $fullRegistryPath -PathType Leaf)) {
    throw "Lane registry not found: $fullRegistryPath"
}

$registry = Get-Content -LiteralPath $fullRegistryPath -Raw | ConvertFrom-Json
$timestamp = (Get-Date).ToString("o")

$session = [ordered]@{
    session_id = "AIOS_SESSION_STATE"
    version = "1.0"
    saved_at = $timestamp
    mode = "manual_restore_only"
    source_registry = $RegistryPath
    safety = [ordered]@{
        codex_auto_launch = $false
        scheduled_tasks = $false
        startup_tasks = $false
        broker_api_live_trading = $false
        destructive_actions = $false
    }
    lanes = @($registry.lanes | ForEach-Object {
        [ordered]@{
            id = $_.id
            name = $_.name
            role = $_.role
            path = $_.path
            branch = $_.branch
            codex_allowed = $_.codex_allowed
            restart_command = $_.restart_command
        }
    })
    restart_commands = @($registry.lanes | ForEach-Object { $_.restart_command })
}

$json = $session | ConvertTo-Json -Depth 8

Write-Host "AI_OS Session Save" -ForegroundColor Cyan
Write-Host "Mode: $(if ($Apply) { 'APPLY - write session state if missing' } else { 'PREVIEW - no file written' })"
Write-Host "Session path: $fullSessionPath"
Write-Host "Safety: no Codex auto-launch, no scheduled tasks, no startup tasks."
Write-Host "Safety: no broker/API/live trading, no commits, no pushes, no destructive actions."

Write-Host ""
Write-Host "== Git Worktree List ==" -ForegroundColor Yellow
git worktree list

Write-Host ""
Write-Host "== Session Preview ==" -ForegroundColor Yellow
Write-Host $json

if (-not $Apply) {
    Write-Host ""
    Write-Host "Preview complete. No session file written." -ForegroundColor Green
    exit 0
}

if (Test-Path -LiteralPath $fullSessionPath -PathType Leaf) {
    throw "Session file already exists. Refusing to overwrite: $fullSessionPath"
}

$sessionDirectory = Split-Path -Parent $fullSessionPath
if (-not (Test-Path -LiteralPath $sessionDirectory -PathType Container)) {
    New-Item -ItemType Directory -Path $sessionDirectory | Out-Null
}

Set-Content -LiteralPath $fullSessionPath -Value $json -Encoding UTF8
Write-Host "Session saved: $fullSessionPath" -ForegroundColor Green
Write-Host "Codex auto-launch performed: NO"
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
