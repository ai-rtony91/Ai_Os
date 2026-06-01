[CmdletBinding()]
param(
    [string]$SourceRepo = "C:\Dev\Ai.Os",
    [string]$BackupRoot = "D:\T9_FOB",
    [ValidateSet("Auto", "Full", "Delta", "ManifestOnly")][string]$BackupMode = "Auto",
    [switch]$Preview,
    [switch]$OutputJson,
    [switch]$AllowDirty,
    [switch]$RetentionPreview
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function ConvertTo-AiOsFullPath {
    param([Parameter(Mandatory = $true)][string]$Path)

    return [System.IO.Path]::GetFullPath($Path).TrimEnd("\")
}

function Format-AiOsBytes {
    param([Parameter(Mandatory = $true)][double]$Bytes)

    $units = @("B", "KB", "MB", "GB", "TB", "PB")
    $value = $Bytes
    $index = 0
    while ($value -ge 1024 -and $index -lt ($units.Count - 1)) {
        $value = $value / 1024
        $index++
    }

    return ("{0:N2} {1}" -f $value, $units[$index])
}

function Get-AiOsDirectorySize {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [string[]]$ExcludeNames = @()
    )

    $total = [double]0
    $files = Get-ChildItem -LiteralPath $Path -Recurse -File -Force -ErrorAction SilentlyContinue
    foreach ($file in $files) {
        $segments = $file.FullName.Split([System.IO.Path]::DirectorySeparatorChar)
        $skip = $false
        foreach ($name in $ExcludeNames) {
            if ($segments -contains $name) {
                $skip = $true
                break
            }
        }
        if (-not $skip) {
            $total += $file.Length
        }
    }

    return $total
}

function Get-AiOsGitStatus {
    param([Parameter(Mandatory = $true)][string]$Path)

    $statusLines = @(git -C $Path status --short --branch)
    if ($LASTEXITCODE -ne 0) {
        throw "Unable to read git status for source repo: $Path"
    }

    return [pscustomobject]@{
        lines = $statusLines
        is_clean = (@($statusLines | Select-Object -Skip 1).Count -eq 0)
    }
}

function Get-AiOsGitInfo {
    param([Parameter(Mandatory = $true)][string]$Path)

    $branch = (git -C $Path branch --show-current).Trim()
    if ($LASTEXITCODE -ne 0) {
        throw "Unable to read git branch for source repo: $Path"
    }

    $commitHash = (git -C $Path rev-parse HEAD).Trim()
    if ($LASTEXITCODE -ne 0) {
        throw "Unable to read git commit for source repo: $Path"
    }

    $commitShort = (git -C $Path rev-parse --short HEAD).Trim()
    if ($LASTEXITCODE -ne 0) {
        throw "Unable to read short git commit for source repo: $Path"
    }

    return [pscustomobject]@{
        branch = $branch
        commit_hash = $commitHash
        commit_short = $commitShort
    }
}

function Get-AiOsProtectedActionLocks {
    param(
        [Parameter(Mandatory = $true)][string]$RepoRoot,
        [Parameter(Mandatory = $true)][string]$BackupReportRoot,
        [Parameter(Mandatory = $true)][string]$BackupLockPath
    )

    $lockRoots = @(
        (Join-Path $RepoRoot "automation\orchestration\locks"),
        $BackupReportRoot
    )
    $protectedPattern = "protected|git|commit|push|merge|stage|staging|reset|clean|branch|\bpr\b|pull request"
    $locks = @()

    foreach ($root in $lockRoots) {
        if (-not (Test-Path -LiteralPath $root -PathType Container)) {
            continue
        }

        $candidates = @(Get-ChildItem -LiteralPath $root -Recurse -File -Force -ErrorAction SilentlyContinue | Where-Object {
            $_.Name -like "*.lock" -or $_.Name -like "*.lock.json"
        })

        foreach ($candidate in $candidates) {
            if ($candidate.FullName -ieq $BackupLockPath) {
                continue
            }

            $nameMatch = $candidate.Name -match $protectedPattern
            $contentMatch = $false
            try {
                $contentMatch = [bool](Select-String -LiteralPath $candidate.FullName -Pattern $protectedPattern -Quiet -ErrorAction Stop)
            } catch {
                $contentMatch = $false
            }

            if ($nameMatch -or $contentMatch) {
                $locks += [pscustomobject]@{
                    path = $candidate.FullName
                    reason = "protected-action-or-git-lock"
                }
            }
        }
    }

    return @($locks)
}

function New-AiOsBackupLock {
    param(
        [Parameter(Mandatory = $true)][string]$BackupReportRoot,
        [Parameter(Mandatory = $true)][string]$BackupLockPath,
        [Parameter(Mandatory = $true)][string]$SourcePath,
        [Parameter(Mandatory = $true)][string]$SnapshotPath
    )

    if (Test-Path -LiteralPath $BackupLockPath) {
        throw "BACKUP_LOCK_EXISTS: $BackupLockPath"
    }

    if (-not (Test-Path -LiteralPath $BackupReportRoot -PathType Container)) {
        New-Item -ItemType Directory -Path $BackupReportRoot | Out-Null
    }

    $lock = [ordered]@{
        schema = "AIOS_BACKUP_LOCK.v1"
        status = "IN_PROGRESS"
        created_at = (Get-Date).ToString("o")
        source_path = $SourcePath
        snapshot_path = $SnapshotPath
        process_id = $PID
    }

    $lock | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $BackupLockPath -Encoding UTF8
}

function Remove-AiOsBackupLock {
    param([Parameter(Mandatory = $true)][string]$BackupLockPath)

    if (Test-Path -LiteralPath $BackupLockPath) {
        Remove-Item -LiteralPath $BackupLockPath -Force
    }
}

function Get-AiOsRobocopyCounts {
    # Robocopy still prints its summary table under /NFL /NDL. Parse the
    # "Files :" row for Copied and Skipped counts. Columns are:
    # Total Copied Skipped Mismatch FAILED Extras
    param([AllowEmptyCollection()][AllowNull()][string[]]$Output = @())

    $counts = [pscustomobject]@{
        files_copied = -1
        files_skipped = -1
    }

    if ($null -eq $Output -or $Output.Count -eq 0) {
        return $counts
    }

    foreach ($line in $Output) {
        if ([string]::IsNullOrWhiteSpace($line)) {
            continue
        }

        if ($line -match '^\s*Files\s*:\s+(\d+)\s+(\d+)\s+(\d+)') {
            $counts.files_copied = [int]$Matches[2]
            $counts.files_skipped = [int]$Matches[3]
            break
        }
    }

    return $counts
}

function Get-AiOsPreviousBackupManifest {
    param(
        [Parameter(Mandatory = $true)][string]$BackupRoot,
        [Parameter(Mandatory = $true)][string]$CurrentSnapshotPath,
        [Nullable[datetime]]$BeforeLocalTime = $null
    )

    if (-not (Test-Path -LiteralPath $BackupRoot -PathType Container)) {
        return $null
    }

    $manifests = @(Get-ChildItem -LiteralPath $BackupRoot -Directory -Filter "AIOS_BACKUP*" -ErrorAction SilentlyContinue |
        Where-Object { $_.FullName -ine $CurrentSnapshotPath } |
        ForEach-Object {
            $candidate = Join-Path $_.FullName "AIOS_BACKUP_MANIFEST.json"
            if (-not (Test-Path -LiteralPath $candidate -PathType Leaf)) { return }
            try {
                $manifest = Get-Content -Raw -LiteralPath $candidate | ConvertFrom-Json
                $status = if ($null -ne $manifest.status) { [string]$manifest.status } else { "" }
                if ($status -ne "SUCCESS") { return }
                $createdAt = if ($null -ne $manifest.created_at) { [datetime]$manifest.created_at } else { $_.LastWriteTime }
                if ($null -ne $BeforeLocalTime -and $createdAt -ge $BeforeLocalTime.Value) { return }
                [pscustomobject]@{
                    path = $candidate
                    manifest = $manifest
                    created_at = $createdAt
                }
            } catch {
                return
            }
        } |
        Sort-Object created_at -Descending)

    if ($manifests.Count -eq 0) { return $null }
    return $manifests[0]
}

function Test-AiOsSuccessfulBackupToday {
    param([Parameter(Mandatory = $true)][string]$BackupRoot)

    if (-not (Test-Path -LiteralPath $BackupRoot -PathType Container)) {
        return $false
    }

    $today = (Get-Date).Date
    $match = @(Get-ChildItem -LiteralPath $BackupRoot -Directory -Filter "AIOS_BACKUP*" -ErrorAction SilentlyContinue |
        ForEach-Object {
            $candidate = Join-Path $_.FullName "AIOS_BACKUP_MANIFEST.json"
            if (-not (Test-Path -LiteralPath $candidate -PathType Leaf)) { return }
            try {
                $manifest = Get-Content -Raw -LiteralPath $candidate | ConvertFrom-Json
                $status = if ($null -ne $manifest.status) { [string]$manifest.status } else { "" }
                if ($status -ne "SUCCESS") { return }
                $createdAt = if ($null -ne $manifest.created_at) { [datetime]$manifest.created_at } else { $_.LastWriteTime }
                if ($createdAt -ge $today) { $_.FullName }
            } catch {
                return
            }
        } | Select-Object -First 1)

    return ($match.Count -gt 0)
}

function Get-AiOsGitDeltaFiles {
    param(
        [Parameter(Mandatory = $true)][string]$RepoRoot,
        [Parameter(Mandatory = $true)][string]$PreviousCommit,
        [Parameter(Mandatory = $true)][string]$CurrentCommit
    )

    $empty = [pscustomobject]@{
        source_range = ""
        changed_files = @()
        deleted_files = @()
        copy_files = @()
    }

    if ([string]::IsNullOrWhiteSpace($PreviousCommit) -or [string]::IsNullOrWhiteSpace($CurrentCommit) -or $PreviousCommit -eq $CurrentCommit) {
        return $empty
    }

    $range = "{0}..{1}" -f $PreviousCommit, $CurrentCommit
    $nameStatusLines = @(git -C $RepoRoot diff --name-status $range)
    if ($LASTEXITCODE -ne 0) {
        return $empty
    }

    $changed = New-Object System.Collections.Generic.List[string]
    $deleted = New-Object System.Collections.Generic.List[string]
    $copy = New-Object System.Collections.Generic.List[string]

    foreach ($line in $nameStatusLines) {
        if ([string]::IsNullOrWhiteSpace($line)) { continue }
        $parts = $line -split "`t"
        $status = [string]$parts[0]
        $relPath = if ($status.StartsWith("R") -and $parts.Count -ge 3) { [string]$parts[2] } elseif ($parts.Count -ge 2) { [string]$parts[1] } else { "" }
        if ([string]::IsNullOrWhiteSpace($relPath)) { continue }
        $relPath = $relPath.Replace("/", "\")

        if ($status -eq "D") {
            $deleted.Add($relPath)
            continue
        }

        $tracked = @(git -C $RepoRoot ls-files -- $relPath)
        if ($LASTEXITCODE -eq 0 -and $tracked.Count -gt 0) {
            $changed.Add($relPath)
            $fullPath = Join-Path $RepoRoot $relPath
            if (Test-Path -LiteralPath $fullPath -PathType Leaf) {
                $copy.Add($relPath)
            }
        }
    }

    return [pscustomobject]@{
        source_range = $range
        changed_files = @($changed)
        deleted_files = @($deleted)
        copy_files = @($copy)
    }
}

function Select-AiOsBackupMode {
    param(
        [Parameter(Mandatory = $true)][string]$RequestedMode,
        [AllowNull()]$PreviousManifest,
        [Parameter(Mandatory = $true)][bool]$HasSuccessfulBackupToday,
        [Parameter(Mandatory = $true)][object]$GitInfo,
        [Parameter(Mandatory = $true)][object]$ProductivityDelta
    )

    if ($RequestedMode -ne "Auto") {
        return [pscustomobject]@{
            mode = $RequestedMode
            reason = "Operator requested $RequestedMode mode."
        }
    }

    if ($null -eq $PreviousManifest) {
        return [pscustomobject]@{ mode = "Full"; reason = "No prior successful backup manifest found." }
    }

    if (-not $HasSuccessfulBackupToday) {
        return [pscustomobject]@{ mode = "Full"; reason = "First successful backup of the local day." }
    }

    if ([string]$ProductivityDelta.previous_backup_commit_hash -eq [string]$GitInfo.commit_hash) {
        return [pscustomobject]@{ mode = "ManifestOnly"; reason = "Current commit already matches the previous backup commit." }
    }

    if ([int]$ProductivityDelta.productivity_delta_files -gt 0 -and [int64]$ProductivityDelta.productivity_delta_bytes -le 52428800) {
        return [pscustomobject]@{ mode = "Delta"; reason = "Productive delta exists and is below the 50 MB delta threshold." }
    }

    return [pscustomobject]@{ mode = "Full"; reason = "Productive delta is large or cannot be safely represented as a small delta." }
}

function Get-AiOsRetentionPreviewCandidates {
    param([Parameter(Mandatory = $true)][string]$BackupRoot)

    if (-not (Test-Path -LiteralPath $BackupRoot -PathType Container)) {
        return @()
    }

    $records = @(Get-ChildItem -LiteralPath $BackupRoot -Directory -Filter "AIOS_BACKUP*" -ErrorAction SilentlyContinue |
        ForEach-Object {
            $manifestPath = Join-Path $_.FullName "AIOS_BACKUP_MANIFEST.json"
            if (-not (Test-Path -LiteralPath $manifestPath -PathType Leaf)) { return }
            try {
                $manifest = Get-Content -Raw -LiteralPath $manifestPath | ConvertFrom-Json
                if ([string]$manifest.status -ne "SUCCESS") { return }
                $mode = if ($manifest.PSObject.Properties.Name -contains "backup_mode") { [string]$manifest.backup_mode } else { "Full" }
                $createdAt = if ($null -ne $manifest.created_at) { [datetime]$manifest.created_at } else { $_.LastWriteTime }
                [pscustomobject]@{
                    backup_id = if ($null -ne $manifest.backup_id) { [string]$manifest.backup_id } else { $_.Name }
                    path = $_.FullName
                    manifest_path = $manifestPath
                    backup_mode = $mode
                    created_at = $createdAt
                    local_date = $createdAt.ToString("yyyy-MM-dd")
                }
            } catch {
                return
            }
        } | Sort-Object created_at -Descending)

    $fullBackups = @($records | Where-Object { $_.backup_mode -eq "Full" })
    $keep = New-Object System.Collections.Generic.HashSet[string]
    @($fullBackups | Select-Object -First 3) | ForEach-Object { [void]$keep.Add($_.backup_id) }
    $fullBackups | Group-Object local_date | ForEach-Object {
        $firstOfDay = @($_.Group | Sort-Object created_at | Select-Object -First 1)
        if ($firstOfDay.Count -gt 0) { [void]$keep.Add($firstOfDay[0].backup_id) }
    }

    return @($fullBackups | Where-Object { -not $keep.Contains($_.backup_id) } | ForEach-Object {
        [pscustomobject]@{
            backup_id = $_.backup_id
            path = $_.path
            reason = "Older duplicate full snapshot; retention preview only."
        }
    })
}

function Copy-AiOsDeltaFiles {
    param(
        [Parameter(Mandatory = $true)][string]$RepoRoot,
        [Parameter(Mandatory = $true)][string]$DestinationRoot,
        [Parameter(Mandatory = $true)][string[]]$RelativePaths
    )

    foreach ($relPath in $RelativePaths) {
        $source = Join-Path $RepoRoot $relPath
        if (-not (Test-Path -LiteralPath $source -PathType Leaf)) { continue }
        $destination = Join-Path $DestinationRoot $relPath
        $destinationParent = Split-Path -Parent $destination
        if (-not (Test-Path -LiteralPath $destinationParent -PathType Container)) {
            New-Item -ItemType Directory -Path $destinationParent -Force | Out-Null
        }
        Copy-Item -LiteralPath $source -Destination $destination -Force
    }
}

function Get-AiOsGitDeltaStats {
    param(
        [Parameter(Mandatory = $true)][string]$RepoRoot,
        [Parameter(Mandatory = $true)][string]$PreviousCommit,
        [Parameter(Mandatory = $true)][string]$CurrentCommit
    )

    $empty = [pscustomobject]@{
        files = 0
        new_files = 0
        changed_files = 0
        deleted_files = 0
        bytes = 0L
        commits = 0
        pr_merges = 0
        pr_merge_subjects = @()
    }
    if ([string]::IsNullOrWhiteSpace($PreviousCommit) -or [string]::IsNullOrWhiteSpace($CurrentCommit) -or $PreviousCommit -eq $CurrentCommit) {
        return $empty
    }

    $range = "{0}..{1}" -f $PreviousCommit, $CurrentCommit
    $commitCountText = (git -C $RepoRoot rev-list --count $range).Trim()
    if ($LASTEXITCODE -ne 0) { return $empty }

    $mergeSubjects = @(git -C $RepoRoot log --merges --grep "Merge pull request" --format=%s $range)
    if ($LASTEXITCODE -ne 0) { $mergeSubjects = @() }

    $nameStatusLines = @(git -C $RepoRoot diff --name-status $range)
    if ($LASTEXITCODE -ne 0) { return $empty }

    $newFiles = 0
    $changedFiles = 0
    $deletedFiles = 0
    $deltaBytes = [int64]0
    foreach ($line in $nameStatusLines) {
        if ([string]::IsNullOrWhiteSpace($line)) { continue }
        $parts = $line -split "`t"
        $status = [string]$parts[0]
        $currentRelPath = if ($status.StartsWith("R") -and $parts.Count -ge 3) { [string]$parts[2] } elseif ($parts.Count -ge 2) { [string]$parts[1] } else { "" }

        if ($status -eq "D") {
            $deletedFiles++
            continue
        } elseif ($status -eq "A") {
            $newFiles++
        } else {
            $changedFiles++
        }

        if (-not [string]::IsNullOrWhiteSpace($currentRelPath)) {
            $fullPath = Join-Path $RepoRoot $currentRelPath
            if (Test-Path -LiteralPath $fullPath -PathType Leaf) {
                $deltaBytes += (Get-Item -LiteralPath $fullPath).Length
            }
        }
    }

    return [pscustomobject]@{
        files = @($nameStatusLines).Count
        new_files = $newFiles
        changed_files = $changedFiles
        deleted_files = $deletedFiles
        bytes = $deltaBytes
        commits = [int]$commitCountText
        pr_merges = @($mergeSubjects).Count
        pr_merge_subjects = @($mergeSubjects)
    }
}

function Get-AiOsBackupProductivityDelta {
    param(
        [Parameter(Mandatory = $true)][string]$RepoRoot,
        [Parameter(Mandatory = $true)][string]$BackupRoot,
        [Parameter(Mandatory = $true)][string]$CurrentSnapshotPath,
        [Parameter(Mandatory = $true)][object]$GitInfo,
        [Parameter(Mandatory = $true)][string[]]$ExcludedDirs
    )

    $previous = Get-AiOsPreviousBackupManifest -BackupRoot $BackupRoot -CurrentSnapshotPath $CurrentSnapshotPath
    $todayBase = Get-AiOsPreviousBackupManifest -BackupRoot $BackupRoot -CurrentSnapshotPath $CurrentSnapshotPath -BeforeLocalTime (Get-Date).Date
    $previousCommit = if ($null -ne $previous -and $null -ne $previous.manifest.commit_hash) { [string]$previous.manifest.commit_hash } else { "" }
    $todayCommit = if ($null -ne $todayBase -and $null -ne $todayBase.manifest.commit_hash) { [string]$todayBase.manifest.commit_hash } else { "" }

    $delta = Get-AiOsGitDeltaStats -RepoRoot $RepoRoot -PreviousCommit $previousCommit -CurrentCommit ([string]$GitInfo.commit_hash)
    $todayDelta = if ([string]::IsNullOrWhiteSpace($todayCommit)) { $null } else { Get-AiOsGitDeltaStats -RepoRoot $RepoRoot -PreviousCommit $todayCommit -CurrentCommit ([string]$GitInfo.commit_hash) }
    $signal = Get-AiOsBackupProductivitySignal -HasPreviousBackup ($null -ne $previous) `
        -Commits ([int]$delta.commits) `
        -Files ([int]$delta.files) `
        -Bytes ([int64]$delta.bytes) `
        -PrMerges ([int]$delta.pr_merges)
    $runtimeNames = @("relay\logs", "relay\running", "relay\done", "relay\error", "telemetry", "Reports")
    $runtimeExcluded = @($runtimeNames | Where-Object {
        $runtimeName = $_
        @($ExcludedDirs | Where-Object { $_ -like "*$runtimeName*" }).Count -gt 0
    }).Count -eq $runtimeNames.Count

    return [pscustomobject]@{
        previous_backup_manifest_path = if ($null -ne $previous) { [string]$previous.path } else { "" }
        previous_backup_id = if ($null -ne $previous -and $null -ne $previous.manifest.backup_id) { [string]$previous.manifest.backup_id } else { "" }
        previous_backup_commit_hash = $previousCommit
        productivity_delta_files = [int]$delta.files
        productivity_delta_new_files = [int]$delta.new_files
        productivity_delta_changed_files = [int]$delta.changed_files
        productivity_delta_deleted_files = [int]$delta.deleted_files
        productivity_delta_bytes = [int64]$delta.bytes
        productivity_delta_human = Format-AiOsBytes -Bytes ([double]$delta.bytes)
        productivity_delta_commits = [int]$delta.commits
        productivity_delta_pr_merges = [int]$delta.pr_merges
        productivity_delta_pr_merge_subjects = @($delta.pr_merge_subjects)
        productivity_delta_today_files = if ($null -eq $todayDelta) { "UNKNOWN" } else { [int]$todayDelta.files }
        productivity_delta_today_bytes = if ($null -eq $todayDelta) { "UNKNOWN" } else { [int64]$todayDelta.bytes }
        productivity_delta_today_human = if ($null -eq $todayDelta) { "UNKNOWN" } else { Format-AiOsBytes -Bytes ([double]$todayDelta.bytes) }
        runtime_files_excluded = [bool]$runtimeExcluded
        runtime_exclusion_status = if ($runtimeExcluded) { "FULL" } else { "PARTIAL" }
        productivity_delta_signal_score = $signal.score
        productivity_delta_progress_bar = $signal.bar
        productivity_delta_progress_label = $signal.label
        productivity_delta_summary = "Productivity delta: $($delta.files) files / $(Format-AiOsBytes -Bytes ([double]$delta.bytes)) / $($delta.commits) commits since last backup."
    }
}

function Get-AiOsBackupProductivitySignal {
    param(
        [Parameter(Mandatory = $true)][bool]$HasPreviousBackup,
        [Parameter(Mandatory = $true)][int]$Commits,
        [Parameter(Mandatory = $true)][int]$Files,
        [Parameter(Mandatory = $true)][int64]$Bytes,
        [Parameter(Mandatory = $true)][int]$PrMerges
    )

    if (-not $HasPreviousBackup) {
        return [pscustomobject]@{
            score = "UNKNOWN"
            bar = "UNKNOWN"
            label = "UNKNOWN"
        }
    }

    $signals = 0
    if ($Commits -gt 0) { $signals++ }
    if ($Files -gt 0) { $signals++ }
    if ($Bytes -gt 0) { $signals++ }
    if ($PrMerges -gt 0) { $signals++ }

    $score = [Math]::Min(100, $signals * 25)
    $filled = [Math]::Min(10, [int]($score / 10))
    $empty = 10 - $filled
    $bar = ("█" * $filled) + ("░" * $empty)

    return [pscustomobject]@{
        score = $score
        bar = $bar
        label = "$score%"
    }
}

function Add-AiOsProductivityFields {
    param(
        [Parameter(Mandatory = $true)][object]$Target,
        [Parameter(Mandatory = $true)][object]$ProductivityDelta
    )

    foreach ($property in $ProductivityDelta.PSObject.Properties) {
        $Target | Add-Member -NotePropertyName $property.Name -NotePropertyValue $property.Value -Force
    }
}

function Write-AiOsBackupProductivityOutput {
    param(
        [Parameter(Mandatory = $true)][object]$ProductivityDelta,
        [Parameter(Mandatory = $true)][string]$CopiedHuman,
        [int]$ChangedCopied = 0,
        [int]$DeletedRecorded = 0,
        [bool]$RestoreRequiresFullBackup = $false,
        [int]$RetentionCandidateCount = 0
    )

    if ([string]$ProductivityDelta.productivity_delta_progress_label -eq "UNKNOWN") {
        Write-Host "Backup productivity bar: UNKNOWN"
    } else {
        Write-Host "Backup productivity bar: $($ProductivityDelta.productivity_delta_progress_bar) $($ProductivityDelta.productivity_delta_progress_label)"
    }
    Write-Host "Backup total copied: $CopiedHuman"
    Write-Host $ProductivityDelta.productivity_delta_summary
    Write-Host "Changed files copied: $ChangedCopied"
    Write-Host "Deleted files recorded: $DeletedRecorded"
    Write-Host "Restore requires full backup: $(if ($RestoreRequiresFullBackup) { 'YES' } else { 'NO' })"
    if ($RetentionPreview) {
        Write-Host "Retention preview candidates: $RetentionCandidateCount"
    }
    Write-Host "PR merges included: $($ProductivityDelta.productivity_delta_pr_merges)"
    Write-Host "Runtime exclusion status: $($ProductivityDelta.runtime_exclusion_status)"
}

function New-AiOsBackupResult {
    param(
        [Parameter(Mandatory = $true)][string]$Status,
        [Parameter(Mandatory = $true)][string]$Message,
        [int]$RobocopyExitCode = -1,
        [int]$ExitCode = 0
    )

    return [pscustomobject]@{
        schema = "AIOS_T9_SNAPSHOT_BACKUP.v1"
        mode = if ($Preview) { "PREVIEW" } else { "APPLY" }
        status = $Status
        message = $Message
        source_repo = $normalizedSource
        backup_root = $normalizedBackupRoot
        snapshot_name = $snapshotName
        snapshot_path = $snapshotPath
        backup_mode = $selectedBackupMode
        requested_backup_mode = $BackupMode
        selected_backup_mode_reason = $selectedBackupModeReason
        excluded_paths = $excludedDirs
        robocopy_exit_code = $RobocopyExitCode
        exit_code = $ExitCode
        mutation_scope = if ($Preview) { "NONE" } elseif ($selectedBackupMode -eq "ManifestOnly") { "BACKUP_MANIFEST_ONLY" } else { "BACKUP_SNAPSHOT_ONLY" }
        active_repo_mutation = "NO"
        scheduler_behavior = "NO"
        runtime_mutation = if ($Preview) { "NO" } else { "BACKUP_DESTINATION_ONLY" }
        allow_dirty = [bool]$AllowDirty
        backup_lock_path = $backupLockPath
        robocopy_log_path = $robocopyLogPath
        manifest_path = $manifestPath
        base_backup_id = $baseBackupId
        base_backup_commit_hash = $baseBackupCommitHash
        changed_files = @($changedFiles)
        deleted_files = @($deletedFiles)
        file_count_copied = [int]$fileCountCopied
        delta_source_range = $deltaSourceRange
        restore_requires_full_backup = [bool]$restoreRequiresFullBackup
        retention_class = $retentionClass
        retention_preview_candidates = @($retentionPreviewCandidates)
        generated_at = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    }
}

function Set-AiOsBackupWindow {
    # Shrink the console to just fit the banner/text, matching the other worker windows.
    try {
        $rawUi = $Host.UI.RawUI
        $targetWidth = 92
        $targetHeight = 34

        $buffer = $rawUi.BufferSize
        $buffer.Width = $targetWidth
        $buffer.Height = [Math]::Max(300, $buffer.Height)
        $rawUi.BufferSize = $buffer

        $window = $rawUi.WindowSize
        $window.Width = [Math]::Min($targetWidth, $rawUi.MaxWindowSize.Width)
        $window.Height = [Math]::Min($targetHeight, $rawUi.MaxWindowSize.Height)
        $rawUi.WindowSize = $window
    } catch {
        # Non-interactive hosts may reject sizing; the backup still runs.
    }
}

function Write-AiOsBackupManifest {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$Status,
        [Parameter(Mandatory = $true)][int]$RobocopyExitCode,
        [Parameter(Mandatory = $true)][object]$GitInfo,
        [Parameter(Mandatory = $true)][object]$GitStatus,
        [AllowEmptyCollection()][AllowNull()][object[]]$ProtectedLocks = @(),
        [Parameter(Mandatory = $true)][object]$ProductivityDelta,
        [int64]$CopiedBytes = 0,
        [string]$CopiedHuman = "0.00 B",
        [string[]]$ChangedFiles = @(),
        [string[]]$DeletedFiles = @(),
        [int]$FileCountCopied = 0,
        [string]$DeltaSourceRange = "",
        [string]$BaseBackupId = "",
        [string]$BaseBackupCommitHash = "",
        [bool]$RestoreRequiresFullBackup = $false,
        [string]$RetentionClass = "",
        [object[]]$RetentionPreviewCandidates = @(),
        [Parameter(Mandatory = $true)][string]$Message
    )

    $protectedLocksForManifest = if ($null -eq $ProtectedLocks) { @() } else { @($ProtectedLocks) }

    $manifest = [ordered]@{
        schema = "AIOS_T9_SNAPSHOT_BACKUP_MANIFEST.v1"
        backup_id = $snapshotName
        created_at = (Get-Date).ToString("o")
        source_path = $normalizedSource
        destination_path = $snapshotPath
        branch = $GitInfo.branch
        commit_hash = $GitInfo.commit_hash
        commit_short = $GitInfo.commit_short
        git_status = @($GitStatus.lines)
        git_status_clean = [bool]$GitStatus.is_clean
        allow_dirty = [bool]$AllowDirty
        robocopy_exit_code = $RobocopyExitCode
        status = $Status
        message = $Message
        backup_mode = $selectedBackupMode
        requested_backup_mode = $BackupMode
        selected_backup_mode_reason = $selectedBackupModeReason
        base_backup_id = $BaseBackupId
        base_backup_commit_hash = $BaseBackupCommitHash
        changed_files = @($ChangedFiles)
        deleted_files = @($DeletedFiles)
        file_count_copied = $FileCountCopied
        delta_source_range = $DeltaSourceRange
        restore_requires_full_backup = [bool]$RestoreRequiresFullBackup
        retention_class = $RetentionClass
        retention_preview_candidates = @($RetentionPreviewCandidates)
        excluded_dirs = @($excludedDirs)
        robocopy_log_path = $robocopyLogPath
        backup_lock_path = $backupLockPath
        protected_action_locks_found = $protectedLocksForManifest
        copied_bytes = $CopiedBytes
        copied_human = $CopiedHuman
        operator = "Anthony"
        script = $PSCommandPath
    }
    foreach ($property in $ProductivityDelta.PSObject.Properties) {
        $manifest[$property.Name] = $property.Value
    }

    $manifest | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $Path -Encoding UTF8
}

$expectedSource = "C:\Dev\Ai.Os"
$expectedBackupRoot = "D:\T9_FOB"
$normalizedSource = ConvertTo-AiOsFullPath -Path $SourceRepo
$normalizedBackupRoot = ConvertTo-AiOsFullPath -Path $BackupRoot
$timestamp = Get-Date -Format "yyyy-MM-dd_HHmmss"
$snapshotName = "AIOS_BACKUP_$timestamp"
$snapshotPath = Join-Path $normalizedBackupRoot $snapshotName
$backupReportRoot = Join-Path $normalizedSource "telemetry\backup_reports"
$backupLockPath = Join-Path $backupReportRoot "AIOS_BACKUP_IN_PROGRESS.lock"
$robocopyLogPath = Join-Path $snapshotPath "AIOS_BACKUP_ROBOCOPY.log"
$manifestPath = Join-Path $snapshotPath "AIOS_BACKUP_MANIFEST.json"
$excludedDirs = @(
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".codex",
    (Join-Path $normalizedSource ".git\logs")
)
$selectedBackupMode = $BackupMode
$selectedBackupModeReason = "Mode has not been selected yet."
$baseBackupId = ""
$baseBackupCommitHash = ""
$changedFiles = @()
$deletedFiles = @()
$fileCountCopied = 0
$deltaSourceRange = ""
$restoreRequiresFullBackup = $false
$retentionClass = ""
$retentionPreviewCandidates = @()

try {
    if (-not $OutputJson) {
        Set-AiOsBackupWindow
        $identityScript = Join-Path $PSScriptRoot "..\..\automation\window_identity\Set-AiOsWindowIdentity.ps1"
        if (Test-Path -LiteralPath $identityScript) {
            & $identityScript -Marker "T9 BACKUP"
        }
    }

    if ($normalizedSource -ne $expectedSource) {
        throw "Source repo must be exactly $expectedSource."
    }

    if ($normalizedBackupRoot -ne $expectedBackupRoot) {
        throw "Backup root must be exactly $expectedBackupRoot."
    }

    if (-not (Test-Path -LiteralPath $normalizedSource -PathType Container)) {
        throw "Source repo does not exist: $normalizedSource"
    }

    if (-not (Test-Path -LiteralPath $normalizedBackupRoot -PathType Container)) {
        throw "Backup root does not exist: $normalizedBackupRoot"
    }

    $volume = Get-Volume -DriveLetter D
    if ($volume.FileSystemLabel -ne "T9_FOB") {
        throw "Drive D: label must be T9_FOB. Actual label: $($volume.FileSystemLabel)"
    }

    if (Test-Path -LiteralPath $snapshotPath) {
        throw "Snapshot destination already exists: $snapshotPath"
    }

    if (Test-Path -LiteralPath $backupLockPath) {
        throw "BACKUP_LOCK_EXISTS: $backupLockPath"
    }

    $gitStatus = Get-AiOsGitStatus -Path $normalizedSource
    $gitInfo = Get-AiOsGitInfo -Path $normalizedSource
    $productivityDelta = Get-AiOsBackupProductivityDelta -RepoRoot $normalizedSource -BackupRoot $normalizedBackupRoot -CurrentSnapshotPath $snapshotPath -GitInfo $gitInfo -ExcludedDirs $excludedDirs
    $previousManifest = Get-AiOsPreviousBackupManifest -BackupRoot $normalizedBackupRoot -CurrentSnapshotPath $snapshotPath
    $hasSuccessfulBackupToday = Test-AiOsSuccessfulBackupToday -BackupRoot $normalizedBackupRoot
    if ($null -ne $previousManifest) {
        $baseBackupId = if ($null -ne $previousManifest.manifest.backup_id) { [string]$previousManifest.manifest.backup_id } else { "" }
        $baseBackupCommitHash = if ($null -ne $previousManifest.manifest.commit_hash) { [string]$previousManifest.manifest.commit_hash } else { "" }
    }
    $deltaInfo = Get-AiOsGitDeltaFiles -RepoRoot $normalizedSource -PreviousCommit $baseBackupCommitHash -CurrentCommit ([string]$gitInfo.commit_hash)
    $changedFiles = @($deltaInfo.copy_files)
    $deletedFiles = @($deltaInfo.deleted_files)
    $deltaSourceRange = [string]$deltaInfo.source_range
    $selection = Select-AiOsBackupMode -RequestedMode $BackupMode -PreviousManifest $previousManifest -HasSuccessfulBackupToday $hasSuccessfulBackupToday -GitInfo $gitInfo -ProductivityDelta $productivityDelta
    $selectedBackupMode = [string]$selection.mode
    $selectedBackupModeReason = [string]$selection.reason
    $restoreRequiresFullBackup = ($selectedBackupMode -eq "Delta")
    $retentionClass = if ($selectedBackupMode -eq "Full") { "FULL_SNAPSHOT" } elseif ($selectedBackupMode -eq "Delta") { "DELTA_SNAPSHOT" } else { "MANIFEST_ONLY" }
    $retentionPreviewCandidates = if ($RetentionPreview) { @(Get-AiOsRetentionPreviewCandidates -BackupRoot $normalizedBackupRoot) } else { @() }

    if ($selectedBackupMode -eq "Full") {
        $snapshotName = "AIOS_BACKUP_$timestamp"
    } else {
        $snapshotName = "AIOS_BACKUP_{0}_{1}" -f $timestamp, $selectedBackupMode.ToUpperInvariant()
    }
    $snapshotPath = Join-Path $normalizedBackupRoot $snapshotName
    $robocopyLogPath = Join-Path $snapshotPath "AIOS_BACKUP_ROBOCOPY.log"
    $manifestPath = Join-Path $snapshotPath "AIOS_BACKUP_MANIFEST.json"

    if ($selectedBackupMode -eq "Delta" -and [string]::IsNullOrWhiteSpace($baseBackupCommitHash)) {
        throw "Delta mode requires a prior successful backup manifest with commit_hash."
    }

    $protectedLocks = @(Get-AiOsProtectedActionLocks -RepoRoot $normalizedSource -BackupReportRoot $backupReportRoot -BackupLockPath $backupLockPath)
    if ($protectedLocks.Count -gt 0) {
        throw "PROTECTED_ACTION_LOCK_EXISTS: $($protectedLocks.path -join ', ')"
    }

    if (-not $Preview -and -not $AllowDirty -and -not $gitStatus.is_clean) {
        throw "DIRTY_REPO: Backup requires clean git status. Re-run with -AllowDirty only after explicit approval. Status: $($gitStatus.lines -join ' | ')"
    }

    $plannedCommand = if ($selectedBackupMode -eq "ManifestOnly") {
        @("Write manifest only to `"$manifestPath`"")
    } elseif ($selectedBackupMode -eq "Delta") {
        @("Copy tracked changed files only to `"$snapshotPath`"", "range=$deltaSourceRange", "files=$($changedFiles.Count)")
    } else {
        @(
            "robocopy",
            "`"$normalizedSource`"",
            "`"$snapshotPath`"",
            "/E",
            "/XJ",
            "/R:1",
            "/W:1",
            "/NFL",
            "/NDL",
            "/NP",
            "/LOG:`"$robocopyLogPath`"",
            "/TEE",
            "/XD"
        ) + ($excludedDirs | ForEach-Object { "`"$_`"" })
    }

    $excludeNames = @("node_modules", "__pycache__", ".pytest_cache", ".codex")

    if ($Preview) {
        $sourceBytes = Get-AiOsDirectorySize -Path $normalizedSource -ExcludeNames $excludeNames
        $destBytes = Get-AiOsDirectorySize -Path $normalizedBackupRoot

        $result = New-AiOsBackupResult -Status "PREVIEW" -Message "Preview only. No folder was created, no lock was created, and robocopy was not run."
        $result | Add-Member -NotePropertyName planned_command -NotePropertyValue ($plannedCommand -join " ")
        $result | Add-Member -NotePropertyName source_bytes -NotePropertyValue ([long]$sourceBytes)
        $result | Add-Member -NotePropertyName dest_bytes -NotePropertyValue ([long]$destBytes)
        $result | Add-Member -NotePropertyName copied_bytes -NotePropertyValue 0
        $result | Add-Member -NotePropertyName copied_human -NotePropertyValue "0.00 B"
        $result | Add-Member -NotePropertyName source_human -NotePropertyValue (Format-AiOsBytes -Bytes $sourceBytes)
        $result | Add-Member -NotePropertyName dest_human -NotePropertyValue (Format-AiOsBytes -Bytes $destBytes)
        $result | Add-Member -NotePropertyName git_status_clean -NotePropertyValue ([bool]$gitStatus.is_clean)
        $result | Add-Member -NotePropertyName protected_action_lock_count -NotePropertyValue ([int]$protectedLocks.Count)
        $result | Add-Member -NotePropertyName retention_preview_status -NotePropertyValue $(if ($RetentionPreview) { "RETENTION_PREVIEW_ONLY" } else { "NOT_REQUESTED" })
        Add-AiOsProductivityFields -Target $result -ProductivityDelta $productivityDelta
        if ($OutputJson) {
            $result | ConvertTo-Json -Depth 6
        }
        else {
            Write-Host "AI_OS T9 Snapshot Backup Preview"
            Write-Host "Backup mode: $selectedBackupMode"
            Write-Host "Selected reason: $selectedBackupModeReason"
            if ($RetentionPreview) { Write-Host "RETENTION_PREVIEW_ONLY" }
            Write-Host "Source: $normalizedSource"
            Write-Host "Backup root: $normalizedBackupRoot"
            Write-Host "Snapshot path: $snapshotPath"
            Write-Host "Backup lock path: $backupLockPath"
            Write-Host "Robocopy log path: $robocopyLogPath"
            Write-Host "Manifest path: $manifestPath"
            Write-Host "Git status clean: $($gitStatus.is_clean)"
            Write-Host "Protected-action locks found: $($protectedLocks.Count)"
            Write-Host "Excluded paths:"
            $excludedDirs | ForEach-Object { Write-Host "  - $_" }
            Write-Host ""
            Write-Host "Source data measured:        $(Format-AiOsBytes -Bytes $sourceBytes)"
            Write-Host "Current backup size (T9):    $(Format-AiOsBytes -Bytes $destBytes)"
            Write-Host "Copied this run:             0.00 B (preview - no copy run)"
            Write-Host "Skipped (already current):   pending (preview - robocopy not run)"
            Write-Host "Produced this backup session: 0.00 B (preview - no copy run)"
            Write-Host ""
            Write-AiOsBackupProductivityOutput -ProductivityDelta $productivityDelta -CopiedHuman "0.00 B" -ChangedCopied $changedFiles.Count -DeletedRecorded $deletedFiles.Count -RestoreRequiresFullBackup $restoreRequiresFullBackup -RetentionCandidateCount $retentionPreviewCandidates.Count
            if ($productivityDelta.productivity_delta_today_files -eq "UNKNOWN") {
                Write-Host "Productivity delta today: UNKNOWN"
            } else {
                Write-Host "Productivity delta today: $($productivityDelta.productivity_delta_today_files) files / $($productivityDelta.productivity_delta_today_human)"
            }
            Write-Host ""
            Write-Host "Planned command:"
            Write-Host ($plannedCommand -join " ")
            Write-Host "No folder was created. No lock was created. Robocopy was not run."
        }
        exit 0
    }

    if ($selectedBackupMode -eq "ManifestOnly") {
        $lockCreated = $false
        try {
            New-AiOsBackupLock -BackupReportRoot $backupReportRoot -BackupLockPath $backupLockPath -SourcePath $normalizedSource -SnapshotPath $snapshotPath
            $lockCreated = $true
            New-Item -ItemType Directory -Path $snapshotPath | Out-Null
            $sourceBytes = Get-AiOsDirectorySize -Path $normalizedSource -ExcludeNames $excludeNames
            $destBytes = Get-AiOsDirectorySize -Path $normalizedBackupRoot
            $copiedHuman = "0.00 B"
            $manifestMessage = "Manifest-only checkpoint created. No files were copied."

            Write-AiOsBackupManifest -Path $manifestPath -Status "SUCCESS" -RobocopyExitCode 0 -GitInfo $gitInfo -GitStatus $gitStatus -ProtectedLocks $protectedLocks -ProductivityDelta $productivityDelta -CopiedBytes 0 -CopiedHuman $copiedHuman -ChangedFiles $changedFiles -DeletedFiles $deletedFiles -FileCountCopied 0 -DeltaSourceRange $deltaSourceRange -BaseBackupId $baseBackupId -BaseBackupCommitHash $baseBackupCommitHash -RestoreRequiresFullBackup $false -RetentionClass $retentionClass -RetentionPreviewCandidates $retentionPreviewCandidates -Message $manifestMessage

            $result = New-AiOsBackupResult -Status "SUCCESS" -Message $manifestMessage -RobocopyExitCode 0 -ExitCode 0
            $result | Add-Member -NotePropertyName source_bytes -NotePropertyValue ([long]$sourceBytes)
            $result | Add-Member -NotePropertyName dest_bytes -NotePropertyValue ([long]$destBytes)
            $result | Add-Member -NotePropertyName copied_bytes -NotePropertyValue 0
            $result | Add-Member -NotePropertyName files_copied -NotePropertyValue 0
            $result | Add-Member -NotePropertyName files_skipped -NotePropertyValue -1
            $result | Add-Member -NotePropertyName source_human -NotePropertyValue (Format-AiOsBytes -Bytes $sourceBytes)
            $result | Add-Member -NotePropertyName dest_human -NotePropertyValue (Format-AiOsBytes -Bytes $destBytes)
            $result | Add-Member -NotePropertyName copied_human -NotePropertyValue $copiedHuman
            Add-AiOsProductivityFields -Target $result -ProductivityDelta $productivityDelta

            if ($OutputJson) {
                $result | ConvertTo-Json -Depth 6
            } else {
                Write-Host "AI_OS T9 Snapshot Backup"
                Write-Host "Status: SUCCESS"
                Write-Host "Backup mode: $selectedBackupMode"
                Write-Host "Selected reason: $selectedBackupModeReason"
                Write-Host "Manifest path: $manifestPath"
                Write-AiOsBackupProductivityOutput -ProductivityDelta $productivityDelta -CopiedHuman $copiedHuman -ChangedCopied 0 -DeletedRecorded $deletedFiles.Count -RestoreRequiresFullBackup $false -RetentionCandidateCount $retentionPreviewCandidates.Count
                Write-Host "Active repo mutation: NO"
                Write-Host "Scheduler behavior: NO"
                Write-Host "Runtime mutation: BACKUP_DESTINATION_ONLY"
            }
            exit 0
        }
        finally {
            if ($lockCreated) {
                Remove-AiOsBackupLock -BackupLockPath $backupLockPath
            }
        }
    }

    if ($selectedBackupMode -eq "Delta") {
        $lockCreated = $false
        try {
            New-AiOsBackupLock -BackupReportRoot $backupReportRoot -BackupLockPath $backupLockPath -SourcePath $normalizedSource -SnapshotPath $snapshotPath
            $lockCreated = $true
            $sourceBytes = Get-AiOsDirectorySize -Path $normalizedSource -ExcludeNames $excludeNames
            $destBytesBefore = Get-AiOsDirectorySize -Path $normalizedBackupRoot
            New-Item -ItemType Directory -Path $snapshotPath | Out-Null
            Copy-AiOsDeltaFiles -RepoRoot $normalizedSource -DestinationRoot $snapshotPath -RelativePaths $changedFiles
            $copiedBytes = Get-AiOsDirectorySize -Path $snapshotPath
            $destBytesAfter = $destBytesBefore + $copiedBytes
            $fileCountCopied = $changedFiles.Count
            $copiedHuman = Format-AiOsBytes -Bytes $copiedBytes
            $manifestMessage = "Delta snapshot created from tracked changed files only."

            Write-AiOsBackupManifest -Path $manifestPath -Status "SUCCESS" -RobocopyExitCode 0 -GitInfo $gitInfo -GitStatus $gitStatus -ProtectedLocks $protectedLocks -ProductivityDelta $productivityDelta -CopiedBytes ([long]$copiedBytes) -CopiedHuman $copiedHuman -ChangedFiles $changedFiles -DeletedFiles $deletedFiles -FileCountCopied $fileCountCopied -DeltaSourceRange $deltaSourceRange -BaseBackupId $baseBackupId -BaseBackupCommitHash $baseBackupCommitHash -RestoreRequiresFullBackup $true -RetentionClass $retentionClass -RetentionPreviewCandidates $retentionPreviewCandidates -Message $manifestMessage

            $result = New-AiOsBackupResult -Status "SUCCESS" -Message $manifestMessage -RobocopyExitCode 0 -ExitCode 0
            $result | Add-Member -NotePropertyName source_bytes -NotePropertyValue ([long]$sourceBytes)
            $result | Add-Member -NotePropertyName dest_bytes -NotePropertyValue ([long]$destBytesAfter)
            $result | Add-Member -NotePropertyName copied_bytes -NotePropertyValue ([long]$copiedBytes)
            $result | Add-Member -NotePropertyName files_copied -NotePropertyValue $fileCountCopied
            $result | Add-Member -NotePropertyName files_skipped -NotePropertyValue -1
            $result | Add-Member -NotePropertyName source_human -NotePropertyValue (Format-AiOsBytes -Bytes $sourceBytes)
            $result | Add-Member -NotePropertyName dest_human -NotePropertyValue (Format-AiOsBytes -Bytes $destBytesAfter)
            $result | Add-Member -NotePropertyName copied_human -NotePropertyValue $copiedHuman
            Add-AiOsProductivityFields -Target $result -ProductivityDelta $productivityDelta

            if ($OutputJson) {
                $result | ConvertTo-Json -Depth 6
            } else {
                Write-Host "AI_OS T9 Snapshot Backup"
                Write-Host "Status: SUCCESS"
                Write-Host "Backup mode: $selectedBackupMode"
                Write-Host "Selected reason: $selectedBackupModeReason"
                Write-Host "Snapshot path: $snapshotPath"
                Write-Host "Manifest path: $manifestPath"
                Write-AiOsBackupProductivityOutput -ProductivityDelta $productivityDelta -CopiedHuman $copiedHuman -ChangedCopied $changedFiles.Count -DeletedRecorded $deletedFiles.Count -RestoreRequiresFullBackup $true -RetentionCandidateCount $retentionPreviewCandidates.Count
                Write-Host "Active repo mutation: NO"
                Write-Host "Scheduler behavior: NO"
                Write-Host "Runtime mutation: BACKUP_DESTINATION_ONLY"
            }
            exit 0
        }
        finally {
            if ($lockCreated) {
                Remove-AiOsBackupLock -BackupLockPath $backupLockPath
            }
        }
    }

    $lockCreated = $false
    try {
        New-AiOsBackupLock -BackupReportRoot $backupReportRoot -BackupLockPath $backupLockPath -SourcePath $normalizedSource -SnapshotPath $snapshotPath
        $lockCreated = $true

        # Measured before the snapshot is created so it reflects existing T9 backups.
        $sourceBytes = Get-AiOsDirectorySize -Path $normalizedSource -ExcludeNames $excludeNames
        $destBytesBefore = Get-AiOsDirectorySize -Path $normalizedBackupRoot

        New-Item -ItemType Directory -Path $snapshotPath | Out-Null

        Write-Host ""
        Write-Host "Source data measured:        $(Format-AiOsBytes -Bytes $sourceBytes)"
        Write-Host "Copying to: $snapshotPath"
        Write-Host ""

        $robocopyArgs = @(
            $normalizedSource,
            $snapshotPath,
            "/E",
            "/XJ",
            "/R:1",
            "/W:1",
            "/NFL",
            "/NDL",
            "/NP",
            "/LOG:$robocopyLogPath",
            "/TEE",
            "/XD"
        ) + $excludedDirs

        $robocopyOutput = @(& robocopy @robocopyArgs 2>&1)
        $robocopyExitCode = $LASTEXITCODE
        $robocopyOutput | ForEach-Object { Write-Host $_ }

        $robocopyLines = @($robocopyOutput | ForEach-Object {
            if ($null -eq $_) {
                ""
            } else {
                "$_"
            }
        })
        $counts = Get-AiOsRobocopyCounts -Output $robocopyLines
        $copiedBytes = Get-AiOsDirectorySize -Path $snapshotPath
        $destBytesAfter = $destBytesBefore + $copiedBytes

        $copiedCountText = if ($counts.files_copied -ge 0) { "{0:N0} files" -f $counts.files_copied } else { "count unavailable" }
        $skippedCountText = if ($counts.files_skipped -ge 0) { "{0:N0} files" -f $counts.files_skipped } else { "count unavailable" }
        $fileCountCopied = if ($counts.files_copied -ge 0) { [int]$counts.files_copied } else { 0 }

        Write-Host ""
        Write-Host "Source data measured:        $(Format-AiOsBytes -Bytes $sourceBytes)"
        Write-Host "Current backup size (T9):    $(Format-AiOsBytes -Bytes $destBytesAfter)"
        Write-Host "Copied this run:             $copiedCountText / $(Format-AiOsBytes -Bytes $copiedBytes)"
        Write-Host "Skipped (already current):   $skippedCountText"
        Write-Host "Produced this backup session: $(Format-AiOsBytes -Bytes $copiedBytes)"
        Write-Host ""
        $copiedHuman = Format-AiOsBytes -Bytes $copiedBytes
        Write-AiOsBackupProductivityOutput -ProductivityDelta $productivityDelta -CopiedHuman $copiedHuman -ChangedCopied $fileCountCopied -DeletedRecorded $deletedFiles.Count -RestoreRequiresFullBackup $false -RetentionCandidateCount $retentionPreviewCandidates.Count
        if ($productivityDelta.productivity_delta_today_files -eq "UNKNOWN") {
            Write-Host "Productivity delta today: UNKNOWN"
        } else {
            Write-Host "Productivity delta today: $($productivityDelta.productivity_delta_today_files) files / $($productivityDelta.productivity_delta_today_human)"
        }
        Write-Host ""

        $majorPaths = @(
            ".git",
            "automation\orchestration",
            "docs\workflows",
            "schemas\aios\orchestration",
            "services\python_supervisor",
            "telemetry"
        )

        $missingPaths = @($majorPaths | Where-Object {
            -not (Test-Path -LiteralPath (Join-Path $snapshotPath $_))
        })

        $manifestStatus = "SUCCESS"
        $manifestMessage = "Backup snapshot created and verified."
        $exitCode = 0
        if ($robocopyExitCode -ge 8) {
            $manifestStatus = "FAILED"
            $manifestMessage = "Robocopy reported a failure."
            $exitCode = $robocopyExitCode
        } elseif ($missingPaths.Count -gt 0) {
            $manifestStatus = "FAILED"
            $manifestMessage = "Snapshot verification failed. Missing expected paths: $($missingPaths -join ', ')."
            $exitCode = 9
        }

        Write-AiOsBackupManifest -Path $manifestPath -Status $manifestStatus -RobocopyExitCode $robocopyExitCode -GitInfo $gitInfo -GitStatus $gitStatus -ProtectedLocks $protectedLocks -ProductivityDelta $productivityDelta -CopiedBytes ([long]$copiedBytes) -CopiedHuman $copiedHuman -ChangedFiles $changedFiles -DeletedFiles $deletedFiles -FileCountCopied $fileCountCopied -DeltaSourceRange $deltaSourceRange -BaseBackupId $baseBackupId -BaseBackupCommitHash $baseBackupCommitHash -RestoreRequiresFullBackup $false -RetentionClass $retentionClass -RetentionPreviewCandidates $retentionPreviewCandidates -Message $manifestMessage

        $result = New-AiOsBackupResult -Status $manifestStatus -Message $manifestMessage -RobocopyExitCode $robocopyExitCode -ExitCode $exitCode
        $result | Add-Member -NotePropertyName source_bytes -NotePropertyValue ([long]$sourceBytes)
        $result | Add-Member -NotePropertyName dest_bytes -NotePropertyValue ([long]$destBytesAfter)
        $result | Add-Member -NotePropertyName copied_bytes -NotePropertyValue ([long]$copiedBytes)
        $result | Add-Member -NotePropertyName files_copied -NotePropertyValue $fileCountCopied
        $result | Add-Member -NotePropertyName files_skipped -NotePropertyValue ([int]$counts.files_skipped)
        $result | Add-Member -NotePropertyName source_human -NotePropertyValue (Format-AiOsBytes -Bytes $sourceBytes)
        $result | Add-Member -NotePropertyName dest_human -NotePropertyValue (Format-AiOsBytes -Bytes $destBytesAfter)
        $result | Add-Member -NotePropertyName copied_human -NotePropertyValue $copiedHuman
        Add-AiOsProductivityFields -Target $result -ProductivityDelta $productivityDelta

        if ($OutputJson) {
            $result | ConvertTo-Json -Depth 6
        }
        else {
            Write-Host "AI_OS T9 Snapshot Backup"
            Write-Host "Status: $manifestStatus"
            Write-Host "Backup mode: $selectedBackupMode"
            Write-Host "Selected reason: $selectedBackupModeReason"
            Write-Host "Snapshot path: $snapshotPath"
            Write-Host "Robocopy log path: $robocopyLogPath"
            Write-Host "Manifest path: $manifestPath"
            Write-Host "Robocopy exit code: $robocopyExitCode"
            Write-Host "Active repo mutation: NO"
            Write-Host "Scheduler behavior: NO"
            Write-Host "Runtime mutation: BACKUP_DESTINATION_ONLY"
        }

        exit $exitCode
    }
    finally {
        if ($lockCreated) {
            Remove-AiOsBackupLock -BackupLockPath $backupLockPath
        }
    }
}
catch {
    $result = New-AiOsBackupResult -Status "FAILED" -Message $_.Exception.Message -ExitCode 1
    $result | ConvertTo-Json -Depth 6
    exit 1
}
