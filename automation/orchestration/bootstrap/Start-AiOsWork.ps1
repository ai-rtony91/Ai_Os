param(
    [string]$Intent = "",
    [int]$MaxTabs = 3,
    [switch]$LaunchManualShells,
    [switch]$Apply
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
$repoRoot = (Get-Location).Path
$currentBranch = (git branch --show-current 2>$null)
if ($null -eq $currentBranch) {
    $currentBranch = ""
}
$currentBranch = $currentBranch.Trim()

$validatorScript = Resolve-AiOsPath -Path "automation/orchestration/bootstrap/Test-AiOsWorkspaceBootstrap.DRY_RUN.ps1"
$packetStateScript = Resolve-AiOsPath -Path "automation/orchestration/work_packets/Get-AiOsWorkPacketState.ps1"
$packetRouteScript = Resolve-AiOsPath -Path "automation/orchestration/work_packets/Route-AiOsWorkPacket.DRY_RUN.ps1"
$dailyStartScript = Resolve-AiOsPath -Path "automation/orchestration/bootstrap/Start-AiOsDay.ps1"
$workerResolverScript = Resolve-AiOsPath -Path "automation/orchestration/workers/Resolve-AiOsNeededWorkers.DRY_RUN.ps1"

foreach ($requiredScript in @($validatorScript, $packetStateScript, $packetRouteScript, $dailyStartScript, $workerResolverScript)) {
    if (-not (Test-Path -LiteralPath $requiredScript -PathType Leaf)) {
        throw "Required workflow script not found: $requiredScript"
    }
}

$workerPlan = (& $workerResolverScript -Intent $Intent -QuietJson | ConvertFrom-Json)
$primaryWorker = $workerPlan.primary_worker
$nextPacket = $workerPlan.next_packet
$packetLabel = "NONE"
if ($null -ne $nextPacket) {
    $packetLabel = "$($nextPacket.packet_id) - $($nextPacket.title)"
}

$codexPrompt = "NONE"
if ($primaryWorker.worker_type -like "*codex*") {
    $packetId = if ($null -eq $nextPacket) { "none" } else { $nextPacket.packet_id }
    $packetTitle = if ($null -eq $nextPacket) { "No active packet" } else { $nextPacket.title }
    $codexPrompt = "APPROVED APPLY - Work packet $packetId`: $packetTitle. Use path $($primaryWorker.default_path) on branch $($primaryWorker.default_branch). Run guard first, keep edits in owned paths, then run validator. Do not commit or push."
}

Write-Host ("COPY START " + [char]0x2014 + " $scriptName")
Write-Host "AI_OS One Command Workflow" -ForegroundColor Cyan
Write-Host "Mode: $(if ($LaunchManualShells) { 'MANUAL SHELL LAUNCH REQUESTED' } else { 'PREVIEW - print only' })"
Write-Host "Intent: $Intent"
Write-Host "MaxTabs: $MaxTabs"
Write-Host "Apply supplied: $($Apply.IsPresent)"
Write-Host "Safety: no commits, no pushes, no PR creation, no merge, no Codex auto-launch."
Write-Host "Safety: no scheduled/startup tasks, no destructive actions, no new worktrees."
Write-Host ("Safety: no " + "bro" + "ker/API/live trading.")

Write-AiOsSection -Title "Current Repo"
Write-Host "Path: $repoRoot"
Write-Host "Branch: $currentBranch"
git status --short --branch

Write-AiOsSection -Title "Bootstrap Validator"
$validatorOutput = powershell -ExecutionPolicy Bypass -File $validatorScript
$validatorText = ($validatorOutput -join [Environment]::NewLine)
if ($validatorText -notmatch "Workspace bootstrap DRY_RUN validation passed") {
    throw "Bootstrap validator did not report pass."
}
Write-Host "PASS: Workspace bootstrap validator passed."

Write-AiOsSection -Title "Work Packet State"
$packetStateOutput = powershell -ExecutionPolicy Bypass -File $packetStateScript
$packetStateOutput | ForEach-Object { Write-Host $_ }

Write-AiOsSection -Title "Packet Routing Preview"
$packetRouteOutput = powershell -ExecutionPolicy Bypass -File $packetRouteScript
$packetRouteOutput | ForEach-Object { Write-Host $_ }

Write-AiOsSection -Title "Daily Start Preview"
if ($LaunchManualShells) {
    powershell -ExecutionPolicy Bypass -File $dailyStartScript -Intent $Intent -MaxTabs $MaxTabs -LaunchManualShells
} else {
    powershell -ExecutionPolicy Bypass -File $dailyStartScript -Intent $Intent -MaxTabs $MaxTabs
}

Write-AiOsSection -Title "Chosen Next Safe Action"
Write-Host "Visible tab/window: $($primaryWorker.display_title)"
Write-Host "Path: $($primaryWorker.default_path)"
Write-Host "Branch: $($primaryWorker.default_branch)"
Write-Host "Worker: $($primaryWorker.worker_id)"
Write-Host "Packet: $packetLabel"
Write-Host "Validator: $($workerPlan.validator)"
Write-Host "Guard check: $($workerPlan.guard_command)"
Write-Host "Exact Codex prompt: $codexPrompt"
Write-Host "Exact save command: $($workerPlan.save_command)"

Write-AiOsSection -Title "WHERE TO RUN NEXT"
Write-Host "Visible tab/window: $($primaryWorker.display_title)"
Write-Host "Path: $($primaryWorker.default_path)"
Write-Host "Branch: $($primaryWorker.default_branch)"
Write-Host "Run:"
Write-Host "  $($workerPlan.guard_command)"
if ($codexPrompt -ne "NONE") {
    Write-Host "Then paste this exact Codex prompt in the correct lane:"
    Write-Host "  $codexPrompt"
}
Write-Host "After work, validate:"
Write-Host "  $($workerPlan.validator)"
Write-Host "Later save preview:"
Write-Host "  $($workerPlan.save_command)"

Write-Host ""
Write-Host "Launch performed: $(if ($LaunchManualShells) { 'MANUAL SHELLS REQUESTED' } else { 'NO' })"
Write-Host "State update performed: NO"
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host "PR created: NO"
Write-Host "Merge performed: NO"
Write-Host ("COPY END " + [char]0x2014 + " $scriptName")
