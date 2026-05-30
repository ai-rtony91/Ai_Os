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

function Get-AiOsRobocopyCounts {
    # Robocopy still prints its summary table under /NFL /NDL. Parse the
    # "Files :" row for Copied and Skipped counts. Columns are:
    # Total Copied Skipped Mismatch FAILED Extras
    param([Parameter(Mandatory = $true)][string[]]$Output)

    $counts = [pscustomobject]@{
        files_copied = -1
        files_skipped = -1
    }

    foreach ($line in $Output) {
        if ($line -match '^\s*Files\s*:\s+(\d+)\s+(\d+)\s+(\d+)') {
            $counts.files_copied = [int]$Matches[2]
            $counts.files_skipped = [int]$Matches[3]
            break
        }
    }

    return $counts
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

    $excludeNames = @("node_modules", "__pycache__", ".pytest_cache", ".codex")

    if ($Preview) {
        $sourceBytes = Get-AiOsDirectorySize -Path $normalizedSource -ExcludeNames $excludeNames
        $destBytes = Get-AiOsDirectorySize -Path $normalizedBackupRoot

        $result = New-AiOsBackupResult -Status "PREVIEW" -Message "Preview only. No folder was created and robocopy was not run."
        $result | Add-Member -NotePropertyName planned_command -NotePropertyValue ($plannedCommand -join " ")
        $result | Add-Member -NotePropertyName source_bytes -NotePropertyValue ([long]$sourceBytes)
        $result | Add-Member -NotePropertyName dest_bytes -NotePropertyValue ([long]$destBytes)
        $result | Add-Member -NotePropertyName source_human -NotePropertyValue (Format-AiOsBytes -Bytes $sourceBytes)
        $result | Add-Member -NotePropertyName dest_human -NotePropertyValue (Format-AiOsBytes -Bytes $destBytes)
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
            Write-Host ""
            Write-Host "Source data measured:        $(Format-AiOsBytes -Bytes $sourceBytes)"
            Write-Host "Current backup size (T9):    $(Format-AiOsBytes -Bytes $destBytes)"
            Write-Host "Copied this run:             pending (preview — robocopy not run)"
            Write-Host "Skipped (already current):   pending (preview — robocopy not run)"
            Write-Host "Produced this backup session: pending (preview — robocopy not run)"
            Write-Host ""
            Write-Host "Planned command:"
            Write-Host ($plannedCommand -join " ")
            Write-Host "No folder was created. Robocopy was not run."
        }
        exit 0
    }

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
        "/XD"
    ) + $excludedDirs

    $robocopyOutput = & robocopy @robocopyArgs 2>&1
    $robocopyExitCode = $LASTEXITCODE
    $robocopyOutput | ForEach-Object { Write-Host $_ }

    $counts = Get-AiOsRobocopyCounts -Output @($robocopyOutput | ForEach-Object { "$_" })
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
    $result | Add-Member -NotePropertyName source_bytes -NotePropertyValue ([long]$sourceBytes)
    $result | Add-Member -NotePropertyName dest_bytes -NotePropertyValue ([long]$destBytesAfter)
    $result | Add-Member -NotePropertyName copied_bytes -NotePropertyValue ([long]$copiedBytes)
    $result | Add-Member -NotePropertyName files_copied -NotePropertyValue ([int]$counts.files_copied)
    $result | Add-Member -NotePropertyName files_skipped -NotePropertyValue ([int]$counts.files_skipped)
    $result | Add-Member -NotePropertyName source_human -NotePropertyValue (Format-AiOsBytes -Bytes $sourceBytes)
    $result | Add-Member -NotePropertyName dest_human -NotePropertyValue (Format-AiOsBytes -Bytes $destBytesAfter)
    $result | Add-Member -NotePropertyName copied_human -NotePropertyValue (Format-AiOsBytes -Bytes $copiedBytes)
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
