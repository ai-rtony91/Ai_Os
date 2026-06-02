<#
.SYNOPSIS
    Dedicated Forex Paper Lab 12-hour report-only loop runner.

.DESCRIPTION
    Reads FOREX_PAPER_LAB_12H_PROFILE.json and runs or previews bounded
    report-only cycles for the Forex Paper Lab. PreviewOnly is the safe default:
    it prints the planned cycle receipts and writes no telemetry/runtime output.

    This runner does not call Invoke-AiOsNightCycle.ps1, ScheduledTask commands,
    git stage/commit/push/merge commands, dashboard/trading runtime files,
    broker/webhook/API/secret paths, or live trading.
#>
[CmdletBinding()]
param(
    [int]$MaxCycles = 12,
    [int]$IntervalSeconds = 3600,
    [string]$OutputRoot = "telemetry/night_supervisor/forex_paper_lab_12h",
    [switch]$PreviewOnly
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = (& git rev-parse --show-toplevel 2>$null | Select-Object -First 1)
if ([string]::IsNullOrWhiteSpace($repoRoot)) {
    throw "Unable to resolve AI_OS repo root."
}
$repoRoot = [string]$repoRoot

$profilePath = "automation/orchestration/night_supervisor/FOREX_PAPER_LAB_12H_PROFILE.json"
$profileFullPath = Join-Path -Path $repoRoot -ChildPath $profilePath
$stopMarkerPaths = @("control/self_continuation/STOP", "relay/STOP.flag")
$blockedPathPrefixes = @(
    "apps/",
    "apps/dashboard/",
    "apps/trading_lab/",
    "broker/",
    "webhooks/",
    ".env",
    "AGENTS.md",
    "README.md",
    "WHITEPAPER.md",
    "docs/governance/",
    "docs/architecture/"
)

function Normalize-AiOsPath {
    param([Parameter(Mandatory = $true)][string]$Path)
    return ($Path -replace "\\", "/").Trim()
}

function Get-AiOsStopMarkers {
    $markers = @()
    foreach ($relativePath in $stopMarkerPaths) {
        $fullPath = Join-Path -Path $repoRoot -ChildPath $relativePath
        $markers += [ordered]@{
            path = $relativePath
            exists = [bool](Test-Path -LiteralPath $fullPath)
        }
    }
    return $markers
}

function Assert-AiOsStopMarkersClear {
    param([Parameter(Mandatory = $true)][string]$Phase)
    $markers = @(Get-AiOsStopMarkers)
    $active = @($markers | Where-Object { $_.exists })
    if ($active.Count -gt 0) {
        $paths = ($active | ForEach-Object { $_.path }) -join ", "
        throw "STOP marker active during ${Phase}: $paths"
    }
    return $markers
}

function Get-AiOsGitStatusPaths {
    $lines = @(& git -C $repoRoot status --porcelain 2>$null | ForEach-Object { [string]$_ })
    $paths = @()
    foreach ($line in $lines) {
        if ([string]::IsNullOrWhiteSpace($line) -or $line.Length -lt 4) {
            continue
        }
        $paths += Normalize-AiOsPath -Path ($line.Substring(3))
    }
    return $paths
}

function Assert-AiOsRepoSafeForCycle {
    param([Parameter(Mandatory = $true)][string]$OutputRoot)

    $normalizedOutputRoot = (Normalize-AiOsPath -Path $OutputRoot).TrimEnd("/") + "/"
    $changedPaths = @(Get-AiOsGitStatusPaths)
    $outsideOutputRoot = @()
    $blockedPaths = @()

    foreach ($path in $changedPaths) {
        $normalized = Normalize-AiOsPath -Path $path
        if (-not $normalized.StartsWith($normalizedOutputRoot)) {
            $outsideOutputRoot += $normalized
        }
        foreach ($blockedPrefix in $blockedPathPrefixes) {
            if ($normalized -eq $blockedPrefix.TrimEnd("/") -or $normalized.StartsWith($blockedPrefix)) {
                $blockedPaths += $normalized
            }
        }
    }

    if ($blockedPaths.Count -gt 0) {
        throw "Blocked path changed: $(($blockedPaths | Sort-Object -Unique) -join ', ')"
    }
    if ($outsideOutputRoot.Count -gt 0) {
        throw "Repo dirty outside approved OutputRoot: $(($outsideOutputRoot | Sort-Object -Unique) -join ', ')"
    }

    return $changedPaths
}

function Assert-AiOsProfileSafe {
    param([Parameter(Mandatory = $true)]$Profile)

    if ($Profile.mode -ne "REPORT_ONLY") {
        throw "Profile mode must be REPORT_ONLY."
    }
    if ([int]$Profile.max_hours -ne 12) {
        throw "Profile max_hours must be 12."
    }
    if ([int]$Profile.interval_minutes -ne 60) {
        throw "Profile interval_minutes must be 60."
    }
    if (-not [bool]$Profile.stop_marker_required) {
        throw "Profile must require STOP marker support."
    }
    if (-not [bool]$Profile.preflight_stop_marker_check) {
        throw "Profile must require preflight STOP marker checks."
    }
}

if (-not (Test-Path -LiteralPath $profileFullPath)) {
    throw "Missing profile: $profilePath"
}

if ($MaxCycles -lt 1) {
    throw "MaxCycles must be at least 1."
}
if ($MaxCycles -gt 12) {
    throw "MaxCycles greater than 12 is refused."
}
if ($IntervalSeconds -lt 60 -and -not $PreviewOnly) {
    throw "IntervalSeconds less than 60 is refused unless -PreviewOnly is used."
}

$profile = Get-Content -Raw -LiteralPath $profileFullPath | ConvertFrom-Json
Assert-AiOsProfileSafe -Profile $profile

$initialMarkers = @(Assert-AiOsStopMarkersClear -Phase "preflight")
if (-not $PreviewOnly) {
    $null = Assert-AiOsRepoSafeForCycle -OutputRoot $OutputRoot
}

$branch = (& git -C $repoRoot rev-parse --abbrev-ref HEAD 2>$null)
$headSha = (& git -C $repoRoot rev-parse --short HEAD 2>$null)
$cycleReceipts = @()
$utcStamp = (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ")
$runOutputRoot = (Normalize-AiOsPath -Path (Join-Path -Path $OutputRoot -ChildPath $utcStamp))

for ($cycle = 1; $cycle -le $MaxCycles; $cycle++) {
    $markers = @(Assert-AiOsStopMarkersClear -Phase "cycle_$cycle")
    $dirtyPaths = if ($PreviewOnly) { @(Get-AiOsGitStatusPaths) } else { @(Assert-AiOsRepoSafeForCycle -OutputRoot $OutputRoot) }
    $hourPlan = @($profile.hourly_plan | Where-Object { [int]$_.hour -eq $cycle } | Select-Object -First 1)

    $cycleReceipts += [ordered]@{
        cycle = $cycle
        focus = if ($hourPlan.Count -gt 0) { [string]$hourPlan[0].focus } else { "profile cycle $cycle" }
        status = if ($PreviewOnly) { "PREVIEW_NOT_WRITTEN" } else { "REPORT_ONLY_READY_TO_WRITE" }
        stop_markers_active = @($markers | Where-Object { $_.exists }).Count
        repo_status_paths_seen = $dirtyPaths.Count
        output_path = "$runOutputRoot/cycle_$('{0:d2}' -f $cycle).json"
    }

    if (-not $PreviewOnly -and $cycle -lt $MaxCycles) {
        Start-Sleep -Seconds $IntervalSeconds
    }
}

Write-Host "REPORT_ONLY_LOOP_READY"
Write-Host "EDUCATIONAL_USE_ONLY"
Write-Host "PAPER_TRADING_SIMULATION_ONLY"
Write-Host "LIVE_TRADING_BLOCKED"
Write-Host "OLD_NIGHT_CYCLE_NOT_USED"
Write-Host "SCHEDULER_NOT_CHANGED"
Write-Host "NO_AUTO_COMMIT_PUSH_MERGE"
Write-Host ("OutputRoot: {0}" -f $OutputRoot)
Write-Host ("Planned cycle count: {0}" -f $MaxCycles)
Write-Host ("PreviewOnly: {0}" -f ([bool]$PreviewOnly))
Write-Host ("Branch: {0}  Head: {1}" -f $branch, $headSha)
Write-Host "Stop condition summary:"
Write-Host "  - STOP markers checked before start and before every cycle."
Write-Host "  - Refuse dirty repo outside OutputRoot during non-preview report-only runs."
Write-Host "  - Refuse blocked path changes."
Write-Host "  - Refuse MaxCycles greater than 12."
Write-Host "  - Refuse IntervalSeconds less than 60 unless PreviewOnly."
Write-Host "  - No old Night Cycle, scheduler, git protected action, broker, webhook, API, secret, dashboard, or trading runtime action."
Write-Host "Initial STOP marker check:"
foreach ($marker in $initialMarkers) {
    Write-Host ("  {0}: {1}" -f $marker.path, ($(if ($marker.exists) { "ACTIVE" } else { "clear" })))
}
Write-Host "Cycle preview:"
foreach ($receipt in $cycleReceipts) {
    Write-Host ("  Cycle {0,2}: {1} [{2}] -> {3}" -f $receipt.cycle, $receipt.focus, $receipt.status, $receipt.output_path)
}
Write-Host "NIGHT_SUPERVISOR_REAL_SESSION_NOT_STARTED"
Write-Host "NO_TELEMETRY_RUNTIME_WRITTEN_IN_PREVIEW"
