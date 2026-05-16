param(
    [string]$Intent = "",
    [switch]$QuietJson,
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

$scriptName = Split-Path -Leaf $PSCommandPath
$registryFullPath = Resolve-AiOsPath -Path $RegistryPath
if (-not (Test-Path -LiteralPath $registryFullPath -PathType Leaf)) {
    throw "Lane registry not found: $registryFullPath"
}

$resolverPath = Join-Path (Split-Path -Parent $PSScriptRoot) "bootstrap\Resolve-AiOsWorkspaceIntent.ps1"
if (-not (Test-Path -LiteralPath $resolverPath -PathType Leaf)) {
    throw "Intent resolver not found: $resolverPath"
}

$workerResolverPath = Join-Path (Split-Path -Parent $PSScriptRoot) "workers\Resolve-AiOsNeededWorkers.DRY_RUN.ps1"
if (-not (Test-Path -LiteralPath $workerResolverPath -PathType Leaf)) {
    throw "Worker profile resolver not found: $workerResolverPath"
}

$registry = Get-Content -LiteralPath $registryFullPath -Raw | ConvertFrom-Json
$intentResolution = (& $resolverPath -Intent $Intent -QuietJson | ConvertFrom-Json)
$workerPlan = (& $workerResolverPath -Intent $Intent -QuietJson | ConvertFrom-Json)
$selectedLaneIds = @($intentResolution.selected_lane_ids)
$manualCodexLaneIds = @($intentResolution.manual_codex_lane_ids)

$codexLaneId = if ($manualCodexLaneIds -contains "rulebook_codex") {
    "rulebook_codex"
} elseif ($manualCodexLaneIds -contains "create_codex") {
    "create_codex"
} elseif ($selectedLaneIds -contains "rulebook_codex") {
    "rulebook_codex"
} else {
    "create_codex"
}

$codexLane = Get-LaneById -Registry $registry -LaneId $codexLaneId
$controlLane = Get-LaneById -Registry $registry -LaneId "main_control"
$saveLane = Get-LaneById -Registry $registry -LaneId "save_git"
$auditLane = Get-LaneById -Registry $registry -LaneId "check_audit"
$primaryWorker = $workerPlan.primary_worker

$filesInScope = @(
    "automation/orchestration/operator/AIOS_OPERATOR_RULES.json",
    "automation/orchestration/bootstrap/Resolve-AiOsWorkspaceIntent.ps1",
    "automation/orchestration/bootstrap/Start-AiOsWorkspace.ps1",
    "automation/orchestration/bootstrap/Start-AiOsDay.ps1",
    "automation/orchestration/bootstrap/Test-AiOsWorkspaceBootstrap.DRY_RUN.ps1",
    "automation/orchestration/supervisor/Resolve-AiOsSupervisorAssignment.DRY_RUN.ps1",
    "docs/AI_OS/orchestration/AIOS_OPERATOR_RULEBOOK.md",
    "docs/AI_OS/orchestration/AIOS_DAILY_START.md",
    "docs/AI_OS/orchestration/AIOS_WORKSPACE_BOOTSTRAP.md"
)

$validators = @(
    $workerPlan.guard_command,
    "powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Test-AiOsWorkspaceBootstrap.DRY_RUN.ps1",
    "powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Start-AiOsDay.ps1 -Intent ""$($intentResolution.intent)"" -MaxTabs 3",
    "git diff --check",
    "git status --short --branch",
    "git diff --stat"
)

$plan = [pscustomobject]@{
    mode = "DRY_RUN"
    intent = $intentResolution.intent
    worker_count = 1
    worker_profile_source = "automation/orchestration/workers/AIOS_WORKER_PROFILES.json"
    workers_needed = @(
        [pscustomobject]@{
            worker_id = $primaryWorker.worker_id
            worker_type = $primaryWorker.worker_type
            lane_id = $primaryWorker.worker_id
            lane_title = $primaryWorker.display_title
            path = $primaryWorker.default_path
            branch = $primaryWorker.default_branch
            does = "Work the selected packet using the standing worker profile. Keep edits inside owned paths and obey overlap restrictions."
            files_in_scope = $filesInScope
        }
    )
    support_lanes = @(
        [pscustomobject]@{ lane_id = $controlLane.lane_id; lane_title = $controlLane.display_title; purpose = "Permanent root and truth check." },
        [pscustomobject]@{ lane_id = $saveLane.lane_id; lane_title = $saveLane.display_title; purpose = "Git status, diff, validation, and explicit save command only." },
        [pscustomobject]@{ lane_id = $auditLane.lane_id; lane_title = $auditLane.display_title; purpose = "Read-only validation and audit." }
    )
    selected_lane_ids = $selectedLaneIds
    validators = $validators
    guard_command = $workerPlan.guard_command
    save_command = $workerPlan.save_command
    approval_required = ("Human approval required before LaunchManualShells, commit, push, protected edits, " + "bro" + "ker/API/live trading, scheduled tasks, or startup tasks.")
    exact_next_safe_action = "Run: $($workerPlan.guard_command)"
}

if ($QuietJson) {
    $plan | ConvertTo-Json -Depth 8
    exit 0
}

Write-Host ("COPY START " + [char]0x2014 + " $scriptName")
Write-Host "AI_OS Supervisor Assignment Planner" -ForegroundColor Cyan
Write-Host "Mode: DRY_RUN"
Write-Host "Intent: $($plan.intent)"
Write-Host "Worker count: $($plan.worker_count)"
Write-Host ""
Write-Host "What workers are needed:" -ForegroundColor Yellow
foreach ($worker in @($plan.workers_needed)) {
    Write-Host "  worker_id: $($worker.worker_id)"
    Write-Host "  worker_type: $($worker.worker_type)"
    Write-Host "  lane_id: $($worker.lane_id)"
    Write-Host "  lane_title: $($worker.lane_title)"
    Write-Host "  path: $($worker.path)"
    Write-Host "  branch: $($worker.branch)"
    Write-Host "  does: $($worker.does)"
}
Write-Host ""
Write-Host "What files are in scope:" -ForegroundColor Yellow
@($filesInScope) | ForEach-Object { Write-Host "  $_" }
Write-Host ""
Write-Host "Validators run:" -ForegroundColor Yellow
@($validators) | ForEach-Object { Write-Host "  $_" }
Write-Host ""
Write-Host "Guard check:" -ForegroundColor Yellow
Write-Host "  $($plan.guard_command)"
Write-Host ""
Write-Host "Later save/PR command:" -ForegroundColor Yellow
Write-Host "  $($plan.save_command)"
Write-Host ""
Write-Host "Approval required:" -ForegroundColor Yellow
Write-Host "  $($plan.approval_required)"
Write-Host ""
Write-Host "Exact next safe action:" -ForegroundColor Yellow
Write-Host "  $($plan.exact_next_safe_action)"
Write-Host ("COPY END " + [char]0x2014 + " $scriptName")
