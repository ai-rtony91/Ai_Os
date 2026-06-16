Set-StrictMode -Version Latest

function ConvertTo-AiOsBackupMetricSize {
    param([Parameter(Mandatory = $true)][int64]$Bytes)

    return [pscustomobject][ordered]@{
        bytes = [int64]$Bytes
        kb = [math]::Round($Bytes / 1KB, 2)
        mb = [math]::Round($Bytes / 1MB, 4)
    }
}

function Get-AiOsRobocopyStatus {
    param([AllowNull()][object]$RobocopyExit)

    if ($null -eq $RobocopyExit) {
        return "NOT_RUN_DRY_RUN"
    }

    $exit = [int]$RobocopyExit
    if ($exit -ge 0 -and $exit -lt 8) {
        return "OK"
    }

    return "FAILED"
}

function New-AiOsBackupCopiedMetrics {
    param(
        [Parameter(Mandatory = $true)][string]$BackupMode,
        [AllowEmptyString()][string]$BackupRoot,
        [AllowEmptyString()][string]$Destination,
        [AllowNull()][object]$RobocopyExit = $null,
        [int]$CopiedFilesCount = 0,
        [int64]$CopiedBytes = 0,
        [int]$FailedFilesCount = 0,
        [int]$FailedDirsCount = 0,
        [string[]]$ExcludedPaths = @(),
        [string[]]$ExcludedSecretPatterns = @(),
        [string]$FullSnapshotOrIncremental = "DRY_RUN_PREVIEW"
    )

    $size = ConvertTo-AiOsBackupMetricSize -Bytes $CopiedBytes
    return [pscustomobject][ordered]@{
        backup_mode = $BackupMode
        backup_root = $BackupRoot
        destination = $Destination
        robocopy_exit = if ($null -eq $RobocopyExit) { $null } else { [int]$RobocopyExit }
        robocopy_status = Get-AiOsRobocopyStatus -RobocopyExit $RobocopyExit
        copied_files_count = [int]$CopiedFilesCount
        copied_bytes = [int64]$CopiedBytes
        copied_kb = $size.kb
        copied_mb = $size.mb
        failed_files_count = [int]$FailedFilesCount
        failed_dirs_count = [int]$FailedDirsCount
        excluded_paths = @($ExcludedPaths)
        excluded_secret_patterns = @($ExcludedSecretPatterns)
        full_snapshot_or_incremental = $FullSnapshotOrIncremental
    }
}

function Invoke-AiOsBackupGit {
    param(
        [Parameter(Mandatory = $true)][string]$RepoRoot,
        [Parameter(Mandatory = $true)][string[]]$Arguments
    )

    $previousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    $lines = @(& git -C $RepoRoot @Arguments 2>$null)
    $exitCode = $LASTEXITCODE
    $ErrorActionPreference = $previousErrorActionPreference

    return [pscustomobject]@{
        exit_code = [int]$exitCode
        lines = @($lines | ForEach-Object { [string]$_ })
    }
}

function Test-AiOsBackupGitCommit {
    param(
        [Parameter(Mandatory = $true)][string]$RepoRoot,
        [AllowNull()][string]$Commit
    )

    if ([string]::IsNullOrWhiteSpace($Commit)) {
        return $false
    }

    $result = Invoke-AiOsBackupGit -RepoRoot $RepoRoot -Arguments @("cat-file", "-e", "$Commit^{commit}")
    return ($result.exit_code -eq 0)
}

function Get-AiOsBackupGitHead {
    param([Parameter(Mandatory = $true)][string]$RepoRoot)

    $result = Invoke-AiOsBackupGit -RepoRoot $RepoRoot -Arguments @("rev-parse", "HEAD")
    if ($result.exit_code -ne 0 -or @($result.lines).Count -eq 0) {
        return ""
    }

    return [string]$result.lines[0]
}

function Get-AiOsBackupPrNumbers {
    param([AllowEmptyCollection()][string[]]$Onelines = @())

    $numbers = New-Object System.Collections.Generic.List[string]
    foreach ($line in $Onelines) {
        foreach ($match in [regex]::Matches([string]$line, '(?i)(?:#|PR\s*#?)(\d+)')) {
            $numbers.Add([string]$match.Groups[1].Value) | Out-Null
        }
    }

    return @($numbers | Sort-Object -Unique)
}

function Get-AiOsBackupPatchDeltaBytes {
    param(
        [Parameter(Mandatory = $true)][string]$RepoRoot,
        [Parameter(Mandatory = $true)][string]$Range
    )

    $result = Invoke-AiOsBackupGit -RepoRoot $RepoRoot -Arguments @("diff", "--binary", "--no-ext-diff", $Range)
    if ($result.exit_code -ne 0 -or @($result.lines).Count -eq 0) {
        return 0L
    }

    $text = @($result.lines) -join [Environment]::NewLine
    return [int64][System.Text.Encoding]::UTF8.GetByteCount($text)
}

function Get-AiOsBackupTouchedFileBytes {
    param(
        [Parameter(Mandatory = $true)][string]$RepoRoot,
        [AllowEmptyCollection()][string[]]$ChangedFiles = @()
    )

    $total = [int64]0
    foreach ($relativePath in $ChangedFiles) {
        if ([string]::IsNullOrWhiteSpace($relativePath)) {
            continue
        }

        $fullPath = Join-Path $RepoRoot $relativePath
        if (Test-Path -LiteralPath $fullPath -PathType Leaf) {
            $total += [int64](Get-Item -LiteralPath $fullPath).Length
        }
    }

    return $total
}

function Get-AiOsBackupGitDeltaSummary {
    param(
        [Parameter(Mandatory = $true)][string]$RepoRoot,
        [AllowNull()][string]$BaseCommit,
        [AllowNull()][string]$CurrentCommit = ""
    )

    $empty = [pscustomobject][ordered]@{
        available = $false
        baseline_note = "baseline commit missing"
        commits = 0
        onelines = @()
        prs = @()
        changed_files = @()
        insertions = 0
        deletions = 0
        patch_bytes = 0L
        touched_bytes = 0L
    }

    if (-not (Test-AiOsBackupGitCommit -RepoRoot $RepoRoot -Commit $BaseCommit)) {
        return $empty
    }

    if ([string]::IsNullOrWhiteSpace($CurrentCommit)) {
        $empty.baseline_note = "current commit missing"
        return $empty
    }

    if (-not (Test-AiOsBackupGitCommit -RepoRoot $RepoRoot -Commit $CurrentCommit)) {
        $empty.baseline_note = "current commit missing"
        return $empty
    }

    if ($BaseCommit -eq $CurrentCommit) {
        $empty.available = $true
        $empty.baseline_note = "base commit equals current commit"
        return $empty
    }

    $range = "{0}..{1}" -f $BaseCommit, $CurrentCommit
    $logResult = Invoke-AiOsBackupGit -RepoRoot $RepoRoot -Arguments @("log", "--oneline", $range)
    $nameResult = Invoke-AiOsBackupGit -RepoRoot $RepoRoot -Arguments @("diff", "--name-only", $range)
    $numstatResult = Invoke-AiOsBackupGit -RepoRoot $RepoRoot -Arguments @("diff", "--numstat", $range)

    if ($logResult.exit_code -ne 0 -or $nameResult.exit_code -ne 0 -or $numstatResult.exit_code -ne 0) {
        $empty.baseline_note = "git delta command failed"
        return $empty
    }

    $insertions = 0
    $deletions = 0
    foreach ($line in $numstatResult.lines) {
        if ([string]::IsNullOrWhiteSpace($line)) {
            continue
        }

        $parts = [string]$line -split "`t"
        if ($parts.Count -lt 3) {
            continue
        }

        if ($parts[0] -match '^\d+$') {
            $insertions += [int]$parts[0]
        }

        if ($parts[1] -match '^\d+$') {
            $deletions += [int]$parts[1]
        }
    }

    $changedFiles = @($nameResult.lines | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
    $patchBytes = Get-AiOsBackupPatchDeltaBytes -RepoRoot $RepoRoot -Range $range
    $touchedBytes = Get-AiOsBackupTouchedFileBytes -RepoRoot $RepoRoot -ChangedFiles $changedFiles

    return [pscustomobject][ordered]@{
        available = $true
        baseline_note = "available"
        commits = [int]@($logResult.lines | Where-Object { -not [string]::IsNullOrWhiteSpace($_) }).Count
        onelines = @($logResult.lines)
        prs = @(Get-AiOsBackupPrNumbers -Onelines $logResult.lines)
        changed_files = @($changedFiles)
        insertions = [int]$insertions
        deletions = [int]$deletions
        patch_bytes = [int64]$patchBytes
        touched_bytes = [int64]$touchedBytes
    }
}

function New-AiOsDevWorkDeltaMetrics {
    param(
        [Parameter(Mandatory = $true)][string]$RepoRoot,
        [AllowNull()][string]$BaseCommit,
        [AllowNull()][string]$CurrentCommit = ""
    )

    $summary = Get-AiOsBackupGitDeltaSummary -RepoRoot $RepoRoot -BaseCommit $BaseCommit -CurrentCommit $CurrentCommit
    $patchSize = ConvertTo-AiOsBackupMetricSize -Bytes ([int64]$summary.patch_bytes)
    $touchedSize = ConvertTo-AiOsBackupMetricSize -Bytes ([int64]$summary.touched_bytes)

    return [pscustomobject][ordered]@{
        available = [bool]$summary.available
        baseline_note = [string]$summary.baseline_note
        base_commit = if ([string]::IsNullOrWhiteSpace($BaseCommit)) { $null } else { [string]$BaseCommit }
        current_commit = $CurrentCommit
        commits_included_count = [int]$summary.commits
        commits_included_oneline = @($summary.onelines)
        pr_numbers_detected = @($summary.prs)
        changed_files_count = [int]@($summary.changed_files).Count
        insertions = [int]$summary.insertions
        deletions = [int]$summary.deletions
        patch_delta_bytes = [int64]$summary.patch_bytes
        patch_delta_kb = $patchSize.kb
        patch_delta_mb = $patchSize.mb
        touched_changed_file_bytes = [int64]$summary.touched_bytes
        touched_changed_file_kb = $touchedSize.kb
        touched_changed_file_mb = $touchedSize.mb
    }
}

function Get-AiOsBackupDayStartCommit {
    param(
        [Parameter(Mandatory = $true)][string]$RepoRoot,
        [datetime]$DayStart = (Get-Date).Date
    )

    $before = $DayStart.ToString("yyyy-MM-ddTHH:mm:ssK")
    $result = Invoke-AiOsBackupGit -RepoRoot $RepoRoot -Arguments @("rev-list", "-1", "--before=$before", "HEAD")
    if ($result.exit_code -ne 0 -or @($result.lines).Count -eq 0) {
        return ""
    }

    return [string]$result.lines[0]
}

function New-AiOsDailyWorkMetrics {
    param(
        [Parameter(Mandatory = $true)][string]$RepoRoot,
        [AllowNull()][string]$CurrentCommit = "",
        [AllowNull()][string]$DayStartCommit = "",
        [datetime]$LocalDate = (Get-Date).Date
    )

    $base = if ([string]::IsNullOrWhiteSpace($DayStartCommit)) {
        Get-AiOsBackupDayStartCommit -RepoRoot $RepoRoot -DayStart $LocalDate
    } else {
        [string]$DayStartCommit
    }

    $summary = Get-AiOsBackupGitDeltaSummary -RepoRoot $RepoRoot -BaseCommit $base -CurrentCommit $CurrentCommit
    $patchSize = ConvertTo-AiOsBackupMetricSize -Bytes ([int64]$summary.patch_bytes)
    $touchedSize = ConvertTo-AiOsBackupMetricSize -Bytes ([int64]$summary.touched_bytes)

    return [pscustomobject][ordered]@{
        available = [bool]$summary.available
        baseline_note = [string]$summary.baseline_note
        local_date = $LocalDate.ToString("yyyy-MM-dd")
        day_start_commit = if ([string]::IsNullOrWhiteSpace($base)) { $null } else { $base }
        current_commit = $CurrentCommit
        commits_today_count = [int]$summary.commits
        prs_today_detected = @($summary.prs)
        changed_files_today_count = [int]@($summary.changed_files).Count
        insertions_today = [int]$summary.insertions
        deletions_today = [int]$summary.deletions
        patch_delta_today_kb = $patchSize.kb
        patch_delta_today_mb = $patchSize.mb
        touched_changed_file_today_kb = $touchedSize.kb
        touched_changed_file_today_mb = $touchedSize.mb
    }
}

function Resolve-AiOsBackupTimeslotWindow {
    param(
        [string]$TimeslotLabel = "manual",
        [AllowNull()][string]$WindowStartLocal = "",
        [AllowNull()][string]$WindowEndLocal = "",
        [datetime]$Now = (Get-Date)
    )

    $label = if ([string]::IsNullOrWhiteSpace($TimeslotLabel)) { "manual" } else { $TimeslotLabel.Trim() }
    $localDate = $Now.Date
    $parsedEnd = $null
    $normalizedLabel = $label -replace '\s+', ''

    if ($normalizedLabel -match '^(?<hour>\d{1,2})(:(?<minute>\d{2}))?(?<ampm>am|pm)$') {
        $hour = [int]$Matches.hour
        $minute = if (-not $Matches.ContainsKey("minute") -or [string]::IsNullOrWhiteSpace($Matches["minute"])) { 0 } else { [int]$Matches["minute"] }
        $ampm = $Matches.ampm.ToLowerInvariant()
        if ($ampm -eq "pm" -and $hour -lt 12) { $hour += 12 }
        if ($ampm -eq "am" -and $hour -eq 12) { $hour = 0 }
        $parsedEnd = $localDate.AddHours($hour).AddMinutes($minute)
    }

    $windowEnd = if (-not [string]::IsNullOrWhiteSpace($WindowEndLocal)) {
        [datetime]::Parse($WindowEndLocal)
    } elseif ($null -ne $parsedEnd) {
        $parsedEnd
    } else {
        $Now
    }

    $defaultStart = if ($label -match '^(?i)10\s*PM$') {
        $localDate.AddHours(15)
    } else {
        $localDate
    }

    $windowStart = if (-not [string]::IsNullOrWhiteSpace($WindowStartLocal)) {
        [datetime]::Parse($WindowStartLocal)
    } else {
        $defaultStart
    }

    return [pscustomobject][ordered]@{
        timeslot_label = $label
        timeslot_local = $windowEnd.ToString("yyyy-MM-dd HH:mm:ss K")
        window_start_local = $windowStart.ToString("yyyy-MM-dd HH:mm:ss K")
        window_end_local = $windowEnd.ToString("yyyy-MM-dd HH:mm:ss K")
    }
}

function New-AiOsTimeslotWorkMetrics {
    param(
        [Parameter(Mandatory = $true)][string]$RepoRoot,
        [AllowNull()][string]$CurrentCommit = "",
        [Parameter(Mandatory = $true)][string]$TimeslotLabel,
        [Parameter(Mandatory = $true)][string]$WindowStartLocal,
        [Parameter(Mandatory = $true)][string]$WindowEndLocal,
        [AllowNull()][string]$BaseCommit = ""
    )

    $summary = Get-AiOsBackupGitDeltaSummary -RepoRoot $RepoRoot -BaseCommit $BaseCommit -CurrentCommit $CurrentCommit
    $patchSize = ConvertTo-AiOsBackupMetricSize -Bytes ([int64]$summary.patch_bytes)
    $touchedSize = ConvertTo-AiOsBackupMetricSize -Bytes ([int64]$summary.touched_bytes)

    return [pscustomobject][ordered]@{
        available = [bool]$summary.available
        baseline_note = [string]$summary.baseline_note
        timeslot_label = $TimeslotLabel
        window_start_local = $WindowStartLocal
        window_end_local = $WindowEndLocal
        base_commit = if ([string]::IsNullOrWhiteSpace($BaseCommit)) { $null } else { [string]$BaseCommit }
        current_commit = $CurrentCommit
        commits_in_window_count = [int]$summary.commits
        prs_in_window_detected = @($summary.prs)
        changed_files_in_window_count = [int]@($summary.changed_files).Count
        insertions_in_window = [int]$summary.insertions
        deletions_in_window = [int]$summary.deletions
        patch_delta_window_kb = $patchSize.kb
        patch_delta_window_mb = $patchSize.mb
        touched_changed_file_window_kb = $touchedSize.kb
        touched_changed_file_window_mb = $touchedSize.mb
    }
}

function Get-AiOsBackupWorkDeltaReport {
    param(
        [Parameter(Mandatory = $true)][string]$RepoRoot,
        [AllowNull()][string]$BaseCommit = "",
        [AllowNull()][string]$CurrentCommit = "",
        [string]$TimeslotLabel = "manual",
        [AllowNull()][string]$WindowStartLocal = "",
        [AllowNull()][string]$WindowEndLocal = "",
        [AllowNull()][string]$DayStartCommit = "",
        [AllowNull()][string]$TimeslotBaseCommit = "",
        [AllowNull()][string]$LastSuccessfulBackupCommit = ""
    )

    $head = if ([string]::IsNullOrWhiteSpace($CurrentCommit)) {
        Get-AiOsBackupGitHead -RepoRoot $RepoRoot
    } else {
        [string]$CurrentCommit
    }

    $window = Resolve-AiOsBackupTimeslotWindow -TimeslotLabel $TimeslotLabel -WindowStartLocal $WindowStartLocal -WindowEndLocal $WindowEndLocal
    $devMetrics = New-AiOsDevWorkDeltaMetrics -RepoRoot $RepoRoot -BaseCommit $BaseCommit -CurrentCommit $head
    $dailyMetrics = New-AiOsDailyWorkMetrics -RepoRoot $RepoRoot -CurrentCommit $head -DayStartCommit $DayStartCommit
    $slotBase = if ([string]::IsNullOrWhiteSpace($TimeslotBaseCommit)) { $BaseCommit } else { $TimeslotBaseCommit }
    $timeslotMetrics = New-AiOsTimeslotWorkMetrics -RepoRoot $RepoRoot -CurrentCommit $head -TimeslotLabel $window.timeslot_label -WindowStartLocal $window.window_start_local -WindowEndLocal $window.window_end_local -BaseCommit $slotBase

    return [pscustomobject][ordered]@{
        backup_timeslot_label = $window.timeslot_label
        backup_timeslot_local = $window.timeslot_local
        backup_window_start = $window.window_start_local
        backup_window_end = $window.window_end_local
        last_successful_backup_commit = if ([string]::IsNullOrWhiteSpace($LastSuccessfulBackupCommit)) { $BaseCommit } else { $LastSuccessfulBackupCommit }
        current_commit = $head
        dev_work_delta_metrics = $devMetrics
        daily_work_metrics = $dailyMetrics
        timeslot_work_metrics = $timeslotMetrics
    }
}
