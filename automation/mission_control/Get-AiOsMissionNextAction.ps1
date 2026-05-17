[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$MissionPath,

    [string]$TaskId = '',

    [switch]$ShowPrompt
)

$ErrorActionPreference = 'Stop'

function Get-RepoRelativePath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$RepoRoot,

        [Parameter(Mandatory = $true)]
        [string]$FullPath
    )

    $root = $RepoRoot.TrimEnd('\', '/')
    if ($FullPath.StartsWith($root, [System.StringComparison]::OrdinalIgnoreCase)) {
        return ($FullPath.Substring($root.Length).TrimStart('\', '/') -replace '\\', '/')
    }

    return ($FullPath -replace '\\', '/')
}

function Resolve-MissionPath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$RepoRoot,

        [Parameter(Mandatory = $true)]
        [string]$InputPath
    )

    $candidate = if ([System.IO.Path]::IsPathRooted($InputPath)) {
        $InputPath
    }
    else {
        Join-Path $RepoRoot $InputPath
    }

    $resolved = (Resolve-Path -LiteralPath $candidate).Path
    $repoPrefix = $RepoRoot.TrimEnd('\', '/') + [System.IO.Path]::DirectorySeparatorChar
    if ($resolved -ne $RepoRoot -and -not $resolved.StartsWith($repoPrefix, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "MissionPath must resolve inside the repo: $InputPath"
    }

    return $resolved
}

function Read-RequiredTextFile {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "Required mission file missing: $Path"
    }

    return Get-Content -LiteralPath $Path -Raw
}

function ConvertTo-SummaryLine {
    param([object[]]$Items)

    $values = @($Items | Where-Object { -not [string]::IsNullOrWhiteSpace([string]$_) } | Select-Object -First 3)
    if ($values.Count -eq 0) {
        return 'None listed.'
    }

    return ($values -join '; ')
}

$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..')).Path
$missionFullPath = Resolve-MissionPath -RepoRoot $repoRoot -InputPath $MissionPath
$missionRelativePath = Get-RepoRelativePath -RepoRoot $repoRoot -FullPath $missionFullPath

$requiredFiles = [ordered]@{
    mission_plan = Join-Path $missionFullPath 'mission_plan.json'
    codex_tasks = Join-Path $missionFullPath 'codex_tasks.md'
    validation_plan = Join-Path $missionFullPath 'validation_plan.md'
    merge_order = Join-Path $missionFullPath 'merge_order.md'
    mission_dashboard = Join-Path $missionFullPath 'mission_dashboard.md'
}

$missionPlanText = Read-RequiredTextFile -Path $requiredFiles.mission_plan
$codexTasksText = Read-RequiredTextFile -Path $requiredFiles.codex_tasks
$validationPlanText = Read-RequiredTextFile -Path $requiredFiles.validation_plan
$mergeOrderText = Read-RequiredTextFile -Path $requiredFiles.merge_order
$missionDashboardText = Read-RequiredTextFile -Path $requiredFiles.mission_dashboard

$missionPlan = $missionPlanText | ConvertFrom-Json
$tasks = @($missionPlan.task_list)
if ($tasks.Count -eq 0) {
    throw "Mission plan has no task_list entries: $($requiredFiles.mission_plan)"
}

$selectedTask = if ([string]::IsNullOrWhiteSpace($TaskId)) {
    @($tasks | Where-Object { $_.status -eq 'PLANNED' } | Select-Object -First 1)
}
else {
    @($tasks | Where-Object { $_.task_id -eq $TaskId } | Select-Object -First 1)
}

if (-not $selectedTask) {
    $availableTaskIds = @($tasks | ForEach-Object { $_.task_id })
    throw "Task not found: $TaskId. Available tasks: $($availableTaskIds -join ', ')"
}

$validationSummary = ConvertTo-SummaryLine -Items @($missionPlan.validation_checklist)
$mergeSummary = ConvertTo-SummaryLine -Items @($missionPlan.merge_order | ForEach-Object { "$($_.order): $($_.lane) - $($_.description)" })
$blockerSummary = ConvertTo-SummaryLine -Items @($missionPlan.blockers)
$nextSafeAction = [string]$missionPlan.next_safe_action

Write-Host 'AIOS Mission Runner v1'
Write-Host 'Mode: READ_ONLY'
Write-Host "Mission path: $missionRelativePath"
Write-Host ''
Write-Host "Current mission: $($missionPlan.mission_name)"
Write-Host "Mission goal: $($missionPlan.goal)"
Write-Host "Recommended worker layout preset: $($missionPlan.recommended_worker_layout_preset)"
Write-Host ''
Write-Host "Next planned task: $($selectedTask.task_id) - $($selectedTask.title)"
Write-Host "Task status: $($selectedTask.status)"
Write-Host "Worker lane: $($selectedTask.lane)"
Write-Host ''
Write-Host "Required validation summary: $validationSummary"
Write-Host "Merge warning summary: $mergeSummary"
Write-Host "Blockers: $blockerSummary"
Write-Host ''
Write-Host "Next safe action: $nextSafeAction"
Write-Host ''
Write-Host 'Files read:'
foreach ($file in $requiredFiles.Values) {
    Write-Host "- $(Get-RepoRelativePath -RepoRoot $repoRoot -FullPath $file)"
}

if ($ShowPrompt) {
    Write-Host ''
    Write-Host "Codex prompt for $($selectedTask.task_id):"
    Write-Host '```text'
    Write-Host $selectedTask.prompt
    Write-Host '```'
}

Write-Host ''
Write-Host 'Mission files changed: NO'
Write-Host 'Commit performed: NO'
Write-Host 'Push performed: NO'
Write-Host 'Merge performed: NO'

$null = $codexTasksText
$null = $validationPlanText
$null = $mergeOrderText
$null = $missionDashboardText
