[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$Goal,

    [string]$MissionName = '',

    [ValidateRange(1, 12)]
    [int]$WorkerCount = 4,

    [ValidateSet('auto', 'compact', 'wide', 'dual-monitor')]
    [string]$Preset = 'auto',

    [switch]$Apply
)

$ErrorActionPreference = 'Stop'

function ConvertTo-AiOsSlug {
    param([string]$Value)

    $slug = $Value.ToLowerInvariant() -replace '[^a-z0-9]+', '-'
    $slug = $slug.Trim('-')
    if ([string]::IsNullOrWhiteSpace($slug)) {
        return 'aios-mission'
    }

    return $slug
}

function ConvertTo-MarkdownList {
    param([object[]]$Items)

    if (-not $Items -or $Items.Count -eq 0) {
        return '- None'
    }

    return (($Items | ForEach-Object { "- $_" }) -join [Environment]::NewLine)
}

function Get-RecommendedPreset {
    param(
        [int]$Count,
        [string]$RequestedPreset
    )

    if ($RequestedPreset -ne 'auto') {
        return $RequestedPreset
    }

    if ($Count -le 4) {
        return 'compact'
    }

    if ($Count -le 7) {
        return 'wide'
    }

    return 'dual-monitor'
}

function New-MissionTask {
    param(
        [int]$Index,
        [int]$Total,
        [string]$MissionGoal
    )

    $workerName = 'WORKER-{0:00}' -f $Index
    $lane = switch ($Index) {
        1 { 'mission-planner' }
        2 { 'implementation-lane' }
        3 { 'validator-lane' }
        4 { 'dashboard-and-proof-lane' }
        default { 'support-lane' }
    }

    $title = switch ($Index) {
        1 { 'Convert goal into scoped work packet' }
        2 { 'Implement approved mission slice' }
        3 { 'Validate mission outputs and safety boundaries' }
        4 { 'Update mission dashboard and proof checklist' }
        default { "Support mission slice $Index of $Total" }
    }

    $prompt = @"
Task ID: MC-$('{0:00}' -f $Index)
Mode: DRY_RUN first, APPLY only after explicit approval.
Goal: $MissionGoal
Worker lane: $lane
Objective: $title
Allowed paths: repo-scoped paths explicitly approved by the mission plan.
Blocked paths: .aios_local_backup, protected root governance files unless approved, secrets, broker paths, live trading paths, startup tasks, scheduled tasks.
Validation: run relevant parser/check commands and git diff --check after changes.
Required report: files inspected, files created, files changed, validation result, git status, commit status, push status, blockers, next safe action.
"@

    return [ordered]@{
        task_id = 'MC-{0:00}' -f $Index
        worker = $workerName
        lane = $lane
        title = $title
        status = 'PLANNED'
        allowed_actions = @(
            'DRY_RUN planning',
            'Repo-scoped file inspection',
            'APPLY only after explicit approval',
            'Scoped validation'
        )
        blocked_actions = @(
            'No commits from generated worker prompts unless separately approved',
            'No pushes',
            'No GitHub merges',
            'No scheduled tasks',
            'No startup tasks',
            'No broker actions',
            'No trading actions',
            'No secrets'
        )
        prompt = $prompt.Trim()
    }
}

function Write-TextFile {
    param(
        [string]$Path,
        [string]$Content
    )

    Set-Content -LiteralPath $Path -Value $Content -Encoding UTF8
}

$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..')).Path
$templatePath = Join-Path $PSScriptRoot 'AIOS_MISSION_TEMPLATE.json'

if (-not (Test-Path -LiteralPath $templatePath -PathType Leaf)) {
    throw "Mission template not found: $templatePath"
}

$template = Get-Content -LiteralPath $templatePath -Raw | ConvertFrom-Json
$mode = if ($Apply) { 'APPLY' } else { 'DRY_RUN' }
$resolvedMissionName = if ([string]::IsNullOrWhiteSpace($MissionName)) { $Goal } else { $MissionName }
$missionSlug = ConvertTo-AiOsSlug -Value $resolvedMissionName
$recommendedPreset = Get-RecommendedPreset -Count $WorkerCount -RequestedPreset $Preset
$timestampUtc = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
$missionsRoot = Join-Path $PSScriptRoot 'missions'
$missionFolder = Join-Path $missionsRoot $missionSlug

$missionStages = @(
    [ordered]@{
        id = 'stage-01'
        name = 'Goal intake'
        purpose = 'Capture the human goal and convert it into a repo-safe mission.'
        exit_criteria = 'Mission plan, worker tasks, validation plan, merge order, and dashboard are generated.'
    },
    [ordered]@{
        id = 'stage-02'
        name = 'Worker execution planning'
        purpose = 'Split the mission into Codex-ready worker prompts.'
        exit_criteria = 'Each planned worker has a scoped task, blocked actions, and validation expectations.'
    },
    [ordered]@{
        id = 'stage-03'
        name = 'Validation and proof'
        purpose = 'Define safe verification before commit, push, PR review, or merge.'
        exit_criteria = 'Validation proof is attached to the mission dashboard.'
    },
    [ordered]@{
        id = 'stage-04'
        name = 'PR sequencing'
        purpose = 'Recommend merge order and stop conditions.'
        exit_criteria = 'Dependent PRs are ordered from foundation to validation to dashboard proof.'
    }
)

$tasks = @(
    for ($i = 1; $i -le $WorkerCount; $i++) {
        New-MissionTask -Index $i -Total $WorkerCount -MissionGoal $Goal
    }
)

$validationChecklist = @(
    'Confirm generated mission_plan.json parses as JSON.',
    'Confirm generated Markdown files are readable and contain next safe action.',
    'Run PowerShell parser checks for any changed PowerShell files.',
    'Run relevant scoped validators for implementation PRs.',
    'Run git diff --check before commit.',
    'Confirm no secrets, broker actions, trading actions, startup tasks, or scheduled tasks were introduced.'
)

$mergeOrder = @(
    [ordered]@{
        order = 1
        lane = 'foundation'
        description = 'Merge config, schemas, or scaffolding PRs first because later implementation depends on stable structure.'
    },
    [ordered]@{
        order = 2
        lane = 'implementation'
        description = 'Merge scoped implementation PRs after foundation validation passes.'
    },
    [ordered]@{
        order = 3
        lane = 'validation'
        description = 'Merge validator or proof updates after implementation behavior is known.'
    },
    [ordered]@{
        order = 4
        lane = 'dashboard'
        description = 'Merge dashboard/status updates last so they reflect the final accepted proof.'
    }
)

$blockers = @(
    'Human approval required before APPLY implementation work.',
    'Validation proof missing until worker PRs run their checks.',
    'PR status placeholders must be replaced with real PR links before merge decisions.',
    'No live trading, broker, secrets, startup tasks, scheduled tasks, or destructive actions are allowed.'
)

$nextSafeAction = if ($Apply) {
    "Review mission folder $missionFolder and choose the first DRY_RUN worker prompt from codex_tasks.md."
}
else {
    "Review this DRY_RUN output, then rerun with -Apply only after approving mission folder $missionFolder."
}

$missionPlan = [ordered]@{
    mission_name = $resolvedMissionName
    goal = $Goal
    generated_timestamp_utc = $timestampUtc
    recommended_worker_layout_preset = $recommendedPreset
    requested_preset = $Preset
    worker_count = $WorkerCount
    mission_stages = $missionStages
    task_list = $tasks
    validation_checklist = $validationChecklist
    merge_order = $mergeOrder
    blockers = $blockers
    next_safe_action = $nextSafeAction
    safety = [ordered]@{
        mode = $mode
        repo_scoped_only = $true
        commits_performed = 'NO'
        pushes_performed = 'NO'
        github_merges_performed = 'NO'
        scheduled_tasks_created = 'NO'
        startup_tasks_created = 'NO'
        broker_actions_performed = 'NO'
        trading_actions_performed = 'NO'
        secrets_touched = 'NO'
        external_network_calls = 'NO'
    }
}

$taskSections = @(
    "# Codex Tasks - $resolvedMissionName",
    '',
    "Goal: $Goal",
    '',
    'Copy one prompt at a time into Codex. Each worker must start in DRY_RUN.',
    ''
)
foreach ($task in $tasks) {
    $taskSections += "## $($task.task_id) - $($task.title)"
    $taskSections += ''
    $taskSections += '```text'
    $taskSections += $task.prompt
    $taskSections += '```'
    $taskSections += ''
}

$validationPlanContent = @"
# Validation Plan - $resolvedMissionName

## Safety Boundary

This mission is repo-scoped only. Do not use live trading, brokers, OANDA, API keys, secrets, startup tasks, scheduled tasks, GitHub merges, commits, pushes, or external network calls from generated runtime scripts.

## Required Checks

$(ConvertTo-MarkdownList -Items $validationChecklist)

## Proof Required

- Terminal output or validator logs for each check.
- Git status before commit and before PR review.
- PR links and CI/check status when PRs exist.
- Mismatch, UNKNOWN, or INVALID DATA notes if evidence conflicts.

## PASS/WARN/BLOCKED Rules

- PASS: required files exist, parsers pass, JSON parses, validators pass, and no blocked actions are present.
- WARN: validation is incomplete but no blocked action is observed.
- BLOCKED: any secret, broker, trading, startup, scheduled task, destructive action, or unapproved APPLY scope appears.

Next safe action: run the first worker task as DRY_RUN and attach validation proof before APPLY.
"@

$mergeOrderRows = @(
    foreach ($item in $mergeOrder) {
        "| $($item.order) | $($item.lane) | $($item.description) |"
    }
)
$mergeOrderContent = @"
# Merge Order - $resolvedMissionName

| Order | Lane | Reason |
|---:|---|---|
$($mergeOrderRows -join [Environment]::NewLine)

## Merge Rules

- Do not merge PRs without validation proof.
- Merge foundation before implementation.
- Merge implementation before validation/dashboard proof.
- Stop if a PR touches secrets, broker actions, trading actions, startup tasks, scheduled tasks, protected root governance files without approval, or unrelated paths.

Next safe action: replace PR placeholders in the dashboard with real PR links and current check status before merge review.
"@

$activeTaskRows = @(
    foreach ($task in $tasks) {
        "| $($task.task_id) | $($task.worker) | $($task.title) | $($task.status) | PENDING |"
    }
)
$dashboardContent = @"
# Mission Dashboard - $resolvedMissionName

## Current Mission

- Goal: $Goal
- Generated UTC: $timestampUtc
- Recommended worker layout preset: $recommendedPreset
- Worker count: $WorkerCount

## Active Tasks

| Task | Worker | Title | Status | Proof |
|---|---|---|---|---|
$($activeTaskRows -join [Environment]::NewLine)

## Blockers

$(ConvertTo-MarkdownList -Items $blockers)

## Proof Status

- Mission plan generated: PENDING REVIEW
- Codex worker prompts generated: PENDING REVIEW
- Validation proof attached: PENDING
- Git diff check: PENDING
- JSON parse proof: PENDING
- PowerShell parser proof: PENDING

## PR Status Placeholders

- Foundation PR: PENDING
- Implementation PR: PENDING
- Validation PR: PENDING
- Dashboard/proof PR: PENDING

## Next Safe Action

$nextSafeAction
"@

$plannedFiles = @(
    (Join-Path $missionFolder 'mission_plan.json')
    (Join-Path $missionFolder 'codex_tasks.md')
    (Join-Path $missionFolder 'validation_plan.md')
    (Join-Path $missionFolder 'merge_order.md')
    (Join-Path $missionFolder 'mission_dashboard.md')
)

Write-Host 'AIOS Mission Control v1'
Write-Host "Mode: $mode"
Write-Host "Mission name: $resolvedMissionName"
Write-Host "Goal: $Goal"
Write-Host "Worker count: $WorkerCount"
Write-Host "Recommended worker layout preset: $recommendedPreset"
Write-Host "Mission folder: $missionFolder"
Write-Host 'Safety: repo-scoped file generation only. No commits, pushes, merges, scheduled tasks, startup tasks, broker actions, trading actions, secrets, or external network calls.'
Write-Host ''
Write-Host 'Planned files:'
foreach ($file in $plannedFiles) {
    Write-Host "- $file"
}
Write-Host ''

if (-not $Apply) {
    Write-Host 'PASS: DRY_RUN complete. No files were created or changed.'
    Write-Host "Next safe action: $nextSafeAction"
    Write-Host 'Commit performed: NO'
    Write-Host 'Push performed: NO'
    exit 0
}

New-Item -ItemType Directory -Path $missionFolder -Force | Out-Null

$missionPlanJson = $missionPlan | ConvertTo-Json -Depth 12
Write-TextFile -Path (Join-Path $missionFolder 'mission_plan.json') -Content $missionPlanJson
Write-TextFile -Path (Join-Path $missionFolder 'codex_tasks.md') -Content ($taskSections -join [Environment]::NewLine)
Write-TextFile -Path (Join-Path $missionFolder 'validation_plan.md') -Content $validationPlanContent
Write-TextFile -Path (Join-Path $missionFolder 'merge_order.md') -Content $mergeOrderContent
Write-TextFile -Path (Join-Path $missionFolder 'mission_dashboard.md') -Content $dashboardContent

Write-Host 'PASS: APPLY complete. Mission files created.'
Write-Host "Next safe action: $nextSafeAction"
Write-Host 'Commit performed: NO'
Write-Host 'Push performed: NO'
