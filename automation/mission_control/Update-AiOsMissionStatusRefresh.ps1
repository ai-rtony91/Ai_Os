[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$MissionPath,

    [switch]$Apply
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

function Resolve-RepoScopedPath {
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

function ConvertTo-ReportValue {
    param([string]$Value)

    if ([string]::IsNullOrWhiteSpace($Value)) {
        return 'Not found'
    }

    return ($Value.Trim() -replace '\r?\n', ' ')
}

function ConvertTo-BulletList {
    param([object[]]$Items)

    $values = @($Items | Where-Object { -not [string]::IsNullOrWhiteSpace([string]$_) })
    if ($values.Count -eq 0) {
        return '- None found'
    }

    return (($values | ForEach-Object { "- $_" }) -join [Environment]::NewLine)
}

function Get-LastMatch {
    param(
        [string]$Text,
        [string]$Pattern
    )

    $matches = [regex]::Matches($Text, $Pattern, [System.Text.RegularExpressions.RegexOptions]::Multiline)
    if ($matches.Count -gt 0) {
        return $matches[$matches.Count - 1].Groups[1].Value.Trim()
    }

    return ''
}

function Get-GitStatusSummary {
    param([string]$RepoRoot)

    $output = @(& git -C $RepoRoot status --short --branch 2>&1)
    if ($LASTEXITCODE -ne 0) {
        return @('git status unavailable: ' + (($output | ForEach-Object { [string]$_ }) -join ' '))
    }

    if ($output.Count -eq 1) {
        return @([string]$output[0], 'Working tree clean')
    }

    return @($output | ForEach-Object { [string]$_ })
}

function Get-ProofSummary {
    param(
        [string]$RepoRoot,
        [string]$MissionFullPath
    )

    $items = New-Object System.Collections.Generic.List[string]
    $missionProofPath = Join-Path $MissionFullPath 'proof'
    if (Test-Path -LiteralPath $missionProofPath -PathType Container) {
        $proofFiles = @(Get-ChildItem -LiteralPath $missionProofPath -File -Recurse | Sort-Object LastWriteTime -Descending)
        $items.Add("Mission proof files: $($proofFiles.Count)")
        foreach ($file in @($proofFiles | Select-Object -First 3)) {
            $items.Add("Proof: $(Get-RepoRelativePath -RepoRoot $RepoRoot -FullPath $file.FullName)")
        }
    }
    else {
        $items.Add('Mission proof folder: Not found')
    }

    $checkpointPath = Join-Path $RepoRoot 'checkpoints'
    if (Test-Path -LiteralPath $checkpointPath -PathType Container) {
        $checkpointFiles = @(Get-ChildItem -LiteralPath $checkpointPath -File | Sort-Object LastWriteTime -Descending)
        $items.Add("Checkpoint files: $($checkpointFiles.Count)")
        foreach ($file in @($checkpointFiles | Select-Object -First 3)) {
            $items.Add("Checkpoint: $(Get-RepoRelativePath -RepoRoot $RepoRoot -FullPath $file.FullName)")
        }
    }
    else {
        $items.Add('Checkpoint folder: Not found')
    }

    return @($items)
}

function Get-RuntimeLogSummary {
    param([string]$RepoRoot)

    $logRoot = Join-Path $RepoRoot 'automation/orchestration/runtime/logs'
    if (-not (Test-Path -LiteralPath $logRoot -PathType Container)) {
        return 'Runtime supervisor log: Not found'
    }

    $latestLog = @(Get-ChildItem -LiteralPath $logRoot -File -Recurse | Sort-Object LastWriteTime -Descending | Select-Object -First 1)
    if (-not $latestLog) {
        return 'Runtime supervisor log: No files found'
    }

    return "Runtime supervisor log: $(Get-RepoRelativePath -RepoRoot $RepoRoot -FullPath $latestLog.FullName)"
}

function Get-WorkPacketSummary {
    param([string]$RepoRoot)

    $packetRoot = Join-Path $RepoRoot 'automation/orchestration/work_packets'
    if (-not (Test-Path -LiteralPath $packetRoot -PathType Container)) {
        return @('Work packet folder: Not found')
    }

    $summary = New-Object System.Collections.Generic.List[string]
    foreach ($state in @('active', 'blocked', 'complete')) {
        $statePath = Join-Path $packetRoot $state
        if (Test-Path -LiteralPath $statePath -PathType Container) {
            $files = @(Get-ChildItem -LiteralPath $statePath -Filter '*.json' -File | Sort-Object LastWriteTime -Descending)
            $summary.Add("$state packets: $($files.Count)")
            foreach ($file in @($files | Select-Object -First 2)) {
                try {
                    $packet = Get-Content -LiteralPath $file.FullName -Raw | ConvertFrom-Json
                    $label = "$(ConvertTo-ReportValue -Value ([string]$packet.status)) - $(ConvertTo-ReportValue -Value ([string]$packet.title))"
                }
                catch {
                    $label = "Unreadable JSON - $(Get-RepoRelativePath -RepoRoot $RepoRoot -FullPath $file.FullName)"
                }

                $summary.Add("$state packet: $label")
            }
        }
        else {
            $summary.Add("$state packets: Not found")
        }
    }

    return @($summary)
}

$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..')).Path
$missionFullPath = Resolve-RepoScopedPath -RepoRoot $repoRoot -InputPath $MissionPath
$missionRelativePath = Get-RepoRelativePath -RepoRoot $repoRoot -FullPath $missionFullPath
$missionPlanPath = Join-Path $missionFullPath 'mission_plan.json'
$dashboardPath = Join-Path $missionFullPath 'mission_dashboard.md'
$dashboardRelativePath = Get-RepoRelativePath -RepoRoot $repoRoot -FullPath $dashboardPath

if (-not (Test-Path -LiteralPath $missionPlanPath -PathType Leaf)) {
    throw "mission_plan.json not found in $missionRelativePath"
}

if (-not (Test-Path -LiteralPath $dashboardPath -PathType Leaf)) {
    throw "mission_dashboard.md not found in $missionRelativePath"
}

$missionPlan = Get-Content -LiteralPath $missionPlanPath -Raw | ConvertFrom-Json
$dashboardText = Get-Content -LiteralPath $dashboardPath -Raw
$missionName = ConvertTo-ReportValue -Value ([string]$missionPlan.mission_name)
$missionGoal = ConvertTo-ReportValue -Value ([string]$missionPlan.goal)
$timestampUtc = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
$tasks = @($missionPlan.task_list)
$nextTask = @($tasks | Where-Object { $_.status -notin @('MERGED', 'SKIPPED') } | Select-Object -First 1)
if (-not $nextTask -and $tasks.Count -gt 0) {
    $nextTask = @($tasks | Select-Object -Last 1)
}

$currentTaskSummary = if ($nextTask) {
    "$($nextTask.task_id) - $($nextTask.title) [$($nextTask.status)]"
}
else {
    'No task entries found'
}

$lastProgressStatus = Get-LastMatch -Text $dashboardText -Pattern '^###\s+(.+?)\s*$'
if (-not [string]::IsNullOrWhiteSpace($lastProgressStatus)) {
    $currentTaskSummary = "$currentTaskSummary; latest dashboard entry: $lastProgressStatus"
}

$proofSummary = Get-ProofSummary -RepoRoot $repoRoot -MissionFullPath $missionFullPath
$gitStatusSummary = Get-GitStatusSummary -RepoRoot $repoRoot
$runtimeSummary = Get-RuntimeLogSummary -RepoRoot $repoRoot
$packetSummary = Get-WorkPacketSummary -RepoRoot $repoRoot

$blockers = New-Object System.Collections.Generic.List[string]
foreach ($blocker in @($missionPlan.blockers)) {
    $blockers.Add([string]$blocker)
}
foreach ($line in @($packetSummary | Where-Object { $_ -match '^blocked packet:' })) {
    $blockers.Add($line)
}
if (@($gitStatusSummary | Where-Object { $_ -match '^\?\?|^ M|^M |^A |^ D|^D ' }).Count -gt 0) {
    $blockers.Add('Working tree has local changes or untracked files; review before commit.')
}

$nextSafeAction = ConvertTo-ReportValue -Value ([string]$missionPlan.next_safe_action)
if ($nextSafeAction -eq 'Not found') {
    $nextSafeAction = 'Run Mission Control DRY_RUN validation before APPLY.'
}

$statusReport = @"
# Mission Dashboard - $missionName

## Mission

- Mission path: $missionRelativePath
- Goal: $missionGoal
- Refreshed UTC: $timestampUtc

## Current Task Summary

- $currentTaskSummary

## Proof Status

$(ConvertTo-BulletList -Items $proofSummary)

## Git Status Summary

$(ConvertTo-BulletList -Items $gitStatusSummary)

## Runtime Status

- $runtimeSummary

## Packet Status

$(ConvertTo-BulletList -Items $packetSummary)

## Blockers

$(ConvertTo-BulletList -Items @($blockers))

## Next Safe Action

$nextSafeAction
"@

Write-Host 'AIOS Mission Status Refresh v1'
Write-Host "Mode: $(if ($Apply) { 'APPLY' } else { 'DRY_RUN' })"
Write-Host "Mission path: $missionRelativePath"
Write-Host "Dashboard: $dashboardRelativePath"
Write-Host ''
Write-Host 'Status refresh preview:'
Write-Host $statusReport
Write-Host ''

if (-not $Apply) {
    Write-Host 'DRY_RUN complete. Mission dashboard changed: NO'
    Write-Host 'Commit performed: NO'
    Write-Host 'Push performed: NO'
    Write-Host 'Merge performed: NO'
    exit 0
}

Set-Content -LiteralPath $dashboardPath -Value $statusReport -Encoding UTF8

Write-Host 'APPLY complete. Mission dashboard changed: YES'
Write-Host "Updated file: $dashboardRelativePath"
Write-Host 'Commit performed: NO'
Write-Host 'Push performed: NO'
Write-Host 'Merge performed: NO'
