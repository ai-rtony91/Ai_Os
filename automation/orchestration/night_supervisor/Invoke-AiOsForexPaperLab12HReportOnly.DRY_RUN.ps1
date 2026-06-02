<#
.SYNOPSIS
    AI_OS Forex Paper Lab 12-hour Night Supervisor report-only wrapper.

.DESCRIPTION
    Reads FOREX_PAPER_LAB_12H_PROFILE.json and emits a DRY_RUN execution plan.
    This wrapper does not start Night Supervisor, run the night cycle, change
    scheduled tasks, write telemetry, mutate repo state, stage, commit, push,
    merge, launch workers, touch broker/webhook/API/secret paths, or enable live
    trading.

    Each planned hour includes an explicit STOP marker preflight check. If a
    STOP marker is present, the wrapper reports BLOCKED and plans no work.

.PARAMETER QuietJson
    Emit only JSON.
#>
[CmdletBinding()]
param(
    [string]$RepoRoot = "",
    [switch]$QuietJson
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$schema = "AIOS_FOREX_PAPER_LAB_12H_REPORT_ONLY_PLAN.v1"
$profilePath = "automation/orchestration/night_supervisor/FOREX_PAPER_LAB_12H_PROFILE.json"
$stopMarkerPaths = @(
    "control/self_continuation/STOP",
    "relay/STOP.flag"
)

function Resolve-AiOsRepoRoot {
    param([AllowEmptyString()][string]$RequestedRoot)

    if (-not [string]::IsNullOrWhiteSpace($RequestedRoot)) {
        return (Resolve-Path -LiteralPath $RequestedRoot -ErrorAction Stop).ProviderPath
    }

    $gitOutput = & git rev-parse --show-toplevel 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Unable to resolve AI_OS repo root. Run inside the repo or pass -RepoRoot."
    }
    return [string]($gitOutput | Select-Object -First 1)
}

function Get-RelativePathState {
    param(
        [Parameter(Mandatory = $true)][string]$Root,
        [Parameter(Mandatory = $true)][string[]]$RelativePaths
    )

    $items = @()
    foreach ($relativePath in $RelativePaths) {
        $literalPath = Join-Path -Path $Root -ChildPath $relativePath
        $items += [ordered]@{
            path = $relativePath
            exists = [bool](Test-Path -LiteralPath $literalPath)
        }
    }
    return $items
}

function Assert-ProfileSafety {
    param([Parameter(Mandatory = $true)]$Profile)

    $failures = @()
    if ($Profile.mode -ne "REPORT_ONLY") {
        $failures += "Profile mode must be REPORT_ONLY."
    }
    if ([int]$Profile.max_hours -ne 12) {
        $failures += "Profile max_hours must be 12."
    }
    if ([int]$Profile.interval_minutes -ne 60) {
        $failures += "Profile interval_minutes must be 60."
    }
    if (-not [bool]$Profile.stop_marker_required) {
        $failures += "Profile must require STOP marker support."
    }
    if (-not [bool]$Profile.preflight_stop_marker_check) {
        $failures += "Profile must require preflight STOP marker checks."
    }

    $safety = $Profile.safety_boundary
    $requiredTrueFlags = @(
        "educational_use_only",
        "paper_trading_simulation_only",
        "report_only_by_default",
        "no_live_trading",
        "no_broker_apis",
        "no_oanda",
        "no_webhooks",
        "no_real_market_data",
        "no_real_orders",
        "no_api_keys_or_secrets",
        "no_automatic_commit",
        "no_automatic_push",
        "no_automatic_merge",
        "no_dashboard_theme_css_layout_changes",
        "no_base44_code_or_style_import"
    )

    foreach ($flag in $requiredTrueFlags) {
        if (-not [bool]$safety.$flag) {
            $failures += "Profile safety flag must be true: $flag"
        }
    }

    return $failures
}

$RepoRoot = Resolve-AiOsRepoRoot -RequestedRoot $RepoRoot
$resolvedProfilePath = Join-Path -Path $RepoRoot -ChildPath $profilePath
if (-not (Test-Path -LiteralPath $resolvedProfilePath)) {
    throw "Missing required profile: $profilePath"
}

$profile = Get-Content -Raw -LiteralPath $resolvedProfilePath | ConvertFrom-Json
$profileFailures = @(Assert-ProfileSafety -Profile $profile)
$stopMarkerState = @(Get-RelativePathState -Root $RepoRoot -RelativePaths $stopMarkerPaths)
$activeStopMarkers = @($stopMarkerState | Where-Object { $_.exists })

$branch = (& git -C $RepoRoot rev-parse --abbrev-ref HEAD 2>$null)
$headSha = (& git -C $RepoRoot rev-parse --short HEAD 2>$null)
$statusLines = @(& git -C $RepoRoot status --porcelain 2>$null | ForEach-Object { [string]$_ })

$isSafe = ($profileFailures.Count -eq 0 -and $activeStopMarkers.Count -eq 0)
$status = if ($isSafe) { "READY_REPORT_ONLY" } else { "BLOCKED" }
$nextSafeAction = if ($isSafe) {
    "Review this report-only plan. A separate approved packet is required before any run, output write, scheduler change, commit, push, or merge."
} else {
    "Stop. Resolve profile validation failures or active STOP markers before planning any future run."
}

$cycles = @()
foreach ($item in $profile.hourly_plan) {
    $cycles += [ordered]@{
        hour = [int]$item.hour
        focus = [string]$item.focus
        interval_minutes = [int]$profile.interval_minutes
        preflight_stop_marker_check = $true
        planned_action = "REPORT_ONLY_GAP_PLANNING"
        status = if ($isSafe) { "PLANNED_NOT_RUN" } else { "BLOCKED_NOT_RUN" }
        writes = @()
        forbidden_actions = $profile.blocked_work
    }
}

$report = [ordered]@{
    schema = $schema
    mode = "DRY_RUN"
    wrapper_status = $status
    generated_at = (Get-Date).ToString("s")
    repo = [ordered]@{
        repo_root = $RepoRoot
        branch = [string]$branch
        head_sha = [string]$headSha
        dirty_or_untracked_count = $statusLines.Count
    }
    profile = [ordered]@{
        path = $profilePath
        profile_id = [string]$profile.profile_id
        mode = [string]$profile.mode
        max_hours = [int]$profile.max_hours
        interval_minutes = [int]$profile.interval_minutes
        source_plan = [string]$profile.source_plan
        principle = [string]$profile.principle
    }
    stop_marker_check = [ordered]@{
        required = [bool]$profile.stop_marker_required
        preflight_check_before_each_cycle = [bool]$profile.preflight_stop_marker_check
        markers = $stopMarkerState
        active_stop_marker_count = $activeStopMarkers.Count
    }
    safety_boundary = $profile.safety_boundary
    allowed_work = $profile.allowed_work
    blocked_work = $profile.blocked_work
    profile_validation_failures = $profileFailures
    planned_cycles = $cycles
    output_behavior = [ordered]@{
        stdout_only = $true
        writes_runtime_outputs = $false
        writes_telemetry = $false
        mutates_repo = $false
        starts_night_supervisor = $false
        changes_scheduler = $false
    }
    safety_confirmation = [ordered]@{
        educational_use_only = $true
        paper_trading_simulation_only = $true
        no_live_trading = $true
        no_broker_apis = $true
        no_oanda = $true
        no_webhooks = $true
        no_real_market_data = $true
        no_real_orders = $true
        no_api_keys_or_secrets = $true
        no_dashboard_theme_css_layout_changes = $true
        no_base44_code_or_style_import = $true
        no_commit_push_merge = $true
        no_scheduler_change = $true
    }
    next_safe_action = $nextSafeAction
}

if ($QuietJson) {
    $report | ConvertTo-Json -Depth 16
    exit 0
}

Write-Host "AI_OS Forex Paper Lab 12H Report-Only Plan"
Write-Host ("Status: {0}" -f $report.wrapper_status)
Write-Host ("Profile: {0}" -f $report.profile.path)
Write-Host ("Branch: {0}  Head: {1}" -f $branch, $headSha)
Write-Host ("STOP markers active: {0}" -f $activeStopMarkers.Count)
Write-Host ""
foreach ($cycle in $cycles) {
    Write-Host ("  Hour {0,2}: {1} [{2}]" -f $cycle.hour, $cycle.focus, $cycle.status)
}
Write-Host ""
Write-Host "No Night Supervisor run started."
Write-Host "No scheduler change performed."
Write-Host "No repo/runtime/telemetry output written."
Write-Host ("Next safe action: {0}" -f $nextSafeAction)
