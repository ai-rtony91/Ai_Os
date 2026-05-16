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
        "Register-ScheduledTask",
        "Start-ScheduledTask",
        "schtasks",
        "shell:startup",
        "OANDA",
        "broker",
        "api key",
        "webhook",
        "live trading",
        "codex "
    )

    foreach ($pattern in $blockedPatterns) {
        if ($content -match [regex]::Escape($pattern)) {
            if ($pattern -in @("OANDA", "broker", "api key", "webhook", "live trading", "codex ")) {
                continue
            }
            throw "Blocked automation pattern found in $Path`: $pattern"
        }
    }
}

$requiredFiles = @(
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
Write-Host "Safety: no Codex auto-launch, no scheduled tasks, no startup tasks."
Write-Host "Safety: no broker/API/live trading, no commits, no pushes, no destructive actions."

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

if (-not $registry.lanes -or @($registry.lanes).Count -lt 1) {
    throw "Lane registry has no lanes."
}

if (-not $sessionExample.lanes -or @($sessionExample.lanes).Count -lt 1) {
    throw "Session example has no lanes."
}

Write-Host ""
Write-Host "== Lane Role / Path / Branch ==" -ForegroundColor Yellow
foreach ($lane in @($registry.lanes)) {
    foreach ($field in @("id", "role", "path", "branch", "restart_command")) {
        if (-not ($lane.PSObject.Properties.Name -contains $field)) {
            throw "Lane $($lane.id) missing field: $field"
        }
    }

    Write-Host "ID: $($lane.id)" -ForegroundColor Cyan
    Write-Host "Role: $($lane.role)"
    Write-Host "Path: $($lane.path)"
    Write-Host "Branch: $($lane.branch)"
    Write-Host "Restart command: $($lane.restart_command)"
    Write-Host ""
}

Write-Host "== Git Worktree List ==" -ForegroundColor Yellow
git worktree list

Write-Host ""
Write-Host "== Bootstrap Preview Smoke Test ==" -ForegroundColor Yellow
powershell -ExecutionPolicy Bypass -File "automation\orchestration\bootstrap\Start-AiOsWorkspace.ps1"

Write-Host ""
Write-Host "Workspace bootstrap DRY_RUN validation passed." -ForegroundColor Green
Write-Host "Files staged: NO"
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
