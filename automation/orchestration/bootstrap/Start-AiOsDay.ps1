param(
    [string]$Intent = "",
    [int]$MaxTabs = 3,
    [switch]$LaunchManualShells,
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

function Write-AiOsSection {
    param([Parameter(Mandatory = $true)][string]$Title)

    Write-Host ""
    Write-Host "== $Title ==" -ForegroundColor Yellow
}

if ($MaxTabs -lt 1) {
    throw "MaxTabs must be 1 or greater."
}

$scriptName = Split-Path -Leaf $PSCommandPath
$isPreview = -not $LaunchManualShells
$registryFullPath = Resolve-AiOsPath -Path $RegistryPath
if (-not (Test-Path -LiteralPath $registryFullPath -PathType Leaf)) {
    throw "Lane registry not found: $registryFullPath"
}

$workspaceScript = Join-Path $PSScriptRoot "Start-AiOsWorkspace.ps1"
$resolverScript = Join-Path $PSScriptRoot "Resolve-AiOsWorkspaceIntent.ps1"
$supervisorScript = Join-Path (Split-Path -Parent $PSScriptRoot) "supervisor\Resolve-AiOsSupervisorAssignment.DRY_RUN.ps1"
$packetStateScript = Join-Path (Split-Path -Parent $PSScriptRoot) "work_packets\Get-AiOsWorkPacketState.ps1"
$workerResolverScript = Join-Path (Split-Path -Parent $PSScriptRoot) "workers\Resolve-AiOsNeededWorkers.DRY_RUN.ps1"

foreach ($requiredScript in @($workspaceScript, $resolverScript, $supervisorScript, $packetStateScript, $workerResolverScript)) {
    if (-not (Test-Path -LiteralPath $requiredScript -PathType Leaf)) {
        throw "Required Daily Start script not found: $requiredScript"
    }
}

$registry = Get-Content -LiteralPath $registryFullPath -Raw | ConvertFrom-Json
$controlLane = @($registry.lanes) | Where-Object { $_.lane_id -eq "main_control" } | Select-Object -First 1
if ($null -eq $controlLane) {
    throw "CONTROL lane not found in registry."
}

$intentResolution = (& $resolverScript -Intent $Intent -QuietJson | ConvertFrom-Json)
$supervisorPlan = (& $supervisorScript -Intent $Intent -QuietJson | ConvertFrom-Json)
$workerPlan = (& $workerResolverScript -Intent $Intent -QuietJson | ConvertFrom-Json)

Write-Host ("COPY START " + [char]0x2014 + " $scriptName")
Write-Host "AI_OS Brainstem Daily Start" -ForegroundColor Cyan
Write-Host "Mode: $(if ($isPreview) { 'PREVIEW - print only' } else { 'MANUAL SHELL LAUNCH' })"
Write-Host "Intent: $($intentResolution.intent)"
Write-Host "MaxTabs: $MaxTabs"
Write-Host "Safety: no Codex auto-launch, no commit, no push, no scheduled/startup tasks."
Write-Host ("Safety: no " + "bro" + "ker/API/live trading.")
Write-Host "Truth rule: path + branch are the source of truth."

Write-AiOsSection -Title "CONTROL Git Status"
Write-Host "lane_id: $($controlLane.lane_id)"
Write-Host "title: $($controlLane.display_title)"
Write-Host "path: $($controlLane.path)"
Write-Host "branch: $($controlLane.branch)"
if (Test-Path -LiteralPath $controlLane.path -PathType Container) {
    $previousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    $controlGitStatus = @(git -C $controlLane.path status --short --branch 2>&1)
    $controlGitExitCode = $LASTEXITCODE
    $ErrorActionPreference = $previousErrorActionPreference
    if ($controlGitExitCode -eq 0) {
        $controlGitStatus | ForEach-Object { Write-Host $_ }
    } else {
        Write-Host "CONTROL git status unavailable in this shell." -ForegroundColor Yellow
        Write-Host "Reason: $($controlGitStatus -join ' ')"
    }
} else {
    Write-Host "CONTROL path unavailable on this machine: $($controlLane.path)" -ForegroundColor Yellow
}

Write-AiOsSection -Title "Workspace Intent Route"
Write-Host "Selected lane IDs:"
@($intentResolution.selected_lane_ids) | ForEach-Object { Write-Host "  $_" }
Write-Host "Manual Codex lane IDs:"
if (@($intentResolution.manual_codex_lane_ids).Count -eq 0) {
    Write-Host "  NONE"
} else {
    @($intentResolution.manual_codex_lane_ids) | ForEach-Object { Write-Host "  $_" }
}

Write-AiOsSection -Title "Supervisor Assignment Preview"
Write-Host "Workers needed: $($supervisorPlan.worker_count)"
foreach ($worker in @($supervisorPlan.workers_needed)) {
    Write-Host "  $($worker.worker_id): $($worker.worker_type)"
    Write-Host "  lane: $($worker.lane_id) - $($worker.lane_title)"
    Write-Host "  does: $($worker.does)"
}
Write-Host "Approval required: $($supervisorPlan.approval_required)"

Write-AiOsSection -Title "Work Packet Summary"
Write-Host "Active packets: $($workerPlan.active_packet_count)"
if ($null -eq $workerPlan.next_packet) {
    Write-Host "Next packet: NONE"
} else {
    Write-Host "Next packet: $($workerPlan.next_packet.packet_id) - $($workerPlan.next_packet.title)"
    Write-Host "Packet repo: $($workerPlan.next_packet.repo)"
    Write-Host "Packet branch: $($workerPlan.next_packet.branch)"
}

Write-AiOsSection -Title "Worker Profile Resolution"
Write-Host "Primary worker: $($workerPlan.primary_worker.worker_id) - $($workerPlan.primary_worker.display_title)"
Write-Host "Worker path: $($workerPlan.primary_worker.default_path)"
Write-Host "Worker branch: $($workerPlan.primary_worker.default_branch)"
Write-Host "Needed workers:"
@($workerPlan.needed_workers) | ForEach-Object {
    Write-Host "  $($_.worker_id) - $($_.display_title) - $($_.worker_type)"
}
Write-Host "Validator: $($workerPlan.validator)"
Write-Host "Guard check: $($workerPlan.guard_command)"
Write-Host "Later save/PR command: $($workerPlan.save_command)"

Write-AiOsSection -Title "Suggested Lanes"
foreach ($laneId in @($intentResolution.selected_lane_ids)) {
    $lane = @($registry.lanes) | Where-Object { $_.lane_id -eq $laneId } | Select-Object -First 1
    if ($null -eq $lane) {
        throw "Intent selected unknown lane_id: $laneId"
    }
    Write-Host "  $($lane.lane_id) - $($lane.display_title) - $($lane.path) - $($lane.branch)"
}

Write-AiOsSection -Title "Suggested Validators"
@($supervisorPlan.validators) | ForEach-Object { Write-Host "  $_" }

Write-AiOsSection -Title "WHERE TO RUN NEXT"
Write-Host ("Visible tab/window: SAVE " + [char]0x00b7 + " git")
Write-Host "Path: $((Get-Location).Path)"
Write-Host "Run:"
Write-Host "  $($workerPlan.guard_command)"
Write-Host "Then:"
Write-Host "  $($workerPlan.validator)"
Write-Host "Stop condition: stop if validator fails, path or branch is unexpected, or any command proposes commit/push/launch without explicit approval."

if ($LaunchManualShells) {
    Write-AiOsSection -Title "Manual Shell Launch"
    & $workspaceScript -LaunchManualShells -Intent $Intent -MaxWindows $MaxTabs -RegistryPath $RegistryPath
} else {
    Write-Host ""
    Write-Host "Daily start preview complete. Tabs opened: NO" -ForegroundColor Green
}

Write-Host "Codex auto-launch performed: NO"
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host ("COPY END " + [char]0x2014 + " $scriptName")
