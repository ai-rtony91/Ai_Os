<#
Schema/contract reference: AIOS_POST_MAIN_UPDATE_BACKUP_PLAN.v1
Mode: DRY_RUN by default; operator-approved snapshot only with -RunBackup and -ApprovedDestinationRoot.
blocked_capabilities:
  - scheduler_registration
  - repo_mutation
  - git_mutation
  - delete_or_mirror_behavior
  - worker_launch
  - packet_movement
  - approval_mutation
next_safe_action: Run preview first. Use -RunBackup only with -ApprovedDestinationRoot D:\T9_FOB after Human Owner approval.
commit_performed: NO / push_performed: NO
#>

[CmdletBinding()]
param(
    [string]$SourceRepo = "C:\Dev\Ai.Os",
    [string]$StateFilePath = "telemetry\backup_reports\AIOS_POST_MAIN_UPDATE_BACKUP_STATE.json",
    [switch]$RunBackup,
    [string]$ApprovedDestinationRoot = "",
    [switch]$OutputJson
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function ConvertTo-AiOsFullPath {
    param([Parameter(Mandatory = $true)][string]$Path)

    return [System.IO.Path]::GetFullPath($Path).TrimEnd("\")
}

function ConvertTo-AiOsRelativePath {
    param(
        [Parameter(Mandatory = $true)][string]$Root,
        [Parameter(Mandatory = $true)][string]$Path
    )

    $fullRoot = ConvertTo-AiOsFullPath -Path $Root
    $fullPath = ConvertTo-AiOsFullPath -Path $Path
    if ($fullPath.StartsWith($fullRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
        return $fullPath.Substring($fullRoot.Length).TrimStart("\").Replace("\", "/")
    }

    return $fullPath.Replace("\", "/")
}

function Read-AiOsBackupState {
    param([Parameter(Mandatory = $true)][string]$Path)

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return $null
    }

    try {
        return Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json
    }
    catch {
        return [pscustomobject]@{
            schema = "AIOS_POST_MAIN_UPDATE_BACKUP_STATE_PARSE_ERROR.v1"
            parse_error = $_.Exception.Message
            state_path = $Path
        }
    }
}

function Get-AiOsFilesystemDrives {
    $drives = Get-PSDrive -PSProvider FileSystem | Sort-Object Name
    @($drives | ForEach-Object {
        [pscustomobject]@{
            name = $_.Name
            root = $_.Root
            free = $_.Free
            used = $_.Used
        }
    })
}

function New-AiOsBackupReport {
    param(
        [Parameter(Mandatory = $true)][string]$Status,
        [Parameter(Mandatory = $true)][string]$Mode,
        [Parameter(Mandatory = $true)][string]$CurrentCommit,
        [Parameter(Mandatory = $true)][string]$ShortCommit,
        [AllowNull()][string]$LastBackedUpCommit,
        [Parameter(Mandatory = $true)][bool]$BackupRequired,
        [AllowNull()][string]$DestinationPath,
        [AllowNull()][string]$RobocopyPreview,
        [int]$RobocopyExitCode = -1,
        [bool]$StateUpdated = $false,
        [int]$WritesPerformed = 0,
        [Parameter(Mandatory = $true)][string]$NextSafeAction,
        [AllowNull()][string]$BlockedReason = "",
        [object[]]$AvailableDrives = @()
    )

    [pscustomobject]@{
        schema = "AIOS_POST_MAIN_UPDATE_BACKUP_PLAN.v1"
        mode = $Mode
        current_commit = $CurrentCommit
        short_commit = $ShortCommit
        last_backed_up_commit = $LastBackedUpCommit
        backup_required = $BackupRequired
        backup_status = $Status
        destination_path = $DestinationPath
        robocopy_preview = $RobocopyPreview
        robocopy_exit_code = $RobocopyExitCode
        state_updated = $StateUpdated
        writes_performed = $WritesPerformed
        state_file_path = ConvertTo-AiOsRelativePath -Root $normalizedSource -Path $resolvedStateFilePath
        excluded_paths = @(".git", ".codex_backups", "node_modules", "__pycache__", ".venv", "dist", "build")
        blocked_reason = $BlockedReason
        available_drives = @($AvailableDrives)
        blocked_capabilities = @(
            "scheduler_registration",
            "repo_mutation",
            "git_mutation",
            "delete_or_mirror_behavior",
            "worker_launch",
            "packet_movement",
            "approval_mutation"
        )
        next_safe_action = $NextSafeAction
        generated_at = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    }
}

function Write-AiOsBackupState {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$Commit,
        [Parameter(Mandatory = $true)][string]$BackupPath,
        [Parameter(Mandatory = $true)][string]$Mode
    )

    $stateRoot = Split-Path -Parent $Path
    if (-not (Test-Path -LiteralPath $stateRoot -PathType Container)) {
        New-Item -ItemType Directory -Force -Path $stateRoot | Out-Null
    }

    $state = [ordered]@{
        schema = "AIOS_POST_MAIN_UPDATE_BACKUP_STATE.v1"
        last_backed_up_commit = $Commit
        last_backup_path = $BackupPath
        last_backup_completed_at = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
        backup_mode = $Mode
    }

    $state | ConvertTo-Json -Depth 5 | Out-File -FilePath $Path -Encoding utf8 -Force
}

$expectedSource = "C:\Dev\Ai.Os"
$expectedBackupRoot = "D:\T9_FOB"
$normalizedSource = ConvertTo-AiOsFullPath -Path $SourceRepo

if ($normalizedSource -ne $expectedSource) {
    throw "Source repo must be exactly $expectedSource."
}

if (-not (Test-Path -LiteralPath $normalizedSource -PathType Container)) {
    throw "Source repo does not exist: $normalizedSource"
}

$resolvedStateFilePath = if ([System.IO.Path]::IsPathRooted($StateFilePath)) {
    ConvertTo-AiOsFullPath -Path $StateFilePath
}
else {
    ConvertTo-AiOsFullPath -Path (Join-Path $normalizedSource $StateFilePath)
}

$stateRoot = ConvertTo-AiOsFullPath -Path (Join-Path $normalizedSource "telemetry\backup_reports")
if (-not $resolvedStateFilePath.StartsWith($stateRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "State file path must stay under telemetry\backup_reports."
}

$gitCommitOutput = @(& git -C $normalizedSource rev-parse HEAD 2>$null)
$gitCommitExitCode = $LASTEXITCODE
$currentCommit = if ($gitCommitOutput.Count -gt 0) { [string]$gitCommitOutput[0] } else { "" }
if ($gitCommitExitCode -ne 0 -or [string]::IsNullOrWhiteSpace($currentCommit)) {
    throw "Unable to read current main commit with git rev-parse HEAD."
}

$shortCommit = if ($currentCommit.Length -ge 7) { $currentCommit.Substring(0, 7) } else { $currentCommit }
$state = Read-AiOsBackupState -Path $resolvedStateFilePath
$lastBackedUpCommit = if ($null -ne $state -and $state.PSObject.Properties.Name -contains "last_backed_up_commit") {
    [string]$state.last_backed_up_commit
}
else {
    $null
}

$backupRequired = -not ($lastBackedUpCommit -and $lastBackedUpCommit -eq $currentCommit)
$timestamp = Get-Date -Format "yyyy-MM-dd_HHmm"
$destinationName = "AIOS_BACKUP_POST_MAIN_${timestamp}_$shortCommit"
$destinationPath = Join-Path $expectedBackupRoot $destinationName
$excludedDirs = @(".git", ".codex_backups", "node_modules", "__pycache__", ".venv", "dist", "build")
$robocopyPreview = @(
    "robocopy",
    "`"$normalizedSource`"",
    "`"$destinationPath`"",
    "/E",
    "/XD"
) + ($excludedDirs | ForEach-Object { "`"$_`"" }) + @(
    "/R:2",
    "/W:2",
    "/COPY:DAT",
    "/DCOPY:DAT",
    "/NP",
    "/TEE",
    "/LOG:`"$destinationPath\AIOS_BACKUP_ROBOCOPY.log`""
)

if (-not $RunBackup) {
    $status = if ($backupRequired) { "BACKUP_RECOMMENDED" } else { "SKIP_BACKUP" }
    $nextSafeAction = if ($backupRequired) {
        "Run again with -RunBackup -ApprovedDestinationRoot `"D:\T9_FOB`" only after Human Owner approval."
    }
    else {
        "No backup needed for this commit unless manually requested before risky APPLY."
    }

    $report = New-AiOsBackupReport -Status $status `
        -Mode "DRY_RUN" `
        -CurrentCommit $currentCommit `
        -ShortCommit $shortCommit `
        -LastBackedUpCommit $lastBackedUpCommit `
        -BackupRequired $backupRequired `
        -DestinationPath $destinationPath `
        -RobocopyPreview ($robocopyPreview -join " ") `
        -NextSafeAction $nextSafeAction
    $report | ConvertTo-Json -Depth 8
    exit 0
}

if ([string]::IsNullOrWhiteSpace($ApprovedDestinationRoot)) {
    $report = New-AiOsBackupReport -Status "BACKUP_BLOCKED" `
        -Mode "APPLY" `
        -CurrentCommit $currentCommit `
        -ShortCommit $shortCommit `
        -LastBackedUpCommit $lastBackedUpCommit `
        -BackupRequired $backupRequired `
        -DestinationPath $null `
        -RobocopyPreview ($robocopyPreview -join " ") `
        -NextSafeAction "Provide -ApprovedDestinationRoot `"D:\T9_FOB`" to run the backup." `
        -BlockedReason "Missing ApprovedDestinationRoot." `
        -AvailableDrives (Get-AiOsFilesystemDrives)
    $report | ConvertTo-Json -Depth 8
    exit 1
}

$normalizedDestinationRoot = ConvertTo-AiOsFullPath -Path $ApprovedDestinationRoot
if ($normalizedDestinationRoot -ne $expectedBackupRoot) {
    $report = New-AiOsBackupReport -Status "BACKUP_BLOCKED" `
        -Mode "APPLY" `
        -CurrentCommit $currentCommit `
        -ShortCommit $shortCommit `
        -LastBackedUpCommit $lastBackedUpCommit `
        -BackupRequired $backupRequired `
        -DestinationPath $null `
        -RobocopyPreview ($robocopyPreview -join " ") `
        -NextSafeAction "Use the approved destination root exactly: D:\T9_FOB." `
        -BlockedReason "ApprovedDestinationRoot did not match D:\T9_FOB." `
        -AvailableDrives (Get-AiOsFilesystemDrives)
    $report | ConvertTo-Json -Depth 8
    exit 1
}

if (-not (Test-Path -LiteralPath $normalizedDestinationRoot -PathType Container)) {
    $report = New-AiOsBackupReport -Status "BACKUP_BLOCKED" `
        -Mode "APPLY" `
        -CurrentCommit $currentCommit `
        -ShortCommit $shortCommit `
        -LastBackedUpCommit $lastBackedUpCommit `
        -BackupRequired $backupRequired `
        -DestinationPath $destinationPath `
        -RobocopyPreview ($robocopyPreview -join " ") `
        -NextSafeAction "Create or attach D:\T9_FOB before running backup." `
        -BlockedReason "Approved destination root missing." `
        -AvailableDrives (Get-AiOsFilesystemDrives)
    $report | ConvertTo-Json -Depth 8
    exit 1
}

if (-not $backupRequired) {
    $report = New-AiOsBackupReport -Status "SKIP_BACKUP" `
        -Mode "APPLY" `
        -CurrentCommit $currentCommit `
        -ShortCommit $shortCommit `
        -LastBackedUpCommit $lastBackedUpCommit `
        -BackupRequired $false `
        -DestinationPath $destinationPath `
        -RobocopyPreview ($robocopyPreview -join " ") `
        -NextSafeAction "Current commit already has a recorded backup. No snapshot created."
    $report | ConvertTo-Json -Depth 8
    exit 0
}

if (Test-Path -LiteralPath $destinationPath) {
    $report = New-AiOsBackupReport -Status "BACKUP_BLOCKED" `
        -Mode "APPLY" `
        -CurrentCommit $currentCommit `
        -ShortCommit $shortCommit `
        -LastBackedUpCommit $lastBackedUpCommit `
        -BackupRequired $backupRequired `
        -DestinationPath $destinationPath `
        -RobocopyPreview ($robocopyPreview -join " ") `
        -NextSafeAction "Choose a fresh timestamped destination. Existing destination was not touched." `
        -BlockedReason "Destination already exists."
    $report | ConvertTo-Json -Depth 8
    exit 1
}

New-Item -ItemType Directory -Force -Path $destinationPath | Out-Null
$robocopyArgs = @(
    $normalizedSource,
    $destinationPath,
    "/E",
    "/XD"
) + $excludedDirs + @(
    "/R:2",
    "/W:2",
    "/COPY:DAT",
    "/DCOPY:DAT",
    "/NP",
    "/TEE",
    "/LOG:$destinationPath\AIOS_BACKUP_ROBOCOPY.log"
)

& robocopy @robocopyArgs
$robocopyExitCode = $LASTEXITCODE
if ($robocopyExitCode -ge 8) {
    $report = New-AiOsBackupReport -Status "BACKUP_FAILED" `
        -Mode "APPLY" `
        -CurrentCommit $currentCommit `
        -ShortCommit $shortCommit `
        -LastBackedUpCommit $lastBackedUpCommit `
        -BackupRequired $backupRequired `
        -DestinationPath $destinationPath `
        -RobocopyPreview ($robocopyPreview -join " ") `
        -RobocopyExitCode $robocopyExitCode `
        -StateUpdated $false `
        -WritesPerformed 1 `
        -NextSafeAction "Review RoboCopy log. State file was not updated." `
        -BlockedReason "RoboCopy exit code $robocopyExitCode."
    $report | ConvertTo-Json -Depth 8
    exit $robocopyExitCode
}

Write-AiOsBackupState -Path $resolvedStateFilePath -Commit $currentCommit -BackupPath $destinationPath -Mode "operator_approved_robocopy"
$report = New-AiOsBackupReport -Status "BACKUP_COMPLETE" `
    -Mode "APPLY" `
    -CurrentCommit $currentCommit `
    -ShortCommit $shortCommit `
    -LastBackedUpCommit $lastBackedUpCommit `
    -BackupRequired $backupRequired `
    -DestinationPath $destinationPath `
    -RobocopyPreview ($robocopyPreview -join " ") `
    -RobocopyExitCode $robocopyExitCode `
    -StateUpdated $true `
    -WritesPerformed 2 `
    -NextSafeAction "Backup complete. Continue only after reviewing PR and state."
$report | ConvertTo-Json -Depth 8
