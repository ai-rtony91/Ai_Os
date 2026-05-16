param(
    [string]$RegistryPath = "automation/orchestration/terminal_workstations/AIOS_WORKTREE_LANE_REGISTRY.json",
    [string]$SessionExamplePath = "automation/orchestration/terminal_workstations/AIOS_SESSION_STATE.example.json"
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

function Test-PowerShellParse {
    param([Parameter(Mandatory = $true)][string]$Path)

    $tokens = $null
    $errors = $null
    [System.Management.Automation.Language.Parser]::ParseFile($Path, [ref]$tokens, [ref]$errors) | Out-Null
    if ($errors.Count -gt 0) {
        throw "PowerShell parse failed for $Path`: $($errors[0].Message)"
    }
}

function Assert-NoBlockedAutomation {
    param([Parameter(Mandatory = $true)][string]$Path)

    $content = Get-Content -LiteralPath $Path -Raw
    $blockedPatterns = @(
        ("bro" + "ker"),
        ("OAN" + "DA"),
        ("api" + "_key"),
        ("web" + "hook"),
        ("live" + "_order"),
        ("real" + "_order"),
        ("scheduled" + "_task"),
        ("startup" + "_task")
    )

    foreach ($pattern in $blockedPatterns) {
        if ($content -match [regex]::Escape($pattern)) {
            throw "Blocked automation pattern found in $Path`: $pattern"
        }
    }
}

function Assert-NoAssistantAutoStart {
    param([Parameter(Mandatory = $true)][string]$Path)

    $content = Get-Content -LiteralPath $Path -Raw
    $autoStartPatterns = @(
        ("cod" + "ex.exe"),
        ("cod" + "ex -"),
        ("cod" + "ex --"),
        ("Start-Process cod" + "ex"),
        ("& cod" + "ex")
    )

    foreach ($pattern in $autoStartPatterns) {
        if ($content -match [regex]::Escape($pattern)) {
            throw "Assistant auto-start pattern found in $Path`: $pattern"
        }
    }
}

$requiredFiles = @(
    "automation/orchestration/terminal_workstations/AIOS_WORKTREE_LANE_REGISTRY.json",
    "automation/orchestration/bootstrap/Start-AiOsWorkspace.ps1",
    "automation/orchestration/bootstrap/Open-AiOsLane.ps1",
    "automation/orchestration/bootstrap/Save-AiOsSession.ps1",
    "automation/orchestration/bootstrap/Restore-AiOsSession.ps1",
    "automation/orchestration/bootstrap/Test-AiOsWorkspaceBootstrap.DRY_RUN.ps1",
    "automation/orchestration/terminal_workstations/AIOS_SESSION_STATE.example.json",
    "docs/AI_OS/orchestration/AIOS_WORKSPACE_BOOTSTRAP.md"
)

Write-Host "AI_OS Workspace Bootstrap Validator" -ForegroundColor Cyan
Write-Host "Mode: DRY_RUN"
Write-Host "Safety: assistant start is manual. Background launch hooks are disabled."
Write-Host "Safety: no commits, no pushes, no destructive cleanup, no external execution integration."

Write-Host ""
Write-Host "== Required Files ==" -ForegroundColor Yellow
foreach ($file in $requiredFiles) {
    $fullPath = Resolve-AiOsPath -Path $file
    if (-not (Test-Path -LiteralPath $fullPath -PathType Leaf)) {
        throw "Missing required file: $file"
    }
    Write-Host "FOUND: $file"
}

Write-Host ""
Write-Host "== PowerShell Parse ==" -ForegroundColor Yellow
foreach ($file in $requiredFiles | Where-Object { $_ -like "*.ps1" }) {
    $fullPath = Resolve-AiOsPath -Path $file
    Test-PowerShellParse -Path $fullPath
    if ((Split-Path -Leaf $fullPath) -ne "Test-AiOsWorkspaceBootstrap.DRY_RUN.ps1") {
        Assert-NoBlockedAutomation -Path $fullPath
        Assert-NoAssistantAutoStart -Path $fullPath
    }
    Write-Host "PASS: $file"
}

Write-Host ""
Write-Host "== JSON Parse ==" -ForegroundColor Yellow
$registryFullPath = Resolve-AiOsPath -Path $RegistryPath
$sessionExampleFullPath = Resolve-AiOsPath -Path $SessionExamplePath
$registry = Get-Content -LiteralPath $registryFullPath -Raw | ConvertFrom-Json
$sessionExample = Get-Content -LiteralPath $sessionExampleFullPath -Raw | ConvertFrom-Json
Write-Host "PASS: $RegistryPath"
Write-Host "PASS: $SessionExamplePath"
Assert-NoBlockedAutomation -Path $registryFullPath
Assert-NoBlockedAutomation -Path $sessionExampleFullPath
Assert-NoAssistantAutoStart -Path $registryFullPath
Assert-NoAssistantAutoStart -Path $sessionExampleFullPath

if (-not $registry.lanes -or @($registry.lanes).Count -lt 1) {
    throw "Lane registry has no lanes."
}

if (-not $sessionExample.lanes -or @($sessionExample.lanes).Count -lt 1) {
    throw "Session example has no lanes."
}

$requiredLaneIds = @(
    "main_control",
    "active_git",
    "active_codex",
    "validation",
    "phase3_git",
    "phase3_codex",
    "bootstrap_git",
    "bootstrap_codex"
)

Write-Host ""
Write-Host "== Required Lane IDs ==" -ForegroundColor Yellow
$actualLaneIds = @($registry.lanes | ForEach-Object { $_.id })
foreach ($laneId in $requiredLaneIds) {
    if ($actualLaneIds -notcontains $laneId) {
        throw "Missing required lane id: $laneId"
    }
    Write-Host "PASS: $laneId"
}

$requiredSessionFields = @(
    "active_workspace",
    "active_worktree",
    "active_branch",
    "open_lanes",
    "last_known_roles",
    "last_commands",
    "pending_workorders",
    "last_validator_status",
    "next_safe_action"
)

Write-Host ""
Write-Host "== Session State Fields ==" -ForegroundColor Yellow
foreach ($field in $requiredSessionFields) {
    if (-not ($sessionExample.PSObject.Properties.Name -contains $field)) {
        throw "Session example missing field: $field"
    }
    Write-Host "PASS: $field"
}

Write-Host ""
Write-Host "== Lane Role / Path / Branch ==" -ForegroundColor Yellow
foreach ($lane in @($registry.lanes)) {
    foreach ($field in @("id", "name", "role", "path", "branch", "codex_policy", "launch_policy", "restart_command", "allowed_actions", "blocked_actions")) {
        if (-not ($lane.PSObject.Properties.Name -contains $field)) {
            throw "Lane $($lane.id) missing field: $field"
        }
    }

    Write-Host "ID: $($lane.id)" -ForegroundColor Cyan
    Write-Host "Role: $($lane.role)"
    Write-Host "Path: $($lane.path)"
    Write-Host "Branch: $($lane.branch)"
    Write-Host "Codex policy: $($lane.codex_policy)"
    Write-Host "Launch policy: $($lane.launch_policy)"
    Write-Host "Restart command: $($lane.restart_command)"
    Write-Host ""
}

Write-Host "== Git Worktree List ==" -ForegroundColor Yellow
git worktree list

Write-Host ""
Write-Host "== Bootstrap Preview Smoke Test ==" -ForegroundColor Yellow
powershell -ExecutionPolicy Bypass -File "automation\orchestration\bootstrap\Start-AiOsWorkspace.ps1" -Preview

Write-Host ""
Write-Host "== Lane Preview Smoke Test ==" -ForegroundColor Yellow
powershell -ExecutionPolicy Bypass -File "automation\orchestration\bootstrap\Open-AiOsLane.ps1" -LaneId bootstrap_git -Preview

Write-Host ""
Write-Host "== Restore Preview Smoke Test ==" -ForegroundColor Yellow
powershell -ExecutionPolicy Bypass -File "automation\orchestration\bootstrap\Restore-AiOsSession.ps1" -Preview

Write-Host ""
Write-Host "Workspace bootstrap DRY_RUN validation passed." -ForegroundColor Green
Write-Host "Files staged: NO"
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
