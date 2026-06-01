[CmdletBinding()]
param(
    [string]$PolicyPath = "control/mode/AIOS_MODE_POLICY.json",
    [Nullable[int]]$IdleSecOverride = $null,
    [string]$LocalTimeOverride = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..\..")).Path
$resolvedPolicy = if ([System.IO.Path]::IsPathRooted($PolicyPath)) { $PolicyPath } else { Join-Path $repoRoot $PolicyPath }
$modeRoot = Split-Path -Parent $resolvedPolicy
$overridePath = Join-Path $modeRoot "MODE_OVERRIDE.flag"
$logPath = Join-Path $repoRoot "relay\logs\mode.log"

function Test-AiOsTimeWindow {
    param([datetime]$Now, [string]$Start, [string]$End)
    $startParts = $Start.Split(":")
    $endParts = $End.Split(":")
    $startTime = $Now.Date.AddHours([int]$startParts[0]).AddMinutes([int]$startParts[1])
    $endTime = $Now.Date.AddHours([int]$endParts[0]).AddMinutes([int]$endParts[1])
    if ($endTime -le $startTime) {
        return ($Now -ge $startTime -or $Now -lt $endTime)
    }
    return ($Now -ge $startTime -and $Now -lt $endTime)
}

function Get-AiOsIdleSec {
    param([Nullable[int]]$Override)
    if ($null -ne $Override) { return [int]$Override }
    try {
        Add-Type @"
using System;
using System.Runtime.InteropServices;
public static class AiOsIdle {
  [StructLayout(LayoutKind.Sequential)] public struct LASTINPUTINFO { public uint cbSize; public uint dwTime; }
  [DllImport("user32.dll")] public static extern bool GetLastInputInfo(ref LASTINPUTINFO plii);
  [DllImport("kernel32.dll")] public static extern uint GetTickCount();
}
"@ -ErrorAction SilentlyContinue
        $info = New-Object AiOsIdle+LASTINPUTINFO
        $info.cbSize = [System.Runtime.InteropServices.Marshal]::SizeOf($info)
        [void][AiOsIdle]::GetLastInputInfo([ref]$info)
        return [int](([AiOsIdle]::GetTickCount() - $info.dwTime) / 1000)
    } catch {
        return 0
    }
}

try {
    $policy = Get-Content -Raw -LiteralPath $resolvedPolicy | ConvertFrom-Json
    $localNow = if ([string]::IsNullOrWhiteSpace($LocalTimeOverride)) { Get-Date } else { [datetime]$LocalTimeOverride }
    $idleSec = Get-AiOsIdleSec -Override $IdleSecOverride
    $override = if (Test-Path -LiteralPath $overridePath -PathType Leaf) { (Get-Content -Raw -LiteralPath $overridePath).Trim().ToUpperInvariant() } else { "" }

    if ($override -eq "OFF") {
        $mode = "OFF"; $reason = "MODE_OVERRIDE.flag=OFF"
    } elseif ($override -eq "NIGHT") {
        $mode = "NIGHT_AUTOPILOT"; $reason = "OPERATOR_OVERRIDE_NIGHT"
    } elseif ((Test-AiOsTimeWindow -Now $localNow -Start ([string]$policy.night_hours_local.start) -End ([string]$policy.night_hours_local.end)) -and ($idleSec -gt [int]$policy.idle_threshold_sec)) {
        $mode = "NIGHT_AUTOPILOT"; $reason = "NIGHT_HOURS_AND_IDLE"
    } else {
        $mode = "DAY_OBSERVER"; $reason = "DAY_OR_OPERATOR_ACTIVE"
    }
} catch {
    $mode = "DAY_OBSERVER"; $reason = "FAIL_CLOSED:$($_.Exception.Message)"; $idleSec = 0; $localNow = Get-Date
}

$result = [ordered]@{
    mode = $mode
    reason = $reason
    idle_sec = $idleSec
    local_clock = $localNow.ToString("HH:mm:ss")
    checked_at_utc = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
}

$logDir = Split-Path -Parent $logPath
if (-not (Test-Path -LiteralPath $logDir -PathType Container)) { New-Item -ItemType Directory -Path $logDir -Force | Out-Null }
Add-Content -LiteralPath $logPath -Value (($result | ConvertTo-Json -Compress -Depth 5))
return [pscustomobject]$result
