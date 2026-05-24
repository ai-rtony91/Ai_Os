<#
.SYNOPSIS
Runs all AI_OS read-only status checks in one command.

.DESCRIPTION
Invoke-AiOsReadOnlyStatus.DRY_RUN.ps1 calls git status, the post-merge
verification gate, and the PR lane runner in sequence. Each section runs
read-only and reports its output. If any gate script fails, the failure
is reported and the wrapper continues to the next check.

This script does not stage, commit, push, merge, switch branches, reset,
clean files, or write reports.

.PARAMETER Json
Pass -Json to each gate script for structured JSON output.

.EXAMPLE
.\automation\orchestration\Invoke-AiOsReadOnlyStatus.DRY_RUN.ps1

.EXAMPLE
.\automation\orchestration\Invoke-AiOsReadOnlyStatus.DRY_RUN.ps1 -Json
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [switch] $Json
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$scriptName = Split-Path -Leaf $PSCommandPath
$scriptDir = Split-Path -Parent $PSCommandPath
$timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
$overallSuccess = $true

function Write-Section {
    param(
        [Parameter(Mandatory = $true)][string] $Title
    )

    Write-Output ""
    Write-Output ("=" * 60)
    Write-Output "  $Title"
    Write-Output ("=" * 60)
    Write-Output ""
}

function Invoke-GateScript {
    param(
        [Parameter(Mandatory = $true)][string] $Path,
        [Parameter(Mandatory = $true)][string] $Label,
        [Parameter(Mandatory = $false)][string[]] $ExtraArgs = @()
    )

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        Write-Output "SKIPPED: $Label"
        Write-Output "  Script not found: $Path"
        $script:lastGateResult = $false; return
    }

    $ErrorActionPreference = "Continue"
    $output = & powershell -ExecutionPolicy Bypass -File $Path @ExtraArgs 2>&1
    $exitCode = $LASTEXITCODE
    $ErrorActionPreference = "Stop"

    $stdoutItems = @($output | Where-Object { $_ -isnot [System.Management.Automation.ErrorRecord] })
    $stderrItems = @($output | Where-Object { $_ -is [System.Management.Automation.ErrorRecord] })

    foreach ($line in $stdoutItems) {
        Write-Output ([string] $line)
    }

    if ($stderrItems.Count -gt 0) {
        foreach ($err in $stderrItems) {
            Write-Warning "[$Label] $($err.Exception.Message)"
        }
    }

    if ($exitCode -ne 0) {
        Write-Output ""
        Write-Output "EXIT CODE: $exitCode (FAILED)"
        $script:lastGateResult = $false; return
    }

    $script:lastGateResult = $true
}

Write-Output "# AI_OS Read-Only Status"
Write-Output "Script: $scriptName"
Write-Output "Timestamp: $timestamp"
Write-Output "Mode: DRY_RUN"

# --- Section 1: git status ---
Write-Section -Title "Git Status"

$ErrorActionPreference = "Continue"
$gitOutput = & git status --short --branch 2>&1
$gitExitCode = $LASTEXITCODE
$ErrorActionPreference = "Stop"

$gitStdout = @($gitOutput | Where-Object { $_ -isnot [System.Management.Automation.ErrorRecord] })
$gitStderr = @($gitOutput | Where-Object { $_ -is [System.Management.Automation.ErrorRecord] })

foreach ($line in $gitStdout) {
    Write-Output ([string] $line)
}

if ($gitStderr.Count -gt 0) {
    foreach ($err in $gitStderr) {
        Write-Warning "[git status] $($err.Exception.Message)"
    }
}

if ($gitExitCode -ne 0) {
    Write-Output ""
    Write-Output "git status EXIT CODE: $gitExitCode (FAILED)"
    $overallSuccess = $false
}

# --- Section 2: Post-Merge Verification ---
Write-Section -Title "Post-Merge Verification"

$postMergePath = Join-Path $scriptDir "post_push\Test-AiOsPostPushVerification.DRY_RUN.ps1"
$postMergeArgs = @()
if ($Json) { $postMergeArgs += "-Json" }

Invoke-GateScript -Path $postMergePath -Label "Post-Merge Verification" -ExtraArgs $postMergeArgs
if (-not $script:lastGateResult) {
    $overallSuccess = $false
}

# --- Section 3: PR Lane Runner ---
Write-Section -Title "PR Lane Runner"

$laneRunnerPath = Join-Path $scriptDir "pr_gates\Invoke-AiOsPrLaneRunner.DRY_RUN.ps1"
$laneRunnerArgs = @()
if ($Json) { $laneRunnerArgs += "-Json" }

Invoke-GateScript -Path $laneRunnerPath -Label "PR Lane Runner" -ExtraArgs $laneRunnerArgs
if (-not $script:lastGateResult) {
    $overallSuccess = $false
}

# --- Footer ---
Write-Output ""
Write-Output ("=" * 60)
$overallStatus = if ($overallSuccess) { "ALL CHECKS COMPLETED" } else { "ONE OR MORE CHECKS FAILED" }
Write-Output "  $overallStatus"
Write-Output ("=" * 60)
Write-Output ""
Write-Output "Commit performed: NO"
Write-Output "Push performed: NO"

if (-not $overallSuccess) {
    exit 1
}
