<#
.SYNOPSIS
Runs one gated AI_OS night cycle.

.DESCRIPTION
This orchestrator wires the relay runner, approval resume consumer,
self-continuation controller, autonomy bridge, and SOS notifier into one local
cycle. Default mode is DRY_RUN and must not mutate relay state. With -Apply,
the flag is passed only to child steps that already support APPLY gates.

Hard limits: this script never runs git, schtasks, Register-ScheduledTask,
New-Service, sc.exe, secret readers, broker execution, OANDA, or live trading.
#>

[CmdletBinding()]
param(
    [switch]$Apply,
    [switch]$Watch,
    [switch]$MorningBrief = $true,
    [string]$ResumeFrom = "",
    [ValidateRange(5, 86400)]
    [int]$IntervalSeconds = 300
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..")).Path
$relayRoot = Join-Path $repoRoot "relay"
$logPath = Join-Path $relayRoot "logs\night_cycle.log"
$cycleMarkerPath = Join-Path $repoRoot "control\cycle\last_marker.json"
$script:AiOsNextIntervalSeconds = $IntervalSeconds
$script:AiOsCycleId = [guid]::NewGuid().ToString()
$script:AiOsResumeActive = [string]::IsNullOrWhiteSpace($ResumeFrom)
$script:AiOsPhaseNames = @(
    "hygiene",
    "clear-stale-approvals",
    "pull-backlog",
    "relay-runner",
    "approval-resume",
    "relay-runner-resume-drain",
    "self-continuation",
    "night-supervisor",
    "autonomy-bridge",
    "morning-brief",
    "sos-file-notifier",
    "pr-watch"
)

function Get-AiOsUtc {
    return (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
}

function Write-AiOsNightCycleLog {
    param([Parameter(Mandatory = $true)][string]$Message)

    $line = "{0} {1}" -f (Get-AiOsUtc), $Message
    if ($Apply) {
        $logDir = Split-Path -Parent $logPath
        if (-not (Test-Path -LiteralPath $logDir -PathType Container)) {
            New-Item -ItemType Directory -Path $logDir -Force | Out-Null
        }
        Add-Content -LiteralPath $logPath -Value $line
    }
    Write-Host $line
}

function Read-CycleMarker {
    if (-not (Test-Path -LiteralPath $cycleMarkerPath -PathType Leaf)) {
        return $null
    }
    try {
        return Get-Content -Raw -LiteralPath $cycleMarkerPath | ConvertFrom-Json
    } catch {
        return $null
    }
}

function Write-CycleMarker {
    param(
        [string]$Phase = "",
        [Parameter(Mandatory = $true)][ValidateSet("STARTED", "COMPLETE", "CYCLE_COMPLETE")]
        [string]$State
    )

    $existing = Read-CycleMarker
    $completed = @()
    if ($State -eq "STARTED" -and ($null -eq $existing -or [string]$existing.cycle_id -ne $script:AiOsCycleId)) {
        $completed = @()
    } elseif ($null -ne $existing -and $null -ne $existing.completed_phases) {
        $completed = @($existing.completed_phases | ForEach-Object { [string]$_ })
    }
    if ($State -eq "COMPLETE" -and -not [string]::IsNullOrWhiteSpace($Phase) -and $completed -notcontains $Phase) {
        $completed += $Phase
    }

    $marker = [ordered]@{
        cycle_id = $script:AiOsCycleId
        cycle_in_progress = ($State -ne "CYCLE_COMPLETE")
        phase_name = $Phase
        phase_state = $State
        started_at = if ($State -eq "STARTED") { Get-AiOsUtc } elseif ($null -ne $existing -and $null -ne $existing.started_at) { [string]$existing.started_at } else { "" }
        updated_at_utc = Get-AiOsUtc
        apply = [bool]$Apply
        resume_from = $ResumeFrom
        phases = @($script:AiOsPhaseNames | ForEach-Object { [ordered]@{ name = $_ } })
        completed_phases = @($completed)
    }

    $markerDir = Split-Path -Parent $cycleMarkerPath
    if (-not (Test-Path -LiteralPath $markerDir -PathType Container)) {
        New-Item -ItemType Directory -Path $markerDir -Force | Out-Null
    }
    $tmpPath = $cycleMarkerPath + ".tmp"
    Set-Content -LiteralPath $tmpPath -Value (($marker | ConvertTo-Json -Depth 10) + "`n") -Encoding UTF8
    Move-Item -LiteralPath $tmpPath -Destination $cycleMarkerPath -Force
}

function Update-AiOsDashboardState {
    $dashboardState = Join-Path $repoRoot "automation\orchestration\dashboard\Update-AiOsDashboardState.ps1"
    if (Test-Path -LiteralPath $dashboardState -PathType Leaf) {
        & $dashboardState | Out-Null
    }
}

function Test-AiOsResumeSkip {
    param([string]$Name)
    if ($script:AiOsResumeActive) {
        return $false
    }
    if ($Name -eq $ResumeFrom) {
        $script:AiOsResumeActive = $true
        return $false
    }
    Write-AiOsNightCycleLog -Message ("RESUME SKIP phase={0} waiting_for={1}" -f $Name, $ResumeFrom)
    return $true
}

function Complete-AiOsSkippedPhase {
    param(
        [int]$Number,
        [string]$Name,
        [string]$Reason
    )
    if (Test-AiOsResumeSkip -Name $Name) {
        return
    }
    Write-CycleMarker -Phase $Name -State "STARTED"
    Write-AiOsNightCycleLog -Message ("STEP {0} SKIP {1} {2}" -f $Number, $Name, $Reason)
    Write-CycleMarker -Phase $Name -State "COMPLETE"
    Update-AiOsDashboardState
}

function Invoke-AiOsStep {
    param(
        [Parameter(Mandatory = $true)][int]$Number,
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][string]$Command,
        [string[]]$Arguments = @()
    )

    if (Test-AiOsResumeSkip -Name $Name) {
        return
    }

    Write-CycleMarker -Phase $Name -State "STARTED"
    Write-AiOsNightCycleLog -Message ("STEP {0} START {1}" -f $Number, $Name)
    & $Command @Arguments
    $exit = if ($null -ne $LASTEXITCODE) { [int]$LASTEXITCODE } else { 0 }
    if ($exit -ne 0) {
        Write-AiOsNightCycleLog -Message ("STEP {0} FAIL {1} exit={2}" -f $Number, $Name, $exit)
        throw "Night cycle step failed: $Name exit=$exit"
    }
    Write-AiOsNightCycleLog -Message ("STEP {0} PASS {1}" -f $Number, $Name)
    Write-CycleMarker -Phase $Name -State "COMPLETE"
    Update-AiOsDashboardState
}

function Invoke-AiOsNightCycleOnce {
    $ps = (Get-Command powershell -ErrorAction Stop).Source
    $rotateLogs = Join-Path $repoRoot "automation\orchestration\hygiene\Rotate-AiOsLogs.ps1"
    $diskWatch = Join-Path $repoRoot "automation\orchestration\hygiene\Watch-AiOsDiskSpace.ps1"
    $modeScript = Join-Path $repoRoot "automation\orchestration\mode\Get-AiOsActiveMode.ps1"
    $runner = Join-Path $repoRoot "automation\orchestration\relay\Invoke-AiOsRelayRunner.ps1"
    $resume = Join-Path $repoRoot "automation\orchestration\approval_runner\Invoke-AiOsApprovedActionResume.ps1"
    $pullBacklog = Join-Path $repoRoot "automation\orchestration\backlog\Pull-AiOsBacklog.ps1"
    $morningBriefScript = Join-Path $repoRoot "automation\orchestration\reports\New-AiOsMorningBrief.ps1"
    $staleApprovals = Join-Path $repoRoot "automation\orchestration\maintenance\Clear-AiOsStaleApprovals.ps1"
    $selfContinuation = Join-Path $repoRoot "automation\orchestration\self_continuation\Invoke-AiOsSelfContinuation.DRY_RUN.ps1"
    $nightSupervisorHarness = Join-Path $repoRoot "automation\orchestration\night_supervisor\night_supervisor_harness.py"
    $bridge = Join-Path $repoRoot "automation\orchestration\night_supervisor\Invoke-AiOsAutonomyBridge.DRY_RUN.ps1"
    $notifier = Join-Path $repoRoot "services\python_supervisor\notifier.py"
    $prWatch = Join-Path $repoRoot "automation\orchestration\pr_watch\Watch-AiOsPullRequests.ps1"
    [string[]]$hygieneArgs = if ($Apply) { @("-Apply") } else { @() }
    foreach ($requiredPath in @($rotateLogs, $diskWatch, $prWatch)) {
        if (-not (Test-Path -LiteralPath $requiredPath -PathType Leaf)) {
            throw "Night cycle hygiene dependency missing: $requiredPath"
        }
    }
    if (-not (Test-AiOsResumeSkip -Name "hygiene")) {
        Write-CycleMarker -Phase "hygiene" -State "STARTED"
        & $rotateLogs @hygieneArgs | Out-Null
        & $diskWatch @hygieneArgs | Out-Null
        Write-CycleMarker -Phase "hygiene" -State "COMPLETE"
        Update-AiOsDashboardState
    }

    $mode = & $modeScript
    switch ($mode.mode) {
        "OFF" { Write-AiOsNightCycleLog -Message "MODE=OFF reason=$($mode.reason)"; exit 0 }
        "DAY_OBSERVER" { $observeOnly = $true; $script:AiOsNextIntervalSeconds = 1800 }
        "NIGHT_AUTOPILOT" { $observeOnly = $false; $script:AiOsNextIntervalSeconds = 300 }
        default { $observeOnly = $true; $script:AiOsNextIntervalSeconds = 1800 }
    }

    $effectiveApply = ($Apply -and -not $observeOnly)
    [string[]]$applyArgs = if ($effectiveApply) { @("-Apply") } else { @() }
    [string[]]$alertArgs = if ($effectiveApply) { @("-AlertApply", "-StateApply") } else { @() }
    [string[]]$briefArgs = if ($effectiveApply) { @("-Apply") } else { @() }
    [string[]]$notifierArgs = @($notifier, "--channel", "file")
    if ($effectiveApply) { $notifierArgs += "--apply" }

    foreach ($requiredPath in @($modeScript, $runner, $pullBacklog, $morningBriefScript, $staleApprovals, $selfContinuation, $nightSupervisorHarness, $bridge, $notifier)) {
        if (-not (Test-Path -LiteralPath $requiredPath -PathType Leaf)) {
            throw "Night cycle dependency missing: $requiredPath"
        }
    }

    if ($effectiveApply -and -not (Test-Path -LiteralPath $resume -PathType Leaf)) {
        throw "Approval resume APPLY script missing: $resume"
    }

    Write-AiOsNightCycleLog -Message ("CYCLE START mode={0} apply={1} observe_only={2}" -f $mode.mode, [bool]$effectiveApply, [bool]$observeOnly)
    if ($observeOnly) {
        Complete-AiOsSkippedPhase -Number 1 -Name "clear-stale-approvals" -Reason "DAY_OBSERVER"
        Complete-AiOsSkippedPhase -Number 2 -Name "pull-backlog" -Reason "DAY_OBSERVER"
        Complete-AiOsSkippedPhase -Number 3 -Name "relay-runner" -Reason "DAY_OBSERVER"
        Complete-AiOsSkippedPhase -Number 4 -Name "approval-resume" -Reason "DAY_OBSERVER"
        Complete-AiOsSkippedPhase -Number 4 -Name "relay-runner-resume-drain" -Reason "DAY_OBSERVER"
        Complete-AiOsSkippedPhase -Number 5 -Name "self-continuation" -Reason "DAY_OBSERVER"
        Invoke-AiOsStep -Number 6 -Name "night-supervisor" -Command "python" -Arguments @($nightSupervisorHarness)
        Invoke-AiOsStep -Number 7 -Name "autonomy-bridge" -Command $ps -Arguments @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $bridge, "-AllowNonMain")
        if ($MorningBrief) {
            Invoke-AiOsStep -Number 8 -Name "morning-brief" -Command $ps -Arguments @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $morningBriefScript)
        } else {
            Complete-AiOsSkippedPhase -Number 8 -Name "morning-brief" -Reason "disabled"
        }
        Invoke-AiOsStep -Number 9 -Name "sos-file-notifier" -Command "python" -Arguments $notifierArgs
        Invoke-AiOsStep -Number 10 -Name "pr-watch" -Command $ps -Arguments @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $prWatch, "-Apply")
        Write-AiOsNightCycleLog -Message "CYCLE PASS"
        Write-CycleMarker -State "CYCLE_COMPLETE"
        Update-AiOsDashboardState
        return
    }

    Invoke-AiOsStep -Number 1 -Name "clear-stale-approvals" -Command $ps -Arguments (@("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $staleApprovals) + $applyArgs)
    Invoke-AiOsStep -Number 2 -Name "pull-backlog" -Command $ps -Arguments (@("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $pullBacklog) + $applyArgs)
    Invoke-AiOsStep -Number 3 -Name "relay-runner" -Command $ps -Arguments (@("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $runner) + $applyArgs)

    if ($effectiveApply) {
        Invoke-AiOsStep -Number 4 -Name "approval-resume" -Command $ps -Arguments @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $resume, "-Apply")
    } else {
        Complete-AiOsSkippedPhase -Number 4 -Name "approval-resume" -Reason "APPLY_ONLY"
    }

    if ($effectiveApply) {
        Write-AiOsNightCycleLog -Message "STEP 4 DRAIN resumed relay inbox"
        Invoke-AiOsStep -Number 4 -Name "relay-runner-resume-drain" -Command $ps -Arguments @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $runner, "-Apply")
    } else {
        Complete-AiOsSkippedPhase -Number 4 -Name "relay-runner-resume-drain" -Reason "APPLY_ONLY"
    }

    Invoke-AiOsStep -Number 5 -Name "self-continuation" -Command $ps -Arguments (@("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $selfContinuation) + $applyArgs)
    Invoke-AiOsStep -Number 6 -Name "night-supervisor" -Command "python" -Arguments @($nightSupervisorHarness)
    Invoke-AiOsStep -Number 7 -Name "autonomy-bridge" -Command $ps -Arguments (@("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $bridge, "-AllowNonMain") + $alertArgs)
    if ($MorningBrief) {
        Invoke-AiOsStep -Number 8 -Name "morning-brief" -Command $ps -Arguments (@("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $morningBriefScript) + $briefArgs)
    } else {
        Complete-AiOsSkippedPhase -Number 8 -Name "morning-brief" -Reason "disabled"
    }
    Invoke-AiOsStep -Number 9 -Name "sos-file-notifier" -Command "python" -Arguments $notifierArgs
    Invoke-AiOsStep -Number 10 -Name "pr-watch" -Command $ps -Arguments @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $prWatch, "-Apply")
    Write-AiOsNightCycleLog -Message "CYCLE PASS"
    Write-CycleMarker -State "CYCLE_COMPLETE"
    Update-AiOsDashboardState
}

do {
    Invoke-AiOsNightCycleOnce
    if ($Watch) {
        Start-Sleep -Seconds $script:AiOsNextIntervalSeconds
    }
} while ($Watch)
