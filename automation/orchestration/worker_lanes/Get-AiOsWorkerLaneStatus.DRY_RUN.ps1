param(
    [string]$StatusPath = (Join-Path $PSScriptRoot "WORKER_LANE_STATUS.example.json"),
    [switch]$OutputJson
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Read-AiOsJsonFile {
    param([Parameter(Mandatory = $true)][string]$Path)

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "Worker lane status file not found: $Path"
    }

    return Get-Content -Raw -LiteralPath $Path | ConvertFrom-Json
}

function Invoke-GitText {
    param([Parameter(Mandatory = $true)][string[]]$Arguments)

    $previousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    $output = & git @Arguments 2>&1
    $ErrorActionPreference = $previousErrorActionPreference
    return @($output | ForEach-Object { [string]$_ })
}

function Test-BranchPattern {
    param(
        [Parameter(Mandatory = $true)][string]$Branch,
        [Parameter(Mandatory = $true)][string]$Pattern
    )

    if ($Pattern.EndsWith("/*")) {
        $prefix = $Pattern.Substring(0, $Pattern.Length - 1)
        return $Branch.StartsWith($prefix)
    }

    return $Branch -eq $Pattern
}

function Get-CurrentLaneId {
    param(
        [Parameter(Mandatory = $true)][string]$Branch,
        [Parameter(Mandatory = $true)]$Lanes
    )

    foreach ($lane in $Lanes) {
        foreach ($pattern in @($lane.expected_branch_patterns)) {
            if (Test-BranchPattern -Branch $Branch -Pattern $pattern) {
                return $lane.lane_id
            }
        }
    }

    return "UNKNOWN"
}

$statusModel = Read-AiOsJsonFile -Path $StatusPath
$lanes = @($statusModel.lanes)

$branchOutputLines = @(Invoke-GitText -Arguments @("branch", "--show-current"))
$branchWarnings = @($branchOutputLines | Where-Object { $_ -match "^warning:" })
$branchLines = @($branchOutputLines | Where-Object { $_ -notmatch "^warning:" })
$currentBranch = if ($branchLines.Count -gt 0 -and -not [string]::IsNullOrWhiteSpace($branchLines[0])) { $branchLines[0] } else { "UNKNOWN" }
$statusOutputLines = @(Invoke-GitText -Arguments @("status", "--short"))
$statusWarnings = @($statusOutputLines | Where-Object { $_ -match "^warning:" })
$statusLines = @($statusOutputLines | Where-Object { $_ -notmatch "^warning:" })
$gitWarnings = @($branchWarnings + $statusWarnings | Sort-Object -Unique)
$statusClean = ($statusLines.Count -eq 0)
$untrackedFiles = @($statusLines | Where-Object { $_.StartsWith("?? ") } | ForEach-Object { $_.Substring(3) })
$trackedDirtyFiles = @($statusLines | Where-Object { -not $_.StartsWith("?? ") })
$currentLaneId = Get-CurrentLaneId -Branch $currentBranch -Lanes $lanes

$laneResults = @()
foreach ($lane in $lanes) {
    $isCurrentLane = ($lane.lane_id -eq $currentLaneId)
    $laneStatus = "UNKNOWN"
    $laneDirty = $false
    $reason = "No verified local evidence for this lane."
    $safeNextAction = $lane.safe_next_action

    if ($isCurrentLane) {
        $laneDirty = -not $statusClean
        if ($statusClean) {
            $laneStatus = "PASS"
            $reason = "Current branch maps to this lane and git status is clean."
            $safeNextAction = "Lane is clean. Operator may assign the next DRY_RUN task."
        } else {
            $laneStatus = "WARN"
            $reason = "Current branch maps to this lane, but git status is dirty or has untracked files."
            $safeNextAction = "Review untracked and dirty files before assigning more work or approving APPLY."
        }
    }

    $laneResults += [pscustomobject]@{
        lane_id = $lane.lane_id
        lane_name = $lane.lane_name
        purpose = $lane.purpose
        is_current_lane = $isCurrentLane
        status = $laneStatus
        dirty = $laneDirty
        current_activity = if ($isCurrentLane) { "Current git branch: $currentBranch" } else { $lane.current_activity }
        status_reason = $reason
        safe_next_action = $safeNextAction
    }
}

$dirtyLanes = @($laneResults | Where-Object { $_.dirty })
$collisionWarnings = @()
if ($dirtyLanes.Count -gt 1) {
    $collisionWarnings += "Collision risk: multiple lanes show dirty-file evidence. Stop and resolve ownership before APPLY."
}

if ($currentLaneId -eq "UNKNOWN") {
    $collisionWarnings += "Current branch does not map to CODEX_01, CODEX_02, CLAUDE_01, or MAIN_CONTROL."
}

$overallStatus = "PASS"
if ($collisionWarnings.Count -gt 0) {
    $overallStatus = "FAIL"
} elseif (-not $statusClean -or $currentLaneId -eq "UNKNOWN") {
    $overallStatus = "WARN"
}

$nextSafeAction = "Review lane status before assigning work."
if ($overallStatus -eq "PASS") {
    $nextSafeAction = "Proceed with DRY_RUN planning or assign one clearly scoped lane task."
} elseif ($overallStatus -eq "WARN") {
    $nextSafeAction = "Review dirty and untracked files before starting another lane task."
} elseif ($overallStatus -eq "FAIL") {
    $nextSafeAction = "Stop. Resolve lane ownership or branch mapping before APPLY, commit, or push."
}

$result = [pscustomobject]@{
    task = "Show AI_OS worker lane status"
    mode = "DRY_RUN"
    status_path = $StatusPath
    current_branch = $currentBranch
    current_lane = $currentLaneId
    git_status = if ($statusClean) { "clean" } else { "dirty" }
    tracked_dirty_count = $trackedDirtyFiles.Count
    untracked_count = $untrackedFiles.Count
    tracked_dirty_files = $trackedDirtyFiles
    untracked_files = $untrackedFiles
    git_warnings = $gitWarnings
    overall_status = $overallStatus
    lanes = $laneResults
    collision_warnings = $collisionWarnings
    safety = [pscustomobject]@{
        writes_performed = 0
        commits_performed = 0
        pushes_performed = 0
        runtime_edits = "NO"
        dispatcher_edits = "NO"
        schema_edits = "NO"
    }
    validator_friendly = $true
    next_safe_action = $nextSafeAction
}

if ($OutputJson) {
    $result | ConvertTo-Json -Depth 8
    exit 0
}

Write-Host "AI_OS Worker Lane Status"
Write-Host "Mode: DRY_RUN"
Write-Host "Current branch: $currentBranch"
Write-Host "Current lane: $currentLaneId"
Write-Host "Git status: $($result.git_status)"
Write-Host "Untracked files: $($result.untracked_count)"
Write-Host "Overall status: $overallStatus"
Write-Host ""

foreach ($lane in $laneResults) {
    Write-Host "Lane: $($lane.lane_id)"
    Write-Host "  Purpose: $($lane.purpose)"
    Write-Host "  Status: $($lane.status)"
    Write-Host "  Current lane: $($lane.is_current_lane)"
    Write-Host "  Activity: $($lane.current_activity)"
    Write-Host "  Reason: $($lane.status_reason)"
    Write-Host "  Safe next action: $($lane.safe_next_action)"
    Write-Host ""
}

Write-Host "Dirty tracked files:"
if ($trackedDirtyFiles.Count -eq 0) {
    Write-Host "  NONE"
} else {
    foreach ($file in $trackedDirtyFiles) {
        Write-Host "  - $file"
    }
}
Write-Host ""

Write-Host "Untracked files:"
if ($untrackedFiles.Count -eq 0) {
    Write-Host "  NONE"
} else {
    foreach ($file in $untrackedFiles) {
        Write-Host "  - $file"
    }
}
Write-Host ""

Write-Host "Collision warnings:"
if ($collisionWarnings.Count -eq 0) {
    Write-Host "  NONE"
} else {
    foreach ($warning in $collisionWarnings) {
        Write-Host "  - $warning"
    }
}
Write-Host ""

Write-Host "Git warnings:"
if ($gitWarnings.Count -eq 0) {
    Write-Host "  NONE"
} else {
    foreach ($warning in $gitWarnings) {
        Write-Host "  - $warning"
    }
}
Write-Host ""

Write-Host "Validator note: no files were changed by this DRY_RUN check."
Write-Host "Next safe action: $nextSafeAction"
