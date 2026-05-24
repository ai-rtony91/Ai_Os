[CmdletBinding()]
param(
    [ValidateSet('DRY_RUN', 'APPLY')]
    [string]$Mode = 'DRY_RUN',

    [string]$RepoRoot,

    [string]$Task = 'Automated AI_OS reporting',

    [string]$Notes = '',

    [string]$SessionStart,

    [string]$SessionEnd,

    [int]$ManualMessageCountUser = 0,

    [int]$ManualMessageCountAssistant = 0,

    [switch]$AllowDifferentRepoRoot
)

$ErrorActionPreference = 'Stop'
$expectedRepoRoot = 'C:\Dev\Ai.Os'
$csvColumns = @(
    'date',
    'timestamp',
    'mode',
    'repo_root',
    'branch',
    'git_status_clean',
    'total_files',
    'total_folders',
    'total_bytes',
    'total_kb',
    'total_mb',
    'session_start',
    'session_end',
    'duration_minutes',
    'manual_message_count_user',
    'manual_message_count_assistant',
    'manual_message_count_total',
    'checkpoint_file',
    'daily_report_file',
    'notes',
    'script_runtime_seconds',
    'bytes_created',
    'kb_created',
    'mb_created',
    'apply_run_count',
    'dry_run_count'
)

function Resolve-RepoRoot {
    param([string]$InputRepoRoot)

    if ([string]::IsNullOrWhiteSpace($InputRepoRoot)) {
        return (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..')).Path
    }

    return (Resolve-Path -LiteralPath $InputRepoRoot).Path
}

function ConvertTo-LocalDateTime {
    param(
        [string]$Value,
        [datetime]$Default
    )

    if ([string]::IsNullOrWhiteSpace($Value)) {
        return $Default
    }

    return [datetime]::Parse($Value, [Globalization.CultureInfo]::InvariantCulture)
}

function Invoke-Git {
    param(
        [string]$RepoRoot,
        [string[]]$Arguments
    )

    $output = & git -C $RepoRoot @Arguments 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "git $($Arguments -join ' ') failed: $($output -join [Environment]::NewLine)"
    }

    return @($output)
}

function Test-ExcludedPath {
    param(
        [System.IO.FileSystemInfo]$Item,
        [string]$RepoRoot
    )

    $relativePath = $Item.FullName.Substring($RepoRoot.Length).TrimStart('\', '/')
    $normalized = $relativePath -replace '/', '\'

    if ($normalized -match '(^|\\)\.git(\\|$)') {
        return $true
    }

    if ($normalized -match '(^|\\)node_modules(\\|$)') {
        return $true
    }

    if (-not $Item.PSIsContainer -and $normalized -match '^Reports\\daily\\.*_INVENTORY_.*\.txt$') {
        return $true
    }

    if (-not $Item.PSIsContainer -and $normalized -match '^Reports\\daily\\.*_DRY_RUN_REPORT.*\.txt$') {
        return $true
    }

    return $false
}

function Get-RelativePath {
    param(
        [string]$RepoRoot,
        [string]$FullName
    )

    return $FullName.Substring($RepoRoot.Length).TrimStart('\', '/')
}

function New-MarkdownList {
    param([object[]]$Items)

    if ($Items.Count -eq 0) {
        return '- None'
    }

    return (($Items | ForEach-Object { "- $_" }) -join [Environment]::NewLine)
}

function ConvertTo-CsvLine {
    param([pscustomobject]$Row)

    return @($Row | ConvertTo-Csv -NoTypeInformation)[1]
}

function New-MetricsObject {
    param(
        [hashtable]$Values
    )

    $object = [ordered]@{}
    foreach ($column in $csvColumns) {
        if ($Values.ContainsKey($column)) {
            $object[$column] = $Values[$column]
        }
        else {
            $object[$column] = ''
        }
    }

    return [pscustomobject]$object
}

function Get-RepoInventory {
    param([string]$RepoRoot)

    $allItems = @(Get-ChildItem -LiteralPath $RepoRoot -Force -Recurse | Where-Object {
        -not (Test-ExcludedPath -Item $_ -RepoRoot $RepoRoot)
    })
    $files = @($allItems | Where-Object { -not $_.PSIsContainer })
    $folders = @($allItems | Where-Object { $_.PSIsContainer })
    $totalBytes = [int64](($files | Measure-Object -Property Length -Sum).Sum)

    return [pscustomobject]@{
        Items = $allItems
        Files = $files
        Folders = $folders
        TotalBytes = $totalBytes
        TotalKb = [math]::Round($totalBytes / 1KB, 2)
        TotalMb = [math]::Round($totalBytes / 1MB, 2)
    }
}

function Get-MetricsRunCounts {
    param(
        [object[]]$Rows
    )

    $applyRunCount = 0
    $dryRunCount = 0

    foreach ($row in $Rows) {
        $rowApplyCount = 0
        $rowDryCount = 0

        if ($row.PSObject.Properties.Name -contains 'apply_run_count' -and [int]::TryParse([string]$row.apply_run_count, [ref]$rowApplyCount)) {
            $applyRunCount = [math]::Max($applyRunCount, $rowApplyCount)
        }

        if ($row.PSObject.Properties.Name -contains 'dry_run_count' -and [int]::TryParse([string]$row.dry_run_count, [ref]$rowDryCount)) {
            $dryRunCount = [math]::Max($dryRunCount, $rowDryCount)
        }
    }

    return [pscustomobject]@{
        ApplyRunCount = $applyRunCount
        DryRunCount = $dryRunCount
    }
}

function Read-NormalizedCsvRows {
    param([string]$Path)

    if (-not (Test-Path -LiteralPath $Path)) {
        return @()
    }

    $existingRows = @(Import-Csv -LiteralPath $Path)
    return @(
        foreach ($existingRow in $existingRows) {
            $values = @{}
            foreach ($column in $csvColumns) {
                if ($existingRow.PSObject.Properties.Name -contains $column) {
                    $values[$column] = $existingRow.$column
                }
            }
            New-MetricsObject -Values $values
        }
    )
}

function Write-TextFile {
    param(
        [string]$Path,
        [string]$Content
    )

    Set-Content -LiteralPath $Path -Value $Content -Encoding UTF8
}

function Update-DailyStatusSnapshot {
    param(
        [string]$Mode,
        [string]$SnapshotPath,
        [string]$CheckpointPath,
        [string]$DailyReportPath,
        [string]$MetricsCsvPath,
        [string]$CheckpointIndexPath,
        [string]$DateStamp,
        [string]$GitStatusSummary,
        [string]$CheckpointRelativePath,
        [string]$DailyRelativePath
    )

    $expectedSnapshotPath = 'C:\Users\mylab\OneDrive\AI-OS-Project\00_AI_OS_CONTEXT_PACKET\Morning work-order\06_DAILY_STATUS_SNAPSHOT.txt'

    if ($Mode -ne 'APPLY') {
        throw 'Snapshot update is only allowed in APPLY mode.'
    }

    if ($SnapshotPath -ine $expectedSnapshotPath) {
        throw "SnapshotPath rejected. Expected '$expectedSnapshotPath'. Received '$SnapshotPath'."
    }

    if ((Split-Path -Path $SnapshotPath -Leaf) -ne '06_DAILY_STATUS_SNAPSHOT.txt') {
        throw 'Snapshot target filename rejected.'
    }

    $snapshotParent = Split-Path -Path $SnapshotPath -Parent
    if (-not (Test-Path -LiteralPath $snapshotParent -PathType Container)) {
        throw "Snapshot parent folder not found: $snapshotParent"
    }

    if (-not (Test-Path -LiteralPath $CheckpointPath -PathType Leaf)) {
        throw "Generated checkpoint file not found: $CheckpointPath"
    }

    if (-not (Test-Path -LiteralPath $DailyReportPath -PathType Leaf)) {
        throw "Generated daily report file not found: $DailyReportPath"
    }

    if (-not (Test-Path -LiteralPath $MetricsCsvPath -PathType Leaf)) {
        throw "Metrics CSV not found: $MetricsCsvPath"
    }

    if (-not (Test-Path -LiteralPath $CheckpointIndexPath -PathType Leaf)) {
        throw "Checkpoint index not found: $CheckpointIndexPath"
    }

    if ($CheckpointRelativePath -notlike 'Reports\checkpoints\CHECKPOINT_*') {
        throw "Checkpoint relative path rejected: $CheckpointRelativePath"
    }

    if ($DailyRelativePath -notlike 'Reports\daily\DAILY_REPORT_*') {
        throw "Daily report relative path rejected: $DailyRelativePath"
    }

    if ($GitStatusSummary -notin @('clean', 'dirty')) {
        throw "Git status summary rejected: $GitStatusSummary"
    }

    $snapshotContent = @"
AI-OS DAILY STATUS SNAPSHOT

Date: $DateStamp
Current stage: BUILD
Current phase: Phase 1.5 - Reporting automation and context packet maintenance
Repo status: $GitStatusSummary
Last checkpoint file: $CheckpointRelativePath
Last daily report file: $DailyRelativePath
Last completed step: Automated AI_OS reporting APPLY run completed.
Next safe action: Review the generated checkpoint/report files and decide whether to continue in DRY_RUN or APPLY.
"@

    if ($snapshotContent -match '(?im)^\s*(\?\?|M|A|D|R|C|U)\s+') {
        throw 'Snapshot content rejected because it appears to contain raw git status lines.'
    }

    if ($snapshotContent -match '(?i)(secret|token|password|api[_-]?key|env:)') {
        throw 'Snapshot content rejected because it appears to contain secret-like text.'
    }

    Write-TextFile -Path $SnapshotPath -Content $snapshotContent
}

try {
    $scriptStart = Get-Date
    $resolvedRepoRoot = Resolve-RepoRoot -InputRepoRoot $RepoRoot

    if (-not $AllowDifferentRepoRoot -and ($resolvedRepoRoot.TrimEnd('\') -ine $expectedRepoRoot.TrimEnd('\'))) {
        throw "RepoRoot rejected. Expected '$expectedRepoRoot'. Received '$resolvedRepoRoot'. Use -AllowDifferentRepoRoot to override."
    }

    if (-not (Test-Path -LiteralPath (Join-Path $resolvedRepoRoot '.git'))) {
        throw ".git not found under '$resolvedRepoRoot'."
    }

    if ($ManualMessageCountUser -lt 0 -or $ManualMessageCountAssistant -lt 0) {
        throw 'Manual message counts cannot be negative.'
    }

    $sessionStartDate = ConvertTo-LocalDateTime -Value $SessionStart -Default $scriptStart
    $sessionEndDate = ConvertTo-LocalDateTime -Value $SessionEnd -Default (Get-Date)

    if ($sessionEndDate -lt $sessionStartDate) {
        throw 'SessionEnd cannot be earlier than SessionStart.'
    }

    $durationMinutes = [math]::Round(($sessionEndDate - $sessionStartDate).TotalMinutes, 2)
    $manualMessageCountTotal = $ManualMessageCountUser + $ManualMessageCountAssistant
    $timestampDate = Get-Date
    $dateStamp = $timestampDate.ToString('yyyy-MM-dd')
    $timestampStamp = $timestampDate.ToString('yyyy-MM-dd HH:mm:ss')
    $fileStamp = $timestampDate.ToString('yyyy-MM-dd_HHmmss')

    $reportsRoot = Join-Path $resolvedRepoRoot 'Reports'
    $checkpointDir = Join-Path $reportsRoot 'checkpoints'
    $dailyDir = Join-Path $reportsRoot 'daily'
    $checkpointRelativePath = "Reports\checkpoints\CHECKPOINT_${fileStamp}_AI_OS.md"
    $dailyRelativePath = "Reports\daily\DAILY_REPORT_${dateStamp}_AI_OS.md"
    $checkpointPath = Join-Path $resolvedRepoRoot $checkpointRelativePath
    $dailyReportPath = Join-Path $resolvedRepoRoot $dailyRelativePath
    $metricsCsvPath = Join-Path $reportsRoot 'DAILY_METRICS.csv'
    $checkpointIndexPath = Join-Path $reportsRoot 'CHECKPOINT_INDEX.md'
    $dailyStatusSnapshotPath = 'C:\Users\mylab\OneDrive\AI-OS-Project\00_AI_OS_CONTEXT_PACKET\Morning work-order\06_DAILY_STATUS_SNAPSHOT.txt'

    $branch = (Invoke-Git -RepoRoot $resolvedRepoRoot -Arguments @('branch', '--show-current') | Select-Object -First 1)
    if ([string]::IsNullOrWhiteSpace($branch)) {
        $branch = 'UNKNOWN'
    }

    $remoteLines = Invoke-Git -RepoRoot $resolvedRepoRoot -Arguments @('remote', '-v')
    $statusLines = Invoke-Git -RepoRoot $resolvedRepoRoot -Arguments @('status', '--short')
    $gitStatusClean = ($statusLines.Count -eq 0)
    $gitStatusSummary = if ($gitStatusClean) { 'clean' } else { 'dirty' }

    $beforeInventory = Get-RepoInventory -RepoRoot $resolvedRepoRoot
    $files = $beforeInventory.Files
    $folders = $beforeInventory.Folders
    $totalBytes = $beforeInventory.TotalBytes
    $totalKb = $beforeInventory.TotalKb
    $totalMb = $beforeInventory.TotalMb

    $lastModifiedRows = @(
        $files |
            Sort-Object LastWriteTime -Descending |
            Select-Object -First 20 |
            ForEach-Object {
                '| {0} | {1} | {2} |' -f $_.LastWriteTime.ToString('yyyy-MM-dd HH:mm:ss'), ([math]::Round($_.Length / 1KB, 2)), (Get-RelativePath -RepoRoot $resolvedRepoRoot -FullName $_.FullName)
            }
    )
    if ($lastModifiedRows.Count -eq 0) {
        $lastModifiedRows = @('| UNKNOWN | 0 | No files found |')
    }

    $statusMarkdown = if ($gitStatusClean) {
        '- Clean working tree'
    }
    else {
        New-MarkdownList -Items $statusLines
    }

    $remoteMarkdown = New-MarkdownList -Items $remoteLines
    $filesInspected = @(
        'Project filesystem inventory excluding .git, node_modules, and ignored raw report dumps',
        'Git branch, remotes, and short status'
    )
    $errors = @()
    $unknowns = @()

    $checkpointContent = @"
# AI_OS Checkpoint - $timestampStamp

## Repository
- Repo root: `$resolvedRepoRoot`
- Branch: `$branch`
- Git status: `$gitStatusSummary`

## Remotes
$remoteMarkdown

## Metrics
- Total files: `$($files.Count)`
- Total folders: `$($folders.Count)`
- Total bytes: `$totalBytes`
- Total KB: `$totalKb`
- Total MB: `$totalMb`

## Session
- Session start: `$($sessionStartDate.ToString('yyyy-MM-dd HH:mm:ss'))`
- Session end: `$($sessionEndDate.ToString('yyyy-MM-dd HH:mm:ss'))`
- Duration minutes: `$durationMinutes`
- Manual user messages: `$ManualMessageCountUser`
- Manual assistant messages: `$ManualMessageCountAssistant`
- Manual total messages: `$manualMessageCountTotal`

## Last Modified Files
| Last modified | Size KB | Path |
|---|---:|---|
$($lastModifiedRows -join [Environment]::NewLine)

## Report Summary
- Task: $Task
- Files inspected: $(($filesInspected -join '; '))
- Files changed: None in DRY_RUN; report artifacts only in APPLY
- Result: $Mode report generation prepared
- Errors: $(if ($errors.Count -eq 0) { 'None' } else { $errors -join '; ' })
- Unknowns: $(if ($unknowns.Count -eq 0) { 'None' } else { $unknowns -join '; ' })
- Next safe action: Review this checkpoint and run the script with `-Mode APPLY` only when ready to write report artifacts.

## Git Status Details
$statusMarkdown
"@

    $dailyReportContent = @"
# AI_OS Daily Report - $dateStamp

## Run
- Timestamp: `$timestampStamp`
- Task: $Task
- Mode: `$Mode`
- Checkpoint: `$checkpointRelativePath`

## Metrics Summary
- Total files: `$($files.Count)`
- Total folders: `$($folders.Count)`
- Total size: `$totalKb KB / $totalMb MB`

## Session Tracking
- Session start: `$($sessionStartDate.ToString('yyyy-MM-dd HH:mm:ss'))`
- Session end: `$($sessionEndDate.ToString('yyyy-MM-dd HH:mm:ss'))`
- Duration minutes: `$durationMinutes`
- Manual user messages: `$ManualMessageCountUser`
- Manual assistant messages: `$ManualMessageCountAssistant`
- Manual total messages: `$manualMessageCountTotal`

## Git Status
- Branch: `$branch`
- Status: `$gitStatusSummary`

## Errors And Unknowns
- Errors: None
- Unknowns: None

## Next Safe Action
Review the generated checkpoint and confirm whether the next workflow should continue in DRY_RUN or APPLY.
"@

    $normalizedRows = @(Read-NormalizedCsvRows -Path $metricsCsvPath)
    $runCounts = Get-MetricsRunCounts -Rows $normalizedRows
    $scriptRuntimeSeconds = [math]::Round(((Get-Date) - $scriptStart).TotalSeconds, 2)
    $bytesCreated = 0
    $kbCreated = 0
    $mbCreated = 0
    $applyRunCount = $runCounts.ApplyRunCount
    $dryRunCount = $runCounts.DryRunCount

    $metricsRowValues = @{
        date = $dateStamp
        timestamp = $timestampStamp
        mode = $Mode
        repo_root = $resolvedRepoRoot
        branch = $branch
        git_status_clean = $gitStatusClean.ToString().ToLowerInvariant()
        total_files = $files.Count
        total_folders = $folders.Count
        total_bytes = $totalBytes
        total_kb = $totalKb
        total_mb = $totalMb
        session_start = $sessionStartDate.ToString('yyyy-MM-dd HH:mm:ss')
        session_end = $sessionEndDate.ToString('yyyy-MM-dd HH:mm:ss')
        duration_minutes = $durationMinutes
        manual_message_count_user = $ManualMessageCountUser
        manual_message_count_assistant = $ManualMessageCountAssistant
        manual_message_count_total = $manualMessageCountTotal
        checkpoint_file = $checkpointRelativePath
        daily_report_file = $dailyRelativePath
        notes = $Notes
        script_runtime_seconds = $scriptRuntimeSeconds
        bytes_created = $bytesCreated
        kb_created = $kbCreated
        mb_created = $mbCreated
        apply_run_count = $applyRunCount
        dry_run_count = $dryRunCount
    }
    $metricsRow = New-MetricsObject -Values $metricsRowValues

    $indexHeader = @"
# AI_OS Checkpoint Index

| Timestamp | Branch | Status | Total files | Total MB | Duration minutes | Messages total | Checkpoint |
|---|---|---:|---:|---:|---:|---:|---|
"@
    $indexRow = '| {0} | {1} | {2} | {3} | {4} | {5} | {6} | {7} |' -f $timestampStamp, $branch, $gitStatusSummary, $files.Count, $totalMb, $durationMinutes, $manualMessageCountTotal, $checkpointRelativePath

    if ($Mode -eq 'DRY_RUN') {
        Write-Host 'DRY_RUN: no files were created or modified.'
        Write-Host "Repo root: $resolvedRepoRoot"
        Write-Host "Checkpoint file: $checkpointRelativePath"
        Write-Host "Daily report file: $dailyRelativePath"
        Write-Host 'Metrics CSV row:'
        Write-Host (ConvertTo-CsvLine -Row $metricsRow)
        Write-Host 'Checkpoint index row:'
        Write-Host $indexRow
        Write-Host "Git status: $gitStatusSummary"
        exit 0
    }

    New-Item -ItemType Directory -Path $checkpointDir -Force | Out-Null
    New-Item -ItemType Directory -Path $dailyDir -Force | Out-Null

    Write-TextFile -Path $checkpointPath -Content $checkpointContent
    Write-TextFile -Path $dailyReportPath -Content $dailyReportContent

    $afterInventory = Get-RepoInventory -RepoRoot $resolvedRepoRoot
    $bytesCreated = [math]::Max(0, $afterInventory.TotalBytes - $beforeInventory.TotalBytes)
    $kbCreated = [math]::Round($bytesCreated / 1KB, 2)
    $mbCreated = [math]::Round($bytesCreated / 1MB, 2)
    $scriptRuntimeSeconds = [math]::Round(((Get-Date) - $scriptStart).TotalSeconds, 2)
    $applyRunCount = $runCounts.ApplyRunCount + 1
    $dryRunCount = $runCounts.DryRunCount

    $metricsRowValues.script_runtime_seconds = $scriptRuntimeSeconds
    $metricsRowValues.bytes_created = $bytesCreated
    $metricsRowValues.kb_created = $kbCreated
    $metricsRowValues.mb_created = $mbCreated
    $metricsRowValues.apply_run_count = $applyRunCount
    $metricsRowValues.dry_run_count = $dryRunCount
    $metricsRow = New-MetricsObject -Values $metricsRowValues

    $allCsvRows = @($normalizedRows + $metricsRow)
    $allCsvRows | Export-Csv -LiteralPath $metricsCsvPath -NoTypeInformation -Encoding UTF8

    if (Test-Path -LiteralPath $checkpointIndexPath) {
        Add-Content -LiteralPath $checkpointIndexPath -Value $indexRow -Encoding UTF8
    }
    else {
        Write-TextFile -Path $checkpointIndexPath -Content "$indexHeader`r`n$indexRow"
    }

    try {
        Update-DailyStatusSnapshot `
            -Mode $Mode `
            -SnapshotPath $dailyStatusSnapshotPath `
            -CheckpointPath $checkpointPath `
            -DailyReportPath $dailyReportPath `
            -MetricsCsvPath $metricsCsvPath `
            -CheckpointIndexPath $checkpointIndexPath `
            -DateStamp $dateStamp `
            -GitStatusSummary $gitStatusSummary `
            -CheckpointRelativePath $checkpointRelativePath `
            -DailyRelativePath $dailyRelativePath
        $dailyStatusSnapshotUpdated = $true
    }
    catch {
        Write-Warning "Snapshot update skipped: $($_.Exception.Message)"
    }

    Write-Host 'APPLY complete.'
    Write-Host "Checkpoint file: $checkpointRelativePath"
    Write-Host "Daily report file: $dailyRelativePath"
    Write-Host 'Metrics CSV updated: Reports\DAILY_METRICS.csv'
    Write-Host 'Checkpoint index updated: Reports\CHECKPOINT_INDEX.md'
    if ($dailyStatusSnapshotUpdated) {
        Write-Host "Daily status snapshot updated: $dailyStatusSnapshotPath"
    }
}
catch {
    Write-Error $_.Exception.Message
    exit 1
}
