[CmdletBinding()]
param(
    [string[]]$AllowedPaths = @("automation/dispatcher/runtime/validators"),
    [string[]]$BlockedPaths = @(
        "automation/operator",
        "Reports/security",
        "apps/dashboard",
        "automation/telemetry",
        "Reports/telemetry"
    )
)

$ErrorActionPreference = "Stop"

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
. (Join-Path $scriptRoot "Test-AIOSRuntimeJson.ps1")
. (Join-Path $scriptRoot "Test-AIOSAllowedPath.ps1")
. (Join-Path $scriptRoot "Test-AIOSBlockedPath.ps1")
. (Join-Path $scriptRoot "Test-AIOSProtectedRoot.ps1")
. (Join-Path $scriptRoot "Test-AIOSDirtyRepo.ps1")
. (Join-Path $scriptRoot "Test-AIOSExactFileStaging.ps1")
. (Join-Path $scriptRoot "Test-AIOSStaleWorker.ps1")
. (Join-Path $scriptRoot "Test-AIOSStaleLock.ps1")
. (Join-Path $scriptRoot "Test-AIOSRecoveryResume.ps1")

function Get-AIOSChangedPaths {
    $lines = & git status --short --branch --untracked-files=all
    if ($LASTEXITCODE -ne 0) {
        return @()
    }

    $paths = New-Object System.Collections.Generic.List[string]
    foreach ($line in $lines) {
        if ($line -like "##*") { continue }
        if ($line.Length -lt 4) { continue }
        $paths.Add($line.Substring(3).Trim()) | Out-Null
    }
    $paths.ToArray()
}

function Get-AIOSRuntimeValidatorSummaryStatus {
    param([object[]]$Results)
    if (@($Results | Where-Object { $_.status -eq "BLOCKED" }).Count -gt 0) { return "BLOCKED" }
    if (@($Results | Where-Object { $_.status -eq "FAIL" }).Count -gt 0) { return "FAIL" }
    if (@($Results | Where-Object { $_.status -eq "REVIEW_REQUIRED" }).Count -gt 0) { return "REVIEW_REQUIRED" }
    return "PASS"
}

$approvedFiles = @(
    "automation/dispatcher/runtime/validators/Test-AIOSRuntimeJson.ps1",
    "automation/dispatcher/runtime/validators/Test-AIOSAllowedPath.ps1",
    "automation/dispatcher/runtime/validators/Test-AIOSBlockedPath.ps1",
    "automation/dispatcher/runtime/validators/Test-AIOSProtectedRoot.ps1",
    "automation/dispatcher/runtime/validators/Test-AIOSDirtyRepo.ps1",
    "automation/dispatcher/runtime/validators/Test-AIOSExactFileStaging.ps1",
    "automation/dispatcher/runtime/validators/Test-AIOSStaleWorker.ps1",
    "automation/dispatcher/runtime/validators/Test-AIOSStaleLock.ps1",
    "automation/dispatcher/runtime/validators/Test-AIOSRecoveryResume.ps1",
    "automation/dispatcher/runtime/validators/Invoke-AIOSRuntimeValidatorDryRun.ps1"
)
$packagePaths = $approvedFiles

$results = @(
    Test-AIOSRuntimeJson
    Test-AIOSAllowedPath -ChangedPaths $packagePaths -AllowedPaths $AllowedPaths
    Test-AIOSBlockedPath -ChangedPaths $packagePaths -BlockedPaths $BlockedPaths
    Test-AIOSProtectedRoot -ChangedPaths $packagePaths
    Test-AIOSDirtyRepo -ApprovedPaths $AllowedPaths -KnownIsolatedPaths @("automation/operator", "Reports/security")
    Test-AIOSExactFileStaging -ApprovedFiles $approvedFiles -ProposedStagingCommands @()
    Test-AIOSStaleWorker
    Test-AIOSStaleLock
    Test-AIOSRecoveryResume
)

$summaryStatus = Get-AIOSRuntimeValidatorSummaryStatus -Results $results

[pscustomobject]@{
    schema = "AIOS_RUNTIME_VALIDATOR_DRY_RUN_SUMMARY.v1"
    generated_at = (Get-Date).ToUniversalTime().ToString("o")
    mode = "DRY_RUN"
    status = $summaryStatus
    validators_run = $results.Count
    results = $results
    blocked_actions = @("modify_files", "stage_files", "commit", "push", "startup_tasks", "scheduled_tasks")
    next_safe_action = "Review validator results before any APPLY, staging, commit, push, or recovery resume."
} | ConvertTo-Json -Depth 10
