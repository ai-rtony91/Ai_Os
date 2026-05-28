<#
Schema/contract reference: AIOS_POST_MAIN_UPDATE_BACKUP_PLAN.v1
Mode: DRY_RUN
blocked_capabilities:
  - robocopy_execution
  - backup_snapshot_creation
  - state_file_write
  - scheduler_registration
  - repo_mutation
  - git_mutation
  - delete_or_mirror_behavior
next_safe_action: Review the generated RoboCopy preview and approve an exact destination before any backup run.
commit_performed: NO / push_performed: NO
#>

[CmdletBinding()]
param(
    [string]$SourceRepo = "C:\Dev\Ai.Os",
    [string]$BackupRoot = "D:\T9_FOB",
    [string]$StateFilePath = "telemetry\backup_reports\AIOS_POST_MAIN_UPDATE_BACKUP_STATE.json",
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

function New-AiOsPostMainBackupPlan {
    param(
        [Parameter(Mandatory = $true)][string]$Status,
        [Parameter(Mandatory = $true)][string]$CurrentCommit,
        [AllowNull()][string]$LastBackedUpCommit,
        [Parameter(Mandatory = $true)][bool]$BackupRequired,
        [Parameter(Mandatory = $true)][string]$RecommendedBackupPath,
        [Parameter(Mandatory = $true)][string]$RobocopyPreview,
        [Parameter(Mandatory = $true)][string]$NextSafeAction,
        [AllowNull()][string]$StateReadStatus
    )

    return [pscustomobject]@{
        schema = "AIOS_POST_MAIN_UPDATE_BACKUP_PLAN.v1"
        mode = "DRY_RUN"
        status = $Status
        current_commit = $CurrentCommit
        last_backed_up_commit = $LastBackedUpCommit
        backup_required = $BackupRequired
        recommended_backup_path = $RecommendedBackupPath
        robocopy_preview = $RobocopyPreview
        writes_performed = 0
        state_file_path = ConvertTo-AiOsRelativePath -Root $normalizedSource -Path $resolvedStateFilePath
        state_read_status = $StateReadStatus
        excluded_paths = @(".git", ".codex_backups", "node_modules", "__pycache__", ".venv", "dist", "build")
        blocked_capabilities = @(
            "robocopy_execution",
            "backup_snapshot_creation",
            "state_file_write",
            "scheduler_registration",
            "repo_mutation",
            "git_mutation",
            "delete_or_mirror_behavior"
        )
        next_safe_action = $NextSafeAction
        generated_at = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    }
}

$expectedSource = "C:\Dev\Ai.Os"
$expectedBackupRoot = "D:\T9_FOB"
$normalizedSource = ConvertTo-AiOsFullPath -Path $SourceRepo
$normalizedBackupRoot = ConvertTo-AiOsFullPath -Path $BackupRoot

if ($normalizedSource -ne $expectedSource) {
    throw "Source repo must be exactly $expectedSource."
}

if ($normalizedBackupRoot -ne $expectedBackupRoot) {
    throw "Backup root must be exactly $expectedBackupRoot."
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

$currentCommit = (& git -C $normalizedSource rev-parse HEAD 2>&1 | Select-Object -First 1)
if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace([string]$currentCommit)) {
    throw "Unable to read current main commit with git rev-parse HEAD."
}

$currentCommit = [string]$currentCommit
$shortCommit = if ($currentCommit.Length -ge 7) { $currentCommit.Substring(0, 7) } else { $currentCommit }
$state = Read-AiOsBackupState -Path $resolvedStateFilePath
$stateReadStatus = if ($null -eq $state) { "MISSING" } elseif ($state.PSObject.Properties.Name -contains "parse_error") { "PARSE_ERROR" } else { "READ" }
$lastBackedUpCommit = if ($null -ne $state -and $state.PSObject.Properties.Name -contains "last_backed_up_commit") {
    [string]$state.last_backed_up_commit
}
else {
    $null
}

$timestamp = Get-Date -Format "yyyy-MM-dd_HHmm"
$destinationName = "AIOS_BACKUP_POST_MAIN_${timestamp}_$shortCommit"
$recommendedBackupPath = Join-Path $normalizedBackupRoot $destinationName
$excludedDirs = @(".git", ".codex_backups", "node_modules", "__pycache__", ".venv", "dist", "build")
$robocopyPreview = @(
    "robocopy",
    "`"$normalizedSource`"",
    "`"$recommendedBackupPath`"",
    "/E",
    "/XD"
) + ($excludedDirs | ForEach-Object { "`"$_`"" }) + @(
    "/R:2",
    "/W:2",
    "/COPY:DAT",
    "/DCOPY:DAT",
    "/NP",
    "/TEE"
)

$backupRequired = -not ($lastBackedUpCommit -and $lastBackedUpCommit -eq $currentCommit)
$status = if ($backupRequired) { "BACKUP_RECOMMENDED" } else { "SKIP_BACKUP" }
$nextSafeAction = if ($backupRequired) {
    "Approve the exact destination path before running any backup command."
}
else {
    "No backup needed for this commit unless the Human Owner requests a fresh snapshot."
}

$plan = New-AiOsPostMainBackupPlan -Status $status `
    -CurrentCommit $currentCommit `
    -LastBackedUpCommit $lastBackedUpCommit `
    -BackupRequired $backupRequired `
    -RecommendedBackupPath $recommendedBackupPath `
    -RobocopyPreview ($robocopyPreview -join " ") `
    -NextSafeAction $nextSafeAction `
    -StateReadStatus $stateReadStatus

if ($OutputJson) {
    $plan | ConvertTo-Json -Depth 6
}
else {
    $plan | ConvertTo-Json -Depth 6
}
