param(
    [string]$LaneRegistryPath = "automation/orchestration/terminal_workstations/AIOS_WORKTREE_LANE_REGISTRY.json",
    [string]$WorkerRegistryPath = "automation/orchestration/workers/AIOS_WORKER_REGISTRY.json",
    [switch]$OutputJson
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Invoke-AiOsGit {
    param([Parameter(Mandatory = $true)][string[]]$Arguments)

    $previousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    $output = & git @Arguments 2>&1
    $exitCode = $LASTEXITCODE
    $ErrorActionPreference = $previousErrorActionPreference

    return [pscustomobject]@{
        Output = @($output | ForEach-Object { [string]$_ })
        ExitCode = $exitCode
    }
}

function Resolve-AiOsPath {
    param([Parameter(Mandatory = $true)][string]$Path)

    if ([System.IO.Path]::IsPathRooted($Path)) {
        return $Path
    }

    return (Join-Path (Get-Location).Path $Path)
}

function Read-AiOsJsonFile {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$Label
    )

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "$Label not found: $Path"
    }

    try {
        return Get-Content -Raw -LiteralPath $Path | ConvertFrom-Json
    } catch {
        throw "$Label JSON parse failed: $($_.Exception.Message)"
    }
}

function ConvertTo-AiOsPathKey {
    param([AllowNull()][string]$Path)

    if ([string]::IsNullOrWhiteSpace($Path)) {
        return ""
    }

    return $Path.Replace("\", "/").Trim().TrimEnd("/")
}

function ConvertTo-AiOsWorktreeRows {
    param([string[]]$Lines)

    $rows = @()
    $current = [ordered]@{}

    foreach ($line in $Lines) {
        if ([string]::IsNullOrWhiteSpace($line)) {
            if ($current.Count -gt 0) {
                $rows += [pscustomobject]$current
                $current = [ordered]@{}
            }
            continue
        }

        if ($line.StartsWith("worktree ")) {
            $current["path"] = $line.Substring(9)
        } elseif ($line.StartsWith("HEAD ")) {
            $current["head"] = $line.Substring(5)
        } elseif ($line.StartsWith("branch ")) {
            $current["branch"] = $line.Substring(7).Replace("refs/heads/", "")
        } elseif ($line -eq "bare") {
            $current["bare"] = $true
        } elseif ($line -eq "detached") {
            $current["detached"] = $true
        }
    }

    if ($current.Count -gt 0) {
        $rows += [pscustomobject]$current
    }

    return $rows
}

function Get-AiOsGitStatusCount {
    param([Parameter(Mandatory = $true)][string]$Path)

    if (-not (Test-Path -LiteralPath $Path -PathType Container)) {
        return [pscustomobject]@{
            status = "MISSING_PATH"
            dirty_count = 0
            files = @()
            warnings = @()
        }
    }

    $result = Invoke-AiOsGit -Arguments @("-C", $Path, "status", "--short")
    $warnings = @($result.Output | Where-Object { $_ -match "^warning:" })
    $files = @($result.Output | Where-Object { $_ -notmatch "^warning:" -and -not [string]::IsNullOrWhiteSpace($_) })
    $readStatus = if ($result.ExitCode -eq 0) { "READ" } else { "READ_FAILED" }

    return [pscustomobject]@{
        status = $readStatus
        dirty_count = if ($readStatus -eq "READ") { $files.Count } else { 0 }
        files = if ($readStatus -eq "READ") { $files } else { @() }
        errors = if ($readStatus -eq "READ_FAILED") { $files } else { @() }
        warnings = $warnings
    }
}

$resolvedLaneRegistryPath = Resolve-AiOsPath -Path $LaneRegistryPath
$resolvedWorkerRegistryPath = Resolve-AiOsPath -Path $WorkerRegistryPath

$laneRegistry = Read-AiOsJsonFile -Path $resolvedLaneRegistryPath -Label "Lane registry"
$workerRegistry = Read-AiOsJsonFile -Path $resolvedWorkerRegistryPath -Label "Worker registry"

$worktreeResult = Invoke-AiOsGit -Arguments @("worktree", "list", "--porcelain")
if ($worktreeResult.ExitCode -ne 0) {
    throw "git worktree list --porcelain failed."
}

$branchResult = Invoke-AiOsGit -Arguments @("branch", "--show-current")
$currentBranchLines = @($branchResult.Output | Where-Object { $_ -notmatch "^warning:" -and -not [string]::IsNullOrWhiteSpace($_) })
$currentBranch = if ($currentBranchLines.Count -gt 0) { $currentBranchLines[0] } else { "UNKNOWN" }
$gitWarnings = @(
    @(
        $worktreeResult.Output | Where-Object { $_ -match "^warning:" }
        $branchResult.Output | Where-Object { $_ -match "^warning:" }
    ) | Sort-Object -Unique
)

$registeredLanes = @($laneRegistry.lanes)
$registeredWorkers = @($workerRegistry.workers)
$worktrees = @(ConvertTo-AiOsWorktreeRows -Lines @($worktreeResult.Output | Where-Object { $_ -notmatch "^warning:" }))

$laneByPath = @{}
$laneByBranch = @{}
foreach ($lane in $registeredLanes) {
    $pathKey = ConvertTo-AiOsPathKey -Path "$($lane.path)"
    if (-not [string]::IsNullOrWhiteSpace($pathKey)) {
        $laneByPath[$pathKey.ToLowerInvariant()] = $lane
    }

    if (-not [string]::IsNullOrWhiteSpace("$($lane.branch)")) {
        $laneByBranch["$($lane.branch)".ToLowerInvariant()] = $lane
    }
}

$laneRows = @()
foreach ($worktree in $worktrees) {
    $path = "$($worktree.path)"
    $branch = if ($worktree.PSObject.Properties["branch"]) { "$($worktree.branch)" } else { "DETACHED_OR_UNKNOWN" }
    $pathKey = (ConvertTo-AiOsPathKey -Path $path).ToLowerInvariant()
    $branchKey = $branch.ToLowerInvariant()
    $registeredLane = $null
    $matchSource = "unregistered"

    if ($laneByPath.ContainsKey($pathKey)) {
        $registeredLane = $laneByPath[$pathKey]
        $matchSource = "path"
    } elseif ($laneByBranch.ContainsKey($branchKey)) {
        $registeredLane = $laneByBranch[$branchKey]
        $matchSource = "branch"
    }

    $status = Get-AiOsGitStatusCount -Path $path
    $laneRows += [pscustomobject]@{
        lane_id = if ($null -ne $registeredLane) { "$($registeredLane.lane_id)" } else { "UNREGISTERED" }
        registered = ($null -ne $registeredLane)
        match_source = $matchSource
        path = $path
        branch = $branch
        head = "$($worktree.head)"
        current_branch = ($branch -eq $currentBranch)
        dirty_count = $status.dirty_count
        dirty_files = $status.files
        read_errors = $status.errors
        status_read = $status.status
        git_warnings = $status.warnings
        role = if ($null -ne $registeredLane) { "$($registeredLane.role)" } else { "UNKNOWN" }
    }
}

$registeredWithoutWorktree = @()
foreach ($lane in $registeredLanes) {
    $lanePath = (ConvertTo-AiOsPathKey -Path "$($lane.path)").ToLowerInvariant()
    $laneBranch = "$($lane.branch)".ToLowerInvariant()
    $found = @($laneRows | Where-Object {
        (ConvertTo-AiOsPathKey -Path $_.path).ToLowerInvariant() -eq $lanePath -or $_.branch.ToLowerInvariant() -eq $laneBranch
    }).Count -gt 0

    if (-not $found) {
        $registeredWithoutWorktree += [pscustomobject]@{
            lane_id = "$($lane.lane_id)"
            path = "$($lane.path)"
            branch = "$($lane.branch)"
            role = "$($lane.role)"
        }
    }
}

$unregisteredRows = @($laneRows | Where-Object { -not $_.registered })
$dirtyRows = @($laneRows | Where-Object { $_.status_read -eq "READ" -and $_.dirty_count -gt 0 })
$readFailedRows = @($laneRows | Where-Object { $_.status_read -ne "READ" })
$warnings = @()
if ($unregisteredRows.Count -gt 0) {
    $warnings += "One or more git worktrees are not represented in the lane registry."
}
if ($registeredWithoutWorktree.Count -gt 0) {
    $warnings += "One or more registered lanes have no matching git worktree evidence."
}
if ($dirtyRows.Count -gt 0) {
    $warnings += "One or more worktrees have dirty or untracked files."
}
if ($readFailedRows.Count -gt 0) {
    $warnings += "One or more worktree status reads failed. Review safe.directory or permissions before trusting clean/dirty state."
}
if (@($laneRows | Where-Object { $_.current_branch }).Count -eq 0) {
    $warnings += "Current branch did not match a listed worktree branch."
}

$overallStatus = if ($warnings.Count -eq 0) { "PASS" } else { "WARN" }

$result = [pscustomobject]@{
    task = "AI_OS worker lane governance report"
    mode = "READ_ONLY"
    overall_status = $overallStatus
    current_branch = $currentBranch
    lane_registry_path = $resolvedLaneRegistryPath
    worker_registry_path = $resolvedWorkerRegistryPath
    counts = [pscustomobject]@{
        git_worktrees = $worktrees.Count
        registered_lanes = $registeredLanes.Count
        registered_workers = $registeredWorkers.Count
        unregistered_worktrees = $unregisteredRows.Count
        registered_lanes_without_worktree = $registeredWithoutWorktree.Count
        dirty_worktrees = $dirtyRows.Count
        status_read_failed = $readFailedRows.Count
    }
    lanes = $laneRows
    unregistered_worktrees = $unregisteredRows
    registered_lanes_without_worktree = $registeredWithoutWorktree
    status_read_failed = $readFailedRows
    warnings = $warnings
    git_warnings = $gitWarnings
    safety = [pscustomobject]@{
        writes_performed = 0
        commits_performed = 0
        pushes_performed = 0
        runtime_edits = "NO"
        dashboard_edits = "NO"
        policy_edits = "NO"
        telemetry_edits = "NO"
    }
    next_safe_action = if ($overallStatus -eq "PASS") { "Use Test-AiOsWorkerIsolation.ps1 before approving APPLY in any lane." } else { "Review unregistered, missing, or dirty lanes before assigning APPLY work." }
}

if ($OutputJson) {
    $result | ConvertTo-Json -Depth 8
    exit 0
}

Write-Host "AI_OS Worker Lane Governance"
Write-Host "Mode: READ_ONLY"
Write-Host "Status: $overallStatus"
Write-Host "Current branch: $currentBranch"
Write-Host "Git worktrees: $($result.counts.git_worktrees)"
Write-Host "Registered lanes: $($result.counts.registered_lanes)"
Write-Host "Unregistered worktrees: $($result.counts.unregistered_worktrees)"
Write-Host "Dirty worktrees: $($result.counts.dirty_worktrees)"
Write-Host ""

foreach ($lane in $laneRows) {
    Write-Host "Lane: $($lane.lane_id)"
    Write-Host "  Branch: $($lane.branch)"
    Write-Host "  Path: $($lane.path)"
    Write-Host "  Registered: $($lane.registered)"
    Write-Host "  Match source: $($lane.match_source)"
    Write-Host "  Dirty files: $($lane.dirty_count)"
    Write-Host ""
}

Write-Host "Warnings:"
if ($warnings.Count -eq 0) {
    Write-Host "  NONE"
} else {
    foreach ($warning in $warnings) {
        Write-Host "  - $warning"
    }
}
Write-Host ""
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host "Next safe action: $($result.next_safe_action)"
