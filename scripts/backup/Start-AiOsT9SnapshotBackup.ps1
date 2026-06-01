[CmdletBinding()]
param(
    [string]$SourceRepo = "C:\Dev\Ai.Os",
    [string]$BackupRoot = "D:\T9_FOB",
    [switch]$Preview,
    [switch]$OutputJson,
    [switch]$AllowDirty
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
        productivity_delta_summary = "Productivity delta: $($delta.files) files / $(Format-AiOsBytes -Bytes ([double]$delta.bytes)) / $($delta.commits) commits since last backup."
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
        excluded_paths = $excludedDirs
        robocopy_exit_code = $RobocopyExitCode
        exit_code = $ExitCode
        mutation_scope = if ($Preview) { "NONE" } else { "BACKUP_SNAPSHOT_ONLY" }
        active_repo_mutation = "NO"
        scheduler_behavior = "NO"
        runtime_mutation = if ($Preview) { "NO" } else { "BACKUP_DESTINATION_ONLY" }
        allow_dirty = [bool]$AllowDirty
        backup_lock_path = $backupLockPath
        robocopy_log_path = $robocopyLogPath
        manifest_path = $manifestPath
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
    $protectedLocks = @(Get-AiOsProtectedActionLocks -RepoRoot $normalizedSource -BackupReportRoot $backupReportRoot -BackupLockPath $backupLockPath)
    if ($protectedLocks.Count -gt 0) {
        throw "PROTECTED_ACTION_LOCK_EXISTS: $($protectedLocks.path -join ', ')"
    }

    if (-not $Preview -and -not $AllowDirty -and -not $gitStatus.is_clean) {
        throw "DIRTY_REPO: Backup requires clean git status. Re-run with -AllowDirty only after explicit approval. Status: $($gitStatus.lines -join ' | ')"
    }

    $plannedCommand = @(
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

    $excludeNames = @("node_modules", "__pycache__", ".pytest_cache", ".codex")

    if ($Preview) {
        $sourceBytes = Get-AiOsDirectorySize -Path $normalizedSource -ExcludeNames $excludeNames
        $destBytes = Get-AiOsDirectorySize -Path $normalizedBackupRoot

        $result = New-AiOsBackupResult -Status "PREVIEW" -Message "Preview only. No folder was created, no lock was created, and robocopy was not run."
        $result | Add-Member -NotePropertyName planned_command -NotePropertyValue ($plannedCommand -join " ")
        $result | Add-Member -NotePropertyName source_bytes -NotePropertyValue ([long]$sourceBytes)
        $result | Add-Member -NotePropertyName dest_bytes -NotePropertyValue ([long]$destBytes)
        $result | Add-Member -NotePropertyName copied_bytes -NotePropertyValue 0
        $result | Add-Member -NotePropertyName copied_human -NotePropertyValue "pending (preview - robocopy not run)"
        $result | Add-Member -NotePropertyName source_human -NotePropertyValue (Format-AiOsBytes -Bytes $sourceBytes)
        $result | Add-Member -NotePropertyName dest_human -NotePropertyValue (Format-AiOsBytes -Bytes $destBytes)
        $result | Add-Member -NotePropertyName git_status_clean -NotePropertyValue ([bool]$gitStatus.is_clean)
        $result | Add-Member -NotePropertyName protected_action_lock_count -NotePropertyValue ([int]$protectedLocks.Count)
        Add-AiOsProductivityFields -Target $result -ProductivityDelta $productivityDelta
        if ($OutputJson) {
            $result | ConvertTo-Json -Depth 6
        }
        else {
            Write-Host "AI_OS T9 Snapshot Backup Preview"
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
            Write-Host "Copied this run:             pending (preview - robocopy not run)"
            Write-Host "Skipped (already current):   pending (preview - robocopy not run)"
            Write-Host "Produced this backup session: pending (preview - robocopy not run)"
            Write-Host ""
            Write-Host "Backup total copied: pending (preview - robocopy not run)"
            Write-Host "Productivity delta since previous backup: $($productivityDelta.productivity_delta_files) files / $($productivityDelta.productivity_delta_human) / $($productivityDelta.productivity_delta_commits) commits"
            if ($productivityDelta.productivity_delta_today_files -eq "UNKNOWN") {
                Write-Host "Productivity delta today: UNKNOWN"
            } else {
                Write-Host "Productivity delta today: $($productivityDelta.productivity_delta_today_files) files / $($productivityDelta.productivity_delta_today_human)"
            }
            Write-Host "PR merges included: $($productivityDelta.productivity_delta_pr_merges)"
            Write-Host "Runtime exclusion status: $($productivityDelta.runtime_exclusion_status)"
            Write-Host $productivityDelta.productivity_delta_summary
            Write-Host ""
            Write-Host "Planned command:"
            Write-Host ($plannedCommand -join " ")
            Write-Host "No folder was created. No lock was created. Robocopy was not run."
        }
        exit 0
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

        Write-Host ""
        Write-Host "Source data measured:        $(Format-AiOsBytes -Bytes $sourceBytes)"
        Write-Host "Current backup size (T9):    $(Format-AiOsBytes -Bytes $destBytesAfter)"
        Write-Host "Copied this run:             $copiedCountText / $(Format-AiOsBytes -Bytes $copiedBytes)"
        Write-Host "Skipped (already current):   $skippedCountText"
        Write-Host "Produced this backup session: $(Format-AiOsBytes -Bytes $copiedBytes)"
        Write-Host ""
        $copiedHuman = Format-AiOsBytes -Bytes $copiedBytes
        Write-Host "Backup total copied: $copiedHuman"
        Write-Host "Productivity delta since previous backup: $($productivityDelta.productivity_delta_files) files / $($productivityDelta.productivity_delta_human) / $($productivityDelta.productivity_delta_commits) commits"
        if ($productivityDelta.productivity_delta_today_files -eq "UNKNOWN") {
            Write-Host "Productivity delta today: UNKNOWN"
        } else {
            Write-Host "Productivity delta today: $($productivityDelta.productivity_delta_today_files) files / $($productivityDelta.productivity_delta_today_human)"
        }
        Write-Host "PR merges included: $($productivityDelta.productivity_delta_pr_merges)"
        Write-Host "Runtime exclusion status: $($productivityDelta.runtime_exclusion_status)"
        Write-Host $productivityDelta.productivity_delta_summary
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

        Write-AiOsBackupManifest -Path $manifestPath -Status $manifestStatus -RobocopyExitCode $robocopyExitCode -GitInfo $gitInfo -GitStatus $gitStatus -ProtectedLocks $protectedLocks -ProductivityDelta $productivityDelta -CopiedBytes ([long]$copiedBytes) -CopiedHuman $copiedHuman -Message $manifestMessage

        $result = New-AiOsBackupResult -Status $manifestStatus -Message $manifestMessage -RobocopyExitCode $robocopyExitCode -ExitCode $exitCode
        $result | Add-Member -NotePropertyName source_bytes -NotePropertyValue ([long]$sourceBytes)
        $result | Add-Member -NotePropertyName dest_bytes -NotePropertyValue ([long]$destBytesAfter)
        $result | Add-Member -NotePropertyName copied_bytes -NotePropertyValue ([long]$copiedBytes)
        $result | Add-Member -NotePropertyName files_copied -NotePropertyValue ([int]$counts.files_copied)
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
