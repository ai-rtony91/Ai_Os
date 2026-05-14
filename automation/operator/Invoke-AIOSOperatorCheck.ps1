[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

function Get-AIOSRepoRoot {
    $root = & git rev-parse --show-toplevel 2>$null
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($root)) {
        throw "Unable to find git repository root."
    }
    return $root.Trim()
}

function Get-AIOSChangedPath {
    param([string]$StatusLine)

    if ($StatusLine -like "##*") { return $null }
    if ($StatusLine.Length -lt 4) { return $null }

    $path = $StatusLine.Substring(3).Trim()
    if ($path -match " -> ") {
        $path = ($path -split " -> ")[-1].Trim()
    }
    return ($path -replace "\\", "/")
}

function Read-AIOSJsonFile {
    param([string]$Path)

    if (-not (Test-Path -LiteralPath $Path)) {
        return $null
    }

    try {
        return Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json
    }
    catch {
        return [pscustomobject]@{
            status = "REVIEW_REQUIRED"
            next_safe_action = "Review invalid JSON file: $Path"
        }
    }
}

function Get-AIOSObjectValue {
    param(
        [object]$Object,
        [string[]]$Names,
        [string]$Default = "UNKNOWN"
    )

    if ($null -eq $Object) { return $Default }
    foreach ($name in $Names) {
        if ($Object.PSObject.Properties.Name -contains $name) {
            $value = $Object.$name
            if ($null -ne $value -and -not [string]::IsNullOrWhiteSpace([string]$value)) {
                return [string]$value
            }
        }
    }
    return $Default
}

function Add-AIOSStatus {
    param(
        [System.Collections.Generic.List[string]]$Statuses,
        [string]$Status
    )

    if ([string]::IsNullOrWhiteSpace($Status)) { return }
    $normalized = $Status.ToUpperInvariant()
    if ($normalized -in @("PASS", "BLOCKED", "REVIEW_REQUIRED", "FAIL")) {
        if ($normalized -eq "FAIL") { $normalized = "BLOCKED" }
        $Statuses.Add($normalized) | Out-Null
    }
}

function Get-AIOSSummaryStatus {
    param([string[]]$Statuses)

    if ($Statuses -contains "BLOCKED") { return "BLOCKED" }
    if ($Statuses -contains "REVIEW_REQUIRED") { return "REVIEW_REQUIRED" }
    return "PASS"
}

function Write-AIOSLine {
    param(
        [string]$Label,
        [string]$Value
    )
    Write-Host ("{0}: {1}" -f $Label, $Value)
}

$repoRoot = Get-AIOSRepoRoot
Set-Location -LiteralPath $repoRoot

$statusLines = @(& git status --short --branch --untracked-files=all)
if ($LASTEXITCODE -ne 0) {
    throw "git status failed."
}

$branchLine = @($statusLines | Where-Object { $_ -like "##*" } | Select-Object -First 1)
$changedPaths = @(
    foreach ($line in $statusLines) {
        $path = Get-AIOSChangedPath -StatusLine $line
        if ($null -ne $path) { $path }
    }
)

$dirtyPaths = @($changedPaths)
$untrackedPaths = @(
    foreach ($line in $statusLines) {
        if ($line -like "?? *") {
            $path = Get-AIOSChangedPath -StatusLine $line
            if ($null -ne $path) { $path }
        }
    }
)
$dirtyOperatorPaths = @($dirtyPaths | Where-Object { $_ -like "automation/operator/*" })
$securityPathDetected = [bool]@($dirtyPaths | Where-Object { $_ -like "Reports/security*" }).Count

$validatorScript = Join-Path $repoRoot "automation/dispatcher/runtime/validators/Invoke-AIOSRuntimeValidatorDryRun.ps1"
$validatorStatus = "UNKNOWN"
$validatorCount = 0
$validatorNextAction = "Validator runner was not found."
if (Test-Path -LiteralPath $validatorScript) {
    try {
        $validatorRaw = & powershell -NoProfile -ExecutionPolicy Bypass -File $validatorScript 2>$null
        $validatorJson = ($validatorRaw -join [Environment]::NewLine) | ConvertFrom-Json
        $validatorStatus = Get-AIOSObjectValue -Object $validatorJson -Names @("status") -Default "REVIEW_REQUIRED"
        $validatorCount = [int](Get-AIOSObjectValue -Object $validatorJson -Names @("validators_run") -Default "0")
        $validatorNextAction = Get-AIOSObjectValue -Object $validatorJson -Names @("next_safe_action") -Default "Review validator output."
    }
    catch {
        $validatorStatus = "REVIEW_REQUIRED"
        $validatorNextAction = "Review validator runner failure before APPLY, staging, commit, or push."
    }
}

$packetState = Read-AIOSJsonFile -Path (Join-Path $repoRoot "Reports/dispatcher/runtime/packet_runtime_table.example.json")
$workerState = Read-AIOSJsonFile -Path (Join-Path $repoRoot "Reports/dispatcher/runtime/active_worker_table.example.json")
$approvalState = Read-AIOSJsonFile -Path (Join-Path $repoRoot "Reports/dispatcher/runtime/approval_runtime_status.example.json")
$commitState = Read-AIOSJsonFile -Path (Join-Path $repoRoot "Reports/dispatcher/runtime/commit_readiness_status.example.json")
$recoveryState = Read-AIOSJsonFile -Path (Join-Path $repoRoot "Reports/dispatcher/runtime/recovery_runtime_status.example.json")
$snapshotState = Read-AIOSJsonFile -Path (Join-Path $repoRoot "Reports/dispatcher/runtime/codex_window_snapshot_status.example.json")

$packetStatus = if ($packetState -and $packetState.packets) { Get-AIOSObjectValue -Object $packetState.packets[0] -Names @("status") -Default "REVIEW_REQUIRED" } else { "UNKNOWN" }
$workerStatus = if ($workerState -and $workerState.workers) { Get-AIOSObjectValue -Object $workerState.workers[0] -Names @("status", "last_status") -Default "REVIEW_REQUIRED" } else { "UNKNOWN" }
$approvalStatus = if ($approvalState -and $approvalState.approval_requests) { Get-AIOSObjectValue -Object $approvalState.approval_requests[0] -Names @("approval_status", "status") -Default "REVIEW_REQUIRED" } else { "UNKNOWN" }
$commitStatus = if ($commitState) { Get-AIOSObjectValue -Object $commitState -Names @("commit_readiness", "status") -Default "UNKNOWN" } else { "UNKNOWN" }
$recoveryStatus = if ($recoveryState) { Get-AIOSObjectValue -Object $recoveryState -Names @("recovery_status", "status") -Default "UNKNOWN" } else { "UNKNOWN" }
$snapshotStatus = if ($snapshotState -and $snapshotState.dirty_repo_status) { Get-AIOSObjectValue -Object $snapshotState.dirty_repo_status -Names @("state", "status") -Default "UNKNOWN" } else { "UNKNOWN" }

$statusRollup = [System.Collections.Generic.List[string]]::new()
if ($dirtyPaths.Count -gt 0) { Add-AIOSStatus -Statuses $statusRollup -Status "REVIEW_REQUIRED" }
if ($dirtyOperatorPaths.Count -gt 0) { Add-AIOSStatus -Statuses $statusRollup -Status "REVIEW_REQUIRED" }
if ($securityPathDetected) { Add-AIOSStatus -Statuses $statusRollup -Status "REVIEW_REQUIRED" }
Add-AIOSStatus -Statuses $statusRollup -Status $validatorStatus
Add-AIOSStatus -Statuses $statusRollup -Status $packetStatus
Add-AIOSStatus -Statuses $statusRollup -Status $workerStatus
Add-AIOSStatus -Statuses $statusRollup -Status $approvalStatus
Add-AIOSStatus -Statuses $statusRollup -Status $commitStatus
Add-AIOSStatus -Statuses $statusRollup -Status $recoveryStatus
Add-AIOSStatus -Statuses $statusRollup -Status $snapshotStatus

$overallStatus = Get-AIOSSummaryStatus -Statuses $statusRollup.ToArray()
$repoStatus = if ($dirtyPaths.Count -gt 0) { "REVIEW_REQUIRED" } else { "PASS" }
$nextSafeAction = switch ($overallStatus) {
    "BLOCKED" { "Do not stage or commit. Review commit readiness, dirty files, and validator warnings first." }
    "REVIEW_REQUIRED" { "Review the listed warnings, then approve one exact APPLY or commit package only if needed." }
    default { "Repo check is clear. Continue with the next DRY_RUN task before any APPLY work." }
}

Write-Host "AI_OS OPERATOR CHECK"
Write-AIOSLine -Label "Mode" -Value "DRY_RUN_READ_ONLY"
Write-AIOSLine -Label "Branch" -Value $branchLine
Write-AIOSLine -Label "Overall" -Value $overallStatus
Write-AIOSLine -Label "Repo" -Value ("{0} ({1} changed, {2} untracked)" -f $repoStatus, $dirtyPaths.Count, $untrackedPaths.Count)
Write-AIOSLine -Label "Validators" -Value ("{0} ({1} run)" -f $validatorStatus, $validatorCount)
Write-AIOSLine -Label "Packet Queue" -Value $packetStatus
Write-AIOSLine -Label "Workers" -Value $workerStatus
Write-AIOSLine -Label "Approval" -Value $approvalStatus
Write-AIOSLine -Label "Commit Readiness" -Value $commitStatus
Write-AIOSLine -Label "Recovery" -Value $recoveryStatus
Write-AIOSLine -Label "Snapshot Bootstrap" -Value $snapshotStatus

$warnings = [System.Collections.Generic.List[string]]::new()
if ($dirtyOperatorPaths.Count -gt 0) {
    $warnings.Add(("Dirty operator files require review: {0}" -f $dirtyOperatorPaths.Count)) | Out-Null
}
if ($securityPathDetected) {
    $warnings.Add("Reports/security path detected from git status only; contents were not inspected.") | Out-Null
}
if ($validatorStatus -ne "PASS") {
    $warnings.Add(("Validator runner reported {0}: {1}" -f $validatorStatus, $validatorNextAction)) | Out-Null
}
if ($commitStatus -eq "BLOCKED") {
    $warnings.Add("Commit readiness is BLOCKED.") | Out-Null
}

if ($warnings.Count -gt 0) {
    Write-Host ""
    Write-Host "Warnings:"
    foreach ($warning in $warnings) {
        Write-Host ("- {0}" -f $warning)
    }
}

Write-Host ""
Write-AIOSLine -Label "Next safe action" -Value $nextSafeAction

