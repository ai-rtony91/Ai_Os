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

function Read-AIOSPreferredJsonFile {
    param(
        [string]$LivePath,
        [string]$ExamplePath
    )

    if (Test-Path -LiteralPath $LivePath) {
        return [pscustomobject]@{
            source = "LIVE"
            path = $LivePath
            data = Read-AIOSJsonFile -Path $LivePath
        }
    }

    if (Test-Path -LiteralPath $ExamplePath) {
        return [pscustomobject]@{
            source = "EXAMPLE_FALLBACK"
            path = $ExamplePath
            data = Read-AIOSJsonFile -Path $ExamplePath
        }
    }

    return [pscustomobject]@{
        source = "MISSING"
        path = $LivePath
        data = $null
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

function Get-AIOSArrayCount {
    param([object]$Value)

    if ($null -eq $Value) { return 0 }
    return @($Value).Count
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

$packetStateRef = Read-AIOSPreferredJsonFile `
    -LivePath (Join-Path $repoRoot "Reports/dispatcher/runtime/packets/packet_runtime_table.json") `
    -ExamplePath (Join-Path $repoRoot "Reports/dispatcher/runtime/packet_runtime_table.example.json")
$packetQueueRef = Read-AIOSPreferredJsonFile `
    -LivePath (Join-Path $repoRoot "Reports/dispatcher/runtime/packets/packet_queue.json") `
    -ExamplePath (Join-Path $repoRoot "Reports/dispatcher/runtime/packets/packet_queue.example.json")
$workerStateRef = Read-AIOSPreferredJsonFile `
    -LivePath (Join-Path $repoRoot "Reports/dispatcher/runtime/workers/active_worker_table.json") `
    -ExamplePath (Join-Path $repoRoot "Reports/dispatcher/runtime/active_worker_table.example.json")
$heartbeatStateRef = Read-AIOSPreferredJsonFile `
    -LivePath (Join-Path $repoRoot "Reports/dispatcher/runtime/workers/worker_heartbeat_table.json") `
    -ExamplePath (Join-Path $repoRoot "Reports/dispatcher/runtime/workers/worker_heartbeat_table.example.json")
$recoveryStateRef = Read-AIOSPreferredJsonFile `
    -LivePath (Join-Path $repoRoot "Reports/dispatcher/runtime/recovery/live_recovery_state.json") `
    -ExamplePath (Join-Path $repoRoot "Reports/dispatcher/runtime/recovery_runtime_status.example.json")

$packetState = $packetStateRef.data
$packetQueueState = $packetQueueRef.data
$workerState = $workerStateRef.data
$heartbeatState = $heartbeatStateRef.data
$approvalState = Read-AIOSJsonFile -Path (Join-Path $repoRoot "Reports/dispatcher/runtime/approval_runtime_status.example.json")
$commitState = Read-AIOSJsonFile -Path (Join-Path $repoRoot "Reports/dispatcher/runtime/commit_readiness_status.example.json")
$recoveryState = $recoveryStateRef.data
$snapshotState = Read-AIOSJsonFile -Path (Join-Path $repoRoot "Reports/dispatcher/runtime/codex_window_snapshot_status.example.json")

$packetStatus = if ($packetState -and $packetState.packets) { Get-AIOSObjectValue -Object $packetState.packets[0] -Names @("status") -Default "REVIEW_REQUIRED" } else { "UNKNOWN" }
$packetQueuedCount = if ($packetQueueState -and $packetQueueState.packets) { @($packetQueueState.packets | Where-Object { $_.status -eq "QUEUED" }).Count } else { 0 }
$workerStatus = if ($workerState -and $workerState.workers) { Get-AIOSObjectValue -Object $workerState.workers[0] -Names @("current_state", "status", "last_status") -Default "REVIEW_REQUIRED" } else { "UNKNOWN" }
$workerCount = if ($workerState -and $workerState.workers) { Get-AIOSArrayCount -Value $workerState.workers } else { 0 }
$missingHeartbeatCount = if ($heartbeatState -and $heartbeatState.heartbeats) {
    @($heartbeatState.heartbeats | Where-Object { $null -eq $_.heartbeat_time -or [string]::IsNullOrWhiteSpace([string]$_.heartbeat_time) }).Count
} else {
    0
}
$approvalStatus = if ($approvalState -and $approvalState.approval_requests) { Get-AIOSObjectValue -Object $approvalState.approval_requests[0] -Names @("approval_status", "status") -Default "REVIEW_REQUIRED" } else { "UNKNOWN" }
$commitStatus = if ($commitState) { Get-AIOSObjectValue -Object $commitState -Names @("commit_readiness", "status") -Default "UNKNOWN" } else { "UNKNOWN" }
$recoveryStatus = if ($recoveryState) { Get-AIOSObjectValue -Object $recoveryState -Names @("recovery_status", "status") -Default "UNKNOWN" } else { "UNKNOWN" }
$staleWorkerCount = if ($recoveryState -and $recoveryState.runtime_summary) { [int](Get-AIOSObjectValue -Object $recoveryState.runtime_summary -Names @("stale_worker_count") -Default "0") } else { 0 }
$snapshotStatus = if ($snapshotState -and $snapshotState.dirty_repo_status) { Get-AIOSObjectValue -Object $snapshotState.dirty_repo_status -Names @("state", "status") -Default "UNKNOWN" } else { "UNKNOWN" }

$statusRollup = [System.Collections.Generic.List[string]]::new()
if ($dirtyPaths.Count -gt 0) { Add-AIOSStatus -Statuses $statusRollup -Status "REVIEW_REQUIRED" }
if ($dirtyOperatorPaths.Count -gt 0) { Add-AIOSStatus -Statuses $statusRollup -Status "REVIEW_REQUIRED" }
if ($securityPathDetected) { Add-AIOSStatus -Statuses $statusRollup -Status "REVIEW_REQUIRED" }
foreach ($source in @($packetStateRef.source, $packetQueueRef.source, $workerStateRef.source, $heartbeatStateRef.source, $recoveryStateRef.source)) {
    if ($source -ne "LIVE") { Add-AIOSStatus -Statuses $statusRollup -Status "REVIEW_REQUIRED" }
}
if ($missingHeartbeatCount -gt 0) { Add-AIOSStatus -Statuses $statusRollup -Status "REVIEW_REQUIRED" }
if ($staleWorkerCount -gt 0) { Add-AIOSStatus -Statuses $statusRollup -Status "REVIEW_REQUIRED" }
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
Write-AIOSLine -Label "Packet Queue" -Value ("{0} ({1} queued, {2})" -f $packetStatus, $packetQueuedCount, $packetQueueRef.source)
Write-AIOSLine -Label "Workers" -Value ("{0} ({1} workers, {2} missing heartbeats, {3})" -f $workerStatus, $workerCount, $missingHeartbeatCount, $workerStateRef.source)
Write-AIOSLine -Label "Approval" -Value $approvalStatus
Write-AIOSLine -Label "Commit Readiness" -Value $commitStatus
Write-AIOSLine -Label "Recovery" -Value ("{0} ({1} stale workers, {2})" -f $recoveryStatus, $staleWorkerCount, $recoveryStateRef.source)
Write-AIOSLine -Label "Snapshot Bootstrap" -Value $snapshotStatus

$warnings = [System.Collections.Generic.List[string]]::new()
if ($dirtyOperatorPaths.Count -gt 0) {
    $warnings.Add(("Dirty operator files require review: {0}" -f $dirtyOperatorPaths.Count)) | Out-Null
}
if ($securityPathDetected) {
    $warnings.Add("Reports/security path detected from git status only; contents were not inspected.") | Out-Null
}
foreach ($runtimeRef in @($packetStateRef, $packetQueueRef, $workerStateRef, $heartbeatStateRef, $recoveryStateRef)) {
    if ($runtimeRef.source -ne "LIVE") {
        $warnings.Add(("Runtime source is {0}: {1}" -f $runtimeRef.source, $runtimeRef.path)) | Out-Null
    }
}
if ($missingHeartbeatCount -gt 0) {
    $warnings.Add(("Worker heartbeats missing or null: {0}" -f $missingHeartbeatCount)) | Out-Null
}
if ($staleWorkerCount -gt 0) {
    $warnings.Add(("Recovery reports stale workers: {0}" -f $staleWorkerCount)) | Out-Null
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
