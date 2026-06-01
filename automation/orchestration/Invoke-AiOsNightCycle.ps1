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
    [ValidateRange(5, 86400)]
    [int]$IntervalSeconds = 300
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..")).Path
$relayRoot = Join-Path $repoRoot "relay"
$logPath = Join-Path $relayRoot "logs\night_cycle.log"
$script:AiOsNextIntervalSeconds = $IntervalSeconds

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

function Invoke-AiOsStep {
    param(
        [Parameter(Mandatory = $true)][int]$Number,
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][string]$Command,
        [string[]]$Arguments = @()
    )

    Write-AiOsNightCycleLog -Message ("STEP {0} START {1}" -f $Number, $Name)
    & $Command @Arguments
    $exit = if ($null -ne $LASTEXITCODE) { [int]$LASTEXITCODE } else { 0 }
    if ($exit -ne 0) {
        Write-AiOsNightCycleLog -Message ("STEP {0} FAIL {1} exit={2}" -f $Number, $Name, $exit)
        throw "Night cycle step failed: $Name exit=$exit"
    }
    Write-AiOsNightCycleLog -Message ("STEP {0} PASS {1}" -f $Number, $Name)
}

function Invoke-AiOsNightCycleOnce {
    $ps = (Get-Command powershell -ErrorAction Stop).Source
    $modeScript = Join-Path $repoRoot "automation\orchestration\mode\Get-AiOsActiveMode.ps1"
    $runner = Join-Path $repoRoot "automation\orchestration\relay\Invoke-AiOsRelayRunner.ps1"
    $resume = Join-Path $repoRoot "automation\orchestration\approval_runner\Invoke-AiOsApprovedActionResume.ps1"
    $pullBacklog = Join-Path $repoRoot "automation\orchestration\backlog\Pull-AiOsBacklog.ps1"
    $morningBriefScript = Join-Path $repoRoot "automation\orchestration\reports\New-AiOsMorningBrief.ps1"
    $staleApprovals = Join-Path $repoRoot "automation\orchestration\maintenance\Clear-AiOsStaleApprovals.ps1"
    $selfContinuation = Join-Path $repoRoot "automation\orchestration\self_continuation\Invoke-AiOsSelfContinuation.DRY_RUN.ps1"
    $bridge = Join-Path $repoRoot "automation\orchestration\night_supervisor\Invoke-AiOsAutonomyBridge.DRY_RUN.ps1"
    $notifier = Join-Path $repoRoot "services\python_supervisor\notifier.py"
    $mode = & $modeScript
    switch ($mode.mode) {
        "OFF" { Write-AiOsNightCycleLog -Message "MODE=OFF reason=$($mode.reason)"; exit 0 }
        "DAY_OBSERVER" { $observeOnly = $true; $script:AiOsNextIntervalSeconds = 1800 }
        "NIGHT_AUTOPILOT" { $observeOnly = $false; $script:AiOsNextIntervalSeconds = 300 }
        default { $observeOnly = $true; $script:AiOsNextIntervalSeconds = 1800 }
    }

    $effectiveApply = ($Apply -and -not $observeOnly)
    $applyArgs = if ($effectiveApply) { @("-Apply") } else { @() }
    $alertArgs = if ($effectiveApply) { @("-AlertApply", "-StateApply") } else { @() }
    $briefArgs = if ($effectiveApply) { @("-Apply") } else { @() }
    $notifierArgs = @($notifier, "--channel", "file")
    if ($effectiveApply) { $notifierArgs += "--apply" }

    foreach ($requiredPath in @($modeScript, $runner, $pullBacklog, $morningBriefScript, $staleApprovals, $selfContinuation, $bridge, $notifier)) {
        if (-not (Test-Path -LiteralPath $requiredPath -PathType Leaf)) {
            throw "Night cycle dependency missing: $requiredPath"
        }
    }

    if ($effectiveApply -and -not (Test-Path -LiteralPath $resume -PathType Leaf)) {
        throw "Approval resume APPLY script missing: $resume"
    }

    Write-AiOsNightCycleLog -Message ("CYCLE START mode={0} apply={1} observe_only={2}" -f $mode.mode, [bool]$effectiveApply, [bool]$observeOnly)
    if ($observeOnly) {
        Write-AiOsNightCycleLog -Message "STEP 1 SKIP clear-stale-approvals DAY_OBSERVER"
        Write-AiOsNightCycleLog -Message "STEP 2 SKIP pull-backlog DAY_OBSERVER"
        Write-AiOsNightCycleLog -Message "STEP 3 SKIP relay-runner DAY_OBSERVER"
        Write-AiOsNightCycleLog -Message "STEP 4 SKIP approval-resume DAY_OBSERVER"
        Write-AiOsNightCycleLog -Message "STEP 5 SKIP self-continuation DAY_OBSERVER"
        Invoke-AiOsStep -Number 6 -Name "autonomy-bridge" -Command $ps -Arguments @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $bridge, "-AllowNonMain")
        if ($MorningBrief) {
            Invoke-AiOsStep -Number 7 -Name "morning-brief" -Command $ps -Arguments @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $morningBriefScript)
        } else {
            Write-AiOsNightCycleLog -Message "STEP 7 SKIP morning-brief disabled"
        }
        Invoke-AiOsStep -Number 8 -Name "sos-file-notifier" -Command "python" -Arguments $notifierArgs
        Write-AiOsNightCycleLog -Message "CYCLE PASS"
        return
    }

    Invoke-AiOsStep -Number 1 -Name "clear-stale-approvals" -Command $ps -Arguments (@("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $staleApprovals) + $applyArgs)
    Invoke-AiOsStep -Number 2 -Name "pull-backlog" -Command $ps -Arguments (@("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $pullBacklog) + $applyArgs)
    Invoke-AiOsStep -Number 3 -Name "relay-runner" -Command $ps -Arguments (@("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $runner) + $applyArgs)

    if ($effectiveApply) {
        Invoke-AiOsStep -Number 4 -Name "approval-resume" -Command $ps -Arguments @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $resume, "-Apply")
    } else {
        Write-AiOsNightCycleLog -Message "STEP 4 SKIP approval-resume APPLY_ONLY"
    }

    if ($effectiveApply) {
        Write-AiOsNightCycleLog -Message "STEP 4 DRAIN resumed relay inbox"
        Invoke-AiOsStep -Number 4 -Name "relay-runner-resume-drain" -Command $ps -Arguments @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $runner, "-Apply")
    }

    Invoke-AiOsStep -Number 5 -Name "self-continuation" -Command $ps -Arguments (@("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $selfContinuation) + $applyArgs)
    Invoke-AiOsStep -Number 6 -Name "autonomy-bridge" -Command $ps -Arguments (@("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $bridge, "-AllowNonMain") + $alertArgs)
    if ($MorningBrief) {
        Invoke-AiOsStep -Number 7 -Name "morning-brief" -Command $ps -Arguments (@("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $morningBriefScript) + $briefArgs)
    } else {
        Write-AiOsNightCycleLog -Message "STEP 7 SKIP morning-brief disabled"
    }
    Invoke-AiOsStep -Number 8 -Name "sos-file-notifier" -Command "python" -Arguments $notifierArgs
    Write-AiOsNightCycleLog -Message "CYCLE PASS"
}

do {
    Invoke-AiOsNightCycleOnce
    if ($Watch) {
        Start-Sleep -Seconds $script:AiOsNextIntervalSeconds
    }
} while ($Watch)
