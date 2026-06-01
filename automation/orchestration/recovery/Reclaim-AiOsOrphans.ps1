<#
AI_OS crash watchdog for orphaned relay task files.
This script only moves task files between relay subfolders. It never deletes task
content, executes packets, calls provider CLIs, registers tasks, or touches paths
outside relay/.
#>
[CmdletBinding()]
param(
    [switch]$Apply,
    [int]$OrphanMinutes = 30,
    [int]$MaxRetries = 3,
    [string]$RunningDir = "relay/running",
    [string]$InboxDir = "relay/inbox",
    [string]$ErrorDir = "relay/error"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-AiOsUtc {
    return (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
}

function Resolve-AiOsPath {
    param(
        [Parameter(Mandatory = $true)][string]$RepoRoot,
        [Parameter(Mandatory = $true)][string]$Path
    )

    if ([System.IO.Path]::IsPathRooted($Path)) {
        return [System.IO.Path]::GetFullPath($Path)
    }
    return [System.IO.Path]::GetFullPath((Join-Path $RepoRoot $Path))
}

function ConvertTo-AiOsRelative {
    param(
        [Parameter(Mandatory = $true)][string]$RepoRoot,
        [Parameter(Mandatory = $true)][string]$Path
    )

    $rootFull = [System.IO.Path]::GetFullPath($RepoRoot).TrimEnd("\", "/")
    $pathFull = [System.IO.Path]::GetFullPath($Path)
    $rootUri = [System.Uri]::new($rootFull + [System.IO.Path]::DirectorySeparatorChar)
    $pathUri = [System.Uri]::new($pathFull)
    return [System.Uri]::UnescapeDataString($rootUri.MakeRelativeUri($pathUri).ToString()).Replace("/", "\")
}

function Add-AiOsLogLine {
    param(
        [Parameter(Mandatory = $true)][string]$LogPath,
        [Parameter(Mandatory = $true)][string]$Line,
        [bool]$ShouldWrite
    )

    if (-not $ShouldWrite) {
        Write-Host $Line
        return
    }

    $parent = Split-Path -Parent $LogPath
    if (-not (Test-Path -LiteralPath $parent -PathType Container)) {
        New-Item -ItemType Directory -Path $parent -Force | Out-Null
    }
    Add-Content -LiteralPath $LogPath -Value $Line -Encoding UTF8
    Write-Host $Line
}

function Test-AiOsRelayPath {
    param(
        [Parameter(Mandatory = $true)][string]$RepoRoot,
        [Parameter(Mandatory = $true)][string]$Path
    )

    $full = [System.IO.Path]::GetFullPath($Path)
    $relayRoot = [System.IO.Path]::GetFullPath((Join-Path $RepoRoot "relay")).TrimEnd("\", "/")
    return $full.StartsWith($relayRoot + [System.IO.Path]::DirectorySeparatorChar, [System.StringComparison]::OrdinalIgnoreCase)
}

function Move-AiOsTaskContent {
    param(
        [Parameter(Mandatory = $true)][object]$Payload,
        [Parameter(Mandatory = $true)][string]$SourcePath,
        [Parameter(Mandatory = $true)][string]$DestinationPath,
        [bool]$ShouldWrite
    )

    if (-not $ShouldWrite) {
        return
    }

    $destParent = Split-Path -Parent $DestinationPath
    if (-not (Test-Path -LiteralPath $destParent -PathType Container)) {
        New-Item -ItemType Directory -Path $destParent -Force | Out-Null
    }

    $tmpPath = "{0}.tmp" -f $DestinationPath
    $Payload | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath $tmpPath -Encoding UTF8
    Move-Item -LiteralPath $tmpPath -Destination $DestinationPath -Force
    Remove-Item -LiteralPath $SourcePath -Force
}

$summary = [ordered]@{
    scanned = 0
    reclaimed = 0
    errored = 0
    dry_run = -not [bool]$Apply
    actions = @()
}

try {
    $repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..\..")).Path
    $runningPath = Resolve-AiOsPath -RepoRoot $repoRoot -Path $RunningDir
    $inboxPath = Resolve-AiOsPath -RepoRoot $repoRoot -Path $InboxDir
    $errorPath = Resolve-AiOsPath -RepoRoot $repoRoot -Path $ErrorDir
    $logPath = Join-Path $repoRoot "relay\logs\hygiene.log"

    foreach ($path in @($runningPath, $inboxPath, $errorPath, $logPath)) {
        if (-not (Test-AiOsRelayPath -RepoRoot $repoRoot -Path $path)) {
            throw "Path resolves outside relay/: $path"
        }
    }

    $cutoff = (Get-Date).AddMinutes(-1 * $OrphanMinutes)
    $orphans = @()
    if (Test-Path -LiteralPath $runningPath -PathType Container) {
        $orphans = @(Get-ChildItem -LiteralPath $runningPath -Filter "*.task.json" -File -ErrorAction SilentlyContinue | Where-Object {
            $_.LastWriteTime -lt $cutoff
        })
    }

    $summary.scanned = $orphans.Count
    if ($orphans.Count -eq 0) {
        $line = "{0} NO_ORPHANS scanned=0 reclaimed=0 errored=0" -f (Get-AiOsUtc)
        Add-AiOsLogLine -LogPath $logPath -Line $line -ShouldWrite ([bool]$Apply)
        return [pscustomobject]$summary
    }

    foreach ($orphan in $orphans) {
        $id = [System.IO.Path]::GetFileNameWithoutExtension([System.IO.Path]::GetFileNameWithoutExtension($orphan.Name))
        try {
            $raw = Get-Content -Raw -LiteralPath $orphan.FullName
            try {
                $task = $raw | ConvertFrom-Json
            } catch {
                $task = [ordered]@{
                    id = $id
                    reclaim_reason = "ORPHAN_UNREADABLE"
                    original_filename = $orphan.Name
                    raw_content = $raw
                    reclaimed_at_utc = Get-AiOsUtc
                }
                $dest = Join-Path $errorPath $orphan.Name
                $summary.errored++
                $action = "{0} -> relay/error (reason=ORPHAN_UNREADABLE)" -f $id
                $summary.actions += $action
                Write-Host $action
                Move-AiOsTaskContent -Payload $task -SourcePath $orphan.FullName -DestinationPath $dest -ShouldWrite ([bool]$Apply)
                continue
            }

            if ($task.PSObject.Properties.Name -contains "id" -and -not [string]::IsNullOrWhiteSpace([string]$task.id)) {
                $id = [string]$task.id
            }

            $count = 0
            if ($task.PSObject.Properties.Name -contains "reclaim_count" -and $null -ne $task.reclaim_count) {
                $count = [int]$task.reclaim_count
            }

            if ($count -ge $MaxRetries) {
                $task | Add-Member -NotePropertyName "reclaim_reason" -NotePropertyValue "ORPHAN_MAX_RETRIES" -Force
                $task | Add-Member -NotePropertyName "reclaimed_at_utc" -NotePropertyValue (Get-AiOsUtc) -Force
                $dest = Join-Path $errorPath $orphan.Name
                $summary.errored++
                $action = "{0} -> relay/error (reason=ORPHAN_MAX_RETRIES count={1})" -f $id, $count
            } else {
                $newCount = $count + 1
                $task | Add-Member -NotePropertyName "reclaim_count" -NotePropertyValue $newCount -Force
                $task | Add-Member -NotePropertyName "reclaimed_at_utc" -NotePropertyValue (Get-AiOsUtc) -Force
                $dest = Join-Path $inboxPath $orphan.Name
                $summary.reclaimed++
                $action = "{0} -> relay/inbox (count={1})" -f $id, $newCount
            }

            $summary.actions += $action
            Write-Host $action
            Move-AiOsTaskContent -Payload $task -SourcePath $orphan.FullName -DestinationPath $dest -ShouldWrite ([bool]$Apply)
        } catch {
            $summary.errored++
            $line = "{0} ORPHAN_SWEEP_FILE_ERROR file={1} error={2}" -f (Get-AiOsUtc), $orphan.Name, $_.Exception.Message
            Add-AiOsLogLine -LogPath $logPath -Line $line -ShouldWrite ([bool]$Apply)
        }
    }

    $summaryLine = "{0} ORPHAN_SWEEP reclaimed={1} errored={2} scanned={3}" -f (Get-AiOsUtc), $summary.reclaimed, $summary.errored, $summary.scanned
    Add-AiOsLogLine -LogPath $logPath -Line $summaryLine -ShouldWrite ([bool]$Apply)
    return [pscustomobject]$summary
} catch {
    $summary.actions += ("FATAL {0}" -f $_.Exception.Message)
    Write-Host ("ORPHAN_SWEEP_FATAL {0}" -f $_.Exception.Message)
    return [pscustomobject]$summary
}
