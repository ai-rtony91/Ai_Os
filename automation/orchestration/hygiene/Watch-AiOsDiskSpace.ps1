[CmdletBinding()]
param(
    [string[]]$Drives = @("C", "D"),
    [decimal]$MinFreeGB = 5.0,
    [int]$NotifyCooldownMin = 60,
    [switch]$Apply,
    [hashtable]$MockFreeGBByDrive = @{},
    [string]$StatePath = "relay/logs/disk_alert_state.json",
    [string]$NotificationScript = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..\..")).Path
$hygieneLog = Join-Path $repoRoot "relay\logs\hygiene.log"
$resolvedStatePath = if ([System.IO.Path]::IsPathRooted($StatePath)) { $StatePath } else { Join-Path $repoRoot $StatePath }
if ([string]::IsNullOrWhiteSpace($NotificationScript)) {
    $NotificationScript = Join-Path $repoRoot "automation\orchestration\notifications\Send-AiOsNotification.ps1"
}

function Write-HygieneLog {
    param([string]$Message)
    $dir = Split-Path -Parent $hygieneLog
    if (-not (Test-Path -LiteralPath $dir -PathType Container)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
    Add-Content -LiteralPath $hygieneLog -Value ("{0} Watch-AiOsDiskSpace {1}" -f (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ"), $Message)
}

function Read-AlertState {
    if (-not (Test-Path -LiteralPath $resolvedStatePath -PathType Leaf)) {
        return [ordered]@{}
    }
    $raw = Get-Content -Raw -LiteralPath $resolvedStatePath
    if ([string]::IsNullOrWhiteSpace($raw)) {
        return [ordered]@{}
    }
    $parsed = $raw | ConvertFrom-Json
    $state = [ordered]@{}
    foreach ($prop in $parsed.PSObject.Properties) {
        $state[$prop.Name] = $prop.Value
    }
    return $state
}

$state = Read-AlertState
$now = (Get-Date).ToUniversalTime()
$results = @()

foreach ($drive in $Drives) {
    $driveName = $drive.TrimEnd(":")
    $freeGB = $null
    if ($MockFreeGBByDrive.ContainsKey($driveName)) {
        $freeGB = [decimal]$MockFreeGBByDrive[$driveName]
    } else {
        $psDrive = Get-PSDrive -Name $driveName -ErrorAction SilentlyContinue
        if ($null -eq $psDrive) {
            $results += [pscustomobject]@{ drive = $driveName; status = "MISSING"; free_gb = $null }
            continue
        }
        $freeGB = [math]::Round(([decimal]$psDrive.Free / 1GB), 2)
    }

    $status = "OK"
    if ($freeGB -lt $MinFreeGB) {
        $last = $null
        if ($state.Contains($driveName)) {
            try { $last = ([datetime]$state[$driveName].last_notified_utc).ToUniversalTime() } catch { $last = $null }
        }
        $cooldownOpen = ($null -ne $last -and $last -gt $now.AddMinutes(-1 * $NotifyCooldownMin))
        if ($cooldownOpen) {
            $status = "SUPPRESSED"
        } else {
            $message = "drive=$driveName free=$freeGB GB"
            if ($Apply) {
                & $NotificationScript -Severity "CRITICAL" -Subject "AI_OS DISK LOW" -Message $message -Apply | Out-Null
            } else {
                & $NotificationScript -Severity "CRITICAL" -Subject "AI_OS DISK LOW" -Message $message -DryNotify | Out-Null
            }
            $state[$driveName] = [ordered]@{
                last_notified_utc = $now.ToString("o")
                free_gb = $freeGB
                min_free_gb = $MinFreeGB
            }
            $status = "NOTIFIED"
        }
    }
    $results += [pscustomobject]@{ drive = $driveName; status = $status; free_gb = $freeGB }
}

$stateDir = Split-Path -Parent $resolvedStatePath
if (-not (Test-Path -LiteralPath $stateDir -PathType Container)) {
    New-Item -ItemType Directory -Path $stateDir -Force | Out-Null
}
Set-Content -LiteralPath $resolvedStatePath -Value (($state | ConvertTo-Json -Depth 6) + "`n") -Encoding UTF8

$summary = [ordered]@{ apply = [bool]$Apply; min_free_gb = $MinFreeGB; results = @($results) }
Write-HygieneLog -Message (($summary | ConvertTo-Json -Compress -Depth 8))
Write-Output ($summary | ConvertTo-Json -Depth 8)
