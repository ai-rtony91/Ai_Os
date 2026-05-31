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
    [ValidateRange(5, 86400)]
    [int]$IntervalSeconds = 300
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..")).Path
$relayRoot = Join-Path $repoRoot "relay"
$logPath = Join-Path $relayRoot "logs\night_cycle.log"

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
    $runner = Join-Path $repoRoot "automation\orchestration\relay\Invoke-AiOsRelayRunner.ps1"
    $resume = Join-Path $repoRoot "automation\orchestration\approval_runner\Invoke-AiOsApprovedActionResume.DRY_RUN.ps1"
    $selfContinuation = Join-Path $repoRoot "automation\orchestration\self_continuation\Invoke-AiOsSelfContinuation.DRY_RUN.ps1"
    $bridge = Join-Path $repoRoot "automation\orchestration\night_supervisor\Invoke-AiOsAutonomyBridge.DRY_RUN.ps1"
    $notifier = Join-Path $repoRoot "services\python_supervisor\notifier.py"

    $applyArgs = if ($Apply) { @("-Apply") } else { @() }
    $alertArgs = if ($Apply) { @("-AlertApply", "-StateApply") } else { @() }
    $notifierArgs = @($notifier, "--channel", "file")
    if ($Apply) { $notifierArgs += "--apply" }

    Write-AiOsNightCycleLog -Message ("CYCLE START mode={0}" -f $(if ($Apply) { "APPLY" } else { "DRY_RUN" }))
    Invoke-AiOsStep -Number 1 -Name "relay-runner" -Command $ps -Arguments (@("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $runner) + $applyArgs)
    Invoke-AiOsStep -Number 2 -Name "approval-resume" -Command $ps -Arguments (@("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $resume) + $applyArgs)

    if ($Apply) {
        Write-AiOsNightCycleLog -Message "STEP 2 DRAIN resumed relay inbox"
        Invoke-AiOsStep -Number 2 -Name "relay-runner-resume-drain" -Command $ps -Arguments @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $runner, "-Apply")
    }

    Invoke-AiOsStep -Number 3 -Name "self-continuation" -Command $ps -Arguments (@("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $selfContinuation) + $applyArgs)
    Invoke-AiOsStep -Number 4 -Name "autonomy-bridge" -Command $ps -Arguments (@("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $bridge, "-AllowNonMain") + $alertArgs)
    Invoke-AiOsStep -Number 5 -Name "sos-file-notifier" -Command "python" -Arguments $notifierArgs
    Write-AiOsNightCycleLog -Message "CYCLE PASS"
}

do {
    Invoke-AiOsNightCycleOnce
    if ($Watch) {
        Start-Sleep -Seconds $IntervalSeconds
    }
} while ($Watch)
