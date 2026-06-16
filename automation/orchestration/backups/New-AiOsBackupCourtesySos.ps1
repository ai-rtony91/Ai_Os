Set-StrictMode -Version Latest

function Get-AiOsCourtesyValue {
    param(
        [AllowNull()][object]$Object,
        [Parameter(Mandatory = $true)][string]$Name,
        [AllowNull()][object]$Default = $null
    )

    if ($null -eq $Object) {
        return $Default
    }

    if ($Object.PSObject.Properties.Name -contains $Name) {
        return $Object.$Name
    }

    return $Default
}

function New-AiOsBackupCourtesySos {
    param(
        [Parameter(Mandatory = $true)][string]$Status,
        [Parameter(Mandatory = $true)][string]$TimeslotLabel,
        [AllowNull()][object]$CopiedMetrics,
        [AllowNull()][object]$DevWorkDeltaMetrics,
        [AllowNull()][object]$DailyWorkMetrics,
        [AllowNull()][string]$BaseCommit = "",
        [AllowNull()][string]$CurrentCommit = "",
        [AllowNull()][string]$Destination = "",
        [AllowNull()][object]$RobocopyExit = $null,
        [int]$FailedFilesCount = 0,
        [int]$FailedDirsCount = 0,
        [AllowNull()][string]$LogPath = "",
        [switch]$Failure
    )

    $copiedMb = Get-AiOsCourtesyValue -Object $CopiedMetrics -Name "copied_mb" -Default 0
    $copiedFiles = Get-AiOsCourtesyValue -Object $CopiedMetrics -Name "copied_files_count" -Default 0
    $patchKb = Get-AiOsCourtesyValue -Object $DevWorkDeltaMetrics -Name "patch_delta_kb" -Default 0
    $changedFiles = Get-AiOsCourtesyValue -Object $DevWorkDeltaMetrics -Name "changed_files_count" -Default 0
    $insertions = Get-AiOsCourtesyValue -Object $DevWorkDeltaMetrics -Name "insertions" -Default 0
    $deletions = Get-AiOsCourtesyValue -Object $DevWorkDeltaMetrics -Name "deletions" -Default 0
    $dailyPatchKb = Get-AiOsCourtesyValue -Object $DailyWorkMetrics -Name "patch_delta_today_kb" -Default 0
    $dailyCommits = Get-AiOsCourtesyValue -Object $DailyWorkMetrics -Name "commits_today_count" -Default 0

    $isFailure = [bool]$Failure -or $Status -match '^(FAILED|FAILURE|ERROR|BLOCKED)$'
    if ($isFailure) {
        $exitText = if ($null -eq $RobocopyExit) { "NOT_RUN" } else { [string][int]$RobocopyExit }
        $message = @"
AIOS T9 backup failed.
Status: $Status
Time slot: $TimeslotLabel
Robocopy exit: $exitText
Failed files: $FailedFilesCount
Failed dirs: $FailedDirsCount
Log: $LogPath
Safety: no delete/mirror behavior performed.
"@.Trim()
    }
    else {
        $message = @"
AIOS T9 backup complete.
Status: $Status
Time slot: $TimeslotLabel
Backup copied: $copiedMb MB / $copiedFiles files
New dev work: $patchKb KB patch / $changedFiles files / $insertions insertions / $deletions deletions
Daily work: $dailyPatchKb KB patch today / $dailyCommits commits
From: $BaseCommit
To: $CurrentCommit
Destination: $Destination
Safety: secrets excluded, no delete/mirror behavior.
"@.Trim()
    }

    return [pscustomobject][ordered]@{
        required = $true
        mode = "REPORT_ONLY"
        message = $message
        notify_on_success = $true
        notify_on_failure = $true
        scheduler_active = $false
    }
}
