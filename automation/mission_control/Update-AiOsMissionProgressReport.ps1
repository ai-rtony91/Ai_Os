[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$MissionPath,

    [Parameter(Mandatory = $true)]
    [string]$TaskId,

    [Parameter(Mandatory = $true)]
    [ValidateSet('PLANNED', 'DRY_RUN_COMPLETE', 'APPLY_APPROVED', 'PR_OPENED', 'MERGED', 'BLOCKED', 'SKIPPED')]
    [string]$Status,

    [string]$PullRequest = '',

    [string]$ValidationResult = '',

    [string]$Blocker = '',

    [string]$NextSafeAction = '',

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
        return 'Not provided'
    }

    return ($Value.Trim() -replace '\r?\n', ' ')
}

function New-ProgressEntry {
    param(
        [string]$TaskId,
        [string]$Status,
        [string]$PullRequest,
        [string]$ValidationResult,
        [string]$Blocker,
        [string]$NextSafeAction,
        [string]$TimestampUtc
    )

    return @(
        "### $TaskId - $Status",
        '',
        "- Timestamp: $TimestampUtc",
        "- Task ID: $TaskId",
        "- Status: $Status",
        "- PR: $(ConvertTo-ReportValue -Value $PullRequest)",
        "- Validation: $(ConvertTo-ReportValue -Value $ValidationResult)",
        "- Blocker: $(ConvertTo-ReportValue -Value $Blocker)",
        "- Next safe action: $(ConvertTo-ReportValue -Value $NextSafeAction)"
    ) -join [Environment]::NewLine
}

function Update-ProgressSection {
    param(
        [string]$DashboardContent,
        [string]$Entry
    )

    $sectionHeading = '## Mission Progress Updates'
    if ($DashboardContent -notmatch '(?m)^## Mission Progress Updates\s*$') {
        return $DashboardContent.TrimEnd() + [Environment]::NewLine + [Environment]::NewLine + $sectionHeading + [Environment]::NewLine + [Environment]::NewLine + $Entry + [Environment]::NewLine
    }

    return $DashboardContent.TrimEnd() + [Environment]::NewLine + [Environment]::NewLine + $Entry + [Environment]::NewLine
}

$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..')).Path
$missionFullPath = Resolve-RepoScopedPath -RepoRoot $repoRoot -InputPath $MissionPath
$missionRelativePath = Get-RepoRelativePath -RepoRoot $repoRoot -FullPath $missionFullPath
$dashboardPath = Join-Path $missionFullPath 'mission_dashboard.md'
$dashboardRelativePath = Get-RepoRelativePath -RepoRoot $repoRoot -FullPath $dashboardPath

if (-not (Test-Path -LiteralPath $dashboardPath -PathType Leaf)) {
    throw "mission_dashboard.md not found: $dashboardRelativePath"
}

$dashboardContent = Get-Content -LiteralPath $dashboardPath -Raw
$timestampUtc = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
$entry = New-ProgressEntry `
    -TaskId $TaskId `
    -Status $Status `
    -PullRequest $PullRequest `
    -ValidationResult $ValidationResult `
    -Blocker $Blocker `
    -NextSafeAction $NextSafeAction `
    -TimestampUtc $timestampUtc
$updatedContent = Update-ProgressSection -DashboardContent $dashboardContent -Entry $entry

Write-Host 'AIOS Mission Progress Report Updater v1'
Write-Host "Mode: $(if ($Apply) { 'APPLY' } else { 'DRY_RUN' })"
Write-Host "Mission path: $missionRelativePath"
Write-Host "Dashboard: $dashboardRelativePath"
Write-Host ''
Write-Host 'Progress update preview:'
Write-Host $entry
Write-Host ''

if (-not $Apply) {
    Write-Host 'DRY_RUN complete. Mission dashboard changed: NO'
    Write-Host 'Commit performed: NO'
    Write-Host 'Push performed: NO'
    Write-Host 'Merge performed: NO'
    exit 0
}

Set-Content -LiteralPath $dashboardPath -Value $updatedContent -Encoding UTF8

Write-Host 'APPLY complete. Mission dashboard changed: YES'
Write-Host "Updated file: $dashboardRelativePath"
Write-Host 'Commit performed: NO'
Write-Host 'Push performed: NO'
Write-Host 'Merge performed: NO'
