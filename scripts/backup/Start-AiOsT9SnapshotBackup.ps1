[CmdletBinding()]
param(
    [string]$SourceRepo = "C:\Dev\Ai.Os",
    [string]$BackupRoot = "D:\T9_FOB",
    [switch]$Preview,
    [switch]$OutputJson
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function ConvertTo-AiOsFullPath {
    param([Parameter(Mandatory = $true)][string]$Path)

    return [System.IO.Path]::GetFullPath($Path).TrimEnd("\")
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
        runtime_mutation = "NO"
        generated_at = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    }
}

$expectedSource = "C:\Dev\Ai.Os"
$expectedBackupRoot = "D:\T9_FOB"
$normalizedSource = ConvertTo-AiOsFullPath -Path $SourceRepo
$normalizedBackupRoot = ConvertTo-AiOsFullPath -Path $BackupRoot
$timestamp = Get-Date -Format "yyyy-MM-dd_HHmm"
$snapshotName = "AIOS_BACKUP_$timestamp"
$snapshotPath = Join-Path $normalizedBackupRoot $snapshotName
$excludedDirs = @(
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".codex",
    (Join-Path $normalizedSource ".git\logs")
)

try {
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
        "/XD"
    ) + ($excludedDirs | ForEach-Object { "`"$_`"" })

    if ($Preview) {
        $result = New-AiOsBackupResult -Status "PREVIEW" -Message "Preview only. No folder was created and robocopy was not run."
        $result | Add-Member -NotePropertyName planned_command -NotePropertyValue ($plannedCommand -join " ")
        if ($OutputJson) {
            $result | ConvertTo-Json -Depth 6
        }
        else {
            Write-Host "AI_OS T9 Snapshot Backup Preview"
            Write-Host "Source: $normalizedSource"
            Write-Host "Backup root: $normalizedBackupRoot"
            Write-Host "Snapshot path: $snapshotPath"
            Write-Host "Excluded paths:"
            $excludedDirs | ForEach-Object { Write-Host "  - $_" }
            Write-Host "Planned command:"
            Write-Host ($plannedCommand -join " ")
            Write-Host "No folder was created. Robocopy was not run."
        }
        exit 0
    }

    New-Item -ItemType Directory -Path $snapshotPath | Out-Null

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
        "/XD"
    ) + $excludedDirs

    & robocopy @robocopyArgs
    $robocopyExitCode = $LASTEXITCODE

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

    if ($robocopyExitCode -ge 8) {
        $result = New-AiOsBackupResult -Status "FAILED" -Message "Robocopy reported a failure." -RobocopyExitCode $robocopyExitCode -ExitCode $robocopyExitCode
        $result | ConvertTo-Json -Depth 6
        exit $robocopyExitCode
    }

    if ($missingPaths.Count -gt 0) {
        $result = New-AiOsBackupResult -Status "FAILED" -Message "Snapshot verification failed. Missing expected paths: $($missingPaths -join ', ')." -RobocopyExitCode $robocopyExitCode -ExitCode 9
        $result | ConvertTo-Json -Depth 6
        exit 9
    }

    $result = New-AiOsBackupResult -Status "SUCCESS" -Message "Backup snapshot created and verified." -RobocopyExitCode $robocopyExitCode
    if ($OutputJson) {
        $result | ConvertTo-Json -Depth 6
    }
    else {
        Write-Host "AI_OS T9 Snapshot Backup"
        Write-Host "Status: SUCCESS"
        Write-Host "Snapshot path: $snapshotPath"
        Write-Host "Robocopy exit code: $robocopyExitCode"
        Write-Host "Active repo mutation: NO"
        Write-Host "Scheduler behavior: NO"
        Write-Host "Runtime mutation: NO"
    }
    exit 0
}
catch {
    $result = New-AiOsBackupResult -Status "FAILED" -Message $_.Exception.Message -ExitCode 1
    $result | ConvertTo-Json -Depth 6
    exit 1
}
