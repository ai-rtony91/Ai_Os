<#
Local single-instance supervisor pid lock for AI_OS.
This script never schedules tasks, installs services, kills processes, or restarts anything.
Its only powers are reading a lock file, writing a lock file, and removing its own lock file.
#>
[CmdletBinding()]
param(
    [ValidateSet("Acquire", "Release", "Status")][string]$Action = "Acquire",
    [switch]$Apply,
    [string]$LockPath = "control/cycle/supervisor.lock",
    [int]$StaleMinutes = 60
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function New-LockResult {
    param(
        [bool]$Ok,
        [string]$Reason,
        [object]$Holder = $null,
        [object]$AgeMin = $null,
        [object]$Held = $null,
        [bool]$WouldWrite = $false,
        [bool]$WouldRemove = $false
    )

    $result = [ordered]@{
        ok = $Ok
        reason = $Reason
    }
    if ($null -ne $Holder) { $result.holder = $Holder }
    if ($null -ne $AgeMin) { $result.age_min = [math]::Round([double]$AgeMin, 1) }
    if ($null -ne $Held) { $result.held = [bool]$Held }
    if ($WouldWrite) { $result.would_write = $true }
    if ($WouldRemove) { $result.would_remove = $true }
    return [pscustomobject]$result
}

try {
    $repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..\..")).Path
    $resolvedLockPath = if ([System.IO.Path]::IsPathRooted($LockPath)) {
        $LockPath
    } else {
        Join-Path $repoRoot $LockPath
    }
    $resolvedLockPath = [System.IO.Path]::GetFullPath($resolvedLockPath)
    $lockParent = Split-Path -Parent $resolvedLockPath

    function Read-Lock {
        if (-not (Test-Path -LiteralPath $resolvedLockPath -PathType Leaf)) {
            return $null
        }

        try {
            $content = Get-Content -Raw -LiteralPath $resolvedLockPath
            if ([string]::IsNullOrWhiteSpace($content)) {
                return [pscustomobject]@{ corrupt = $true }
            }
            return ($content | ConvertFrom-Json)
        } catch {
            return [pscustomobject]@{ corrupt = $true }
        }
    }

    function Test-PidAlive {
        param([object]$ProcId)

        try {
            $id = [int]$ProcId
            return $null -ne (Get-Process -Id $id -ErrorAction SilentlyContinue)
        } catch {
            return $false
        }
    }

    function Get-LockAgeMinutes {
        param([object]$Lock)

        if ($null -eq $Lock -or -not (Get-Member -InputObject $Lock -Name started_at_utc -MemberType NoteProperty)) {
            return $null
        }

        try {
            return ((Get-Date).ToUniversalTime() - [datetime]$Lock.started_at_utc).TotalMinutes
        } catch {
            return $null
        }
    }

    $lock = Read-Lock
    $ageMin = Get-LockAgeMinutes -Lock $lock

    if ($Action -eq "Status") {
        $holder = if ($null -ne $lock -and (Get-Member -InputObject $lock -Name pid -MemberType NoteProperty)) { $lock.pid } else { $null }
        return (New-LockResult -Ok $true -Reason "STATUS" -Holder $holder -AgeMin $ageMin -Held ([bool]($null -ne $lock)))
    }

    if ($Action -eq "Release") {
        $ownsLock = $false
        if ($null -ne $lock -and (Get-Member -InputObject $lock -Name pid -MemberType NoteProperty)) {
            $ownsLock = ([int]$lock.pid -eq [int]$PID)
        }

        if ($ownsLock) {
            if ($Apply -and (Test-Path -LiteralPath $resolvedLockPath -PathType Leaf)) {
                Remove-Item -LiteralPath $resolvedLockPath -Force
            }
            return (New-LockResult -Ok $true -Reason "RELEASED" -WouldRemove (-not $Apply))
        }

        return (New-LockResult -Ok $true -Reason "NOT_OWNER_OR_ABSENT")
    }

    $reclaimed = $false
    if ($null -ne $lock) {
        $hasPid = (Get-Member -InputObject $lock -Name pid -MemberType NoteProperty)
        $sameOwner = $hasPid -and ([int]$lock.pid -eq [int]$PID)
        $live = $hasPid -and (Test-PidAlive -ProcId $lock.pid)
        $fresh = ($null -ne $ageMin -and $ageMin -lt $StaleMinutes)

        if ($sameOwner -and $fresh) {
            return (New-LockResult -Ok $true -Reason "ACQUIRED" -Holder $PID -AgeMin $ageMin)
        }

        if ($live -and $fresh) {
            return (New-LockResult -Ok $false -Reason "SUPERVISOR_ALREADY_RUNNING" -Holder $lock.pid -AgeMin $ageMin)
        }

        $reclaimed = $true
    }

    $payload = [ordered]@{
        pid = $PID
        host = $env:COMPUTERNAME
        started_at_utc = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    }

    if ($Apply) {
        if (-not (Test-Path -LiteralPath $lockParent -PathType Container)) {
            New-Item -ItemType Directory -Force -Path $lockParent | Out-Null
        }

        $tmpPath = "$resolvedLockPath.tmp"
        $payload | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $tmpPath -Encoding UTF8
        Move-Item -LiteralPath $tmpPath -Destination $resolvedLockPath -Force
    }

    $reason = if ($reclaimed) { "RECLAIMED_STALE" } else { "ACQUIRED" }
    return (New-LockResult -Ok $true -Reason $reason -Holder $PID -WouldWrite (-not $Apply))
} catch {
    return (New-LockResult -Ok $false -Reason "LOCK_ERROR:$($_.Exception.Message)")
}
