Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$orchestrationRoot = $PSScriptRoot
$snapshotPath = Join-Path $orchestrationRoot "orchestration_status_snapshot.example.json"

function Read-JsonFile {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return $null
    }

    Get-Content -Raw -LiteralPath $Path | ConvertFrom-Json
}

function Resolve-InputPath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$FileName
    )

    Join-Path $orchestrationRoot $FileName
}

function Write-MissingInput {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name,

        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    Write-Host "$Name summary:"
    Write-Host "  Status: UNKNOWN"
    Write-Host "  Reason: input file not found"
    Write-Host "  Path: $Path"
    Write-Host ""
}

$snapshot = Read-JsonFile -Path $snapshotPath
if ($null -eq $snapshot) {
    throw "Required file was not found: $snapshotPath"
}

$inputs = $snapshot.status_inputs
$queuePath = Resolve-InputPath -FileName $inputs.queue
$workerPath = Resolve-InputPath -FileName $inputs.worker_registry
$approvalPath = Resolve-InputPath -FileName $inputs.approval_inbox
$validatorPath = Resolve-InputPath -FileName $inputs.validator_chain
$recoveryPath = Resolve-InputPath -FileName $inputs.recovery_bootstrap

$queue = Read-JsonFile -Path $queuePath
$workerRegistry = Read-JsonFile -Path $workerPath
$approvalInbox = Read-JsonFile -Path $approvalPath
$validatorChain = Read-JsonFile -Path $validatorPath
$recoveryBootstrap = Read-JsonFile -Path $recoveryPath

Write-Host "AI_OS Orchestration Status Snapshot"
Write-Host "Mode: $($snapshot.mode)"
Write-Host "Snapshot: $($snapshot.snapshot_name)"
Write-Host "Phase: $($snapshot.phase)"
Write-Host "Stage: $($snapshot.stage)"
Write-Host "Purpose: $($snapshot.purpose)"
Write-Host ""
Write-Host "Safety: read-only display. Nothing is modified, created, launched, staged, committed, or pushed."
Write-Host ""

if ($null -eq $queue) {
    Write-MissingInput -Name "Queue" -Path $queuePath
} else {
    $packets = @($queue.packets)
    $availablePackets = @($packets | Where-Object { $_.status -eq "available" })
    $assignedPackets = @($packets | Where-Object { $null -ne $_.assigned_worker_id })
    $approvalRequiredPackets = @($packets | Where-Object { $_.approval_required -eq $true })
    $validatorRequiredPackets = @($packets | Where-Object { $_.validator_required -eq $true })

    Write-Host "Queue summary:"
    Write-Host "  Source: $($inputs.queue)"
    Write-Host "  Queue: $($queue.queue_name)"
    Write-Host "  Mode: $($queue.mode)"
    Write-Host "  Total packets: $($packets.Count)"
    Write-Host "  Available packets: $($availablePackets.Count)"
    Write-Host "  Assigned packets: $($assignedPackets.Count)"
    Write-Host "  Approval required: $($approvalRequiredPackets.Count)"
    Write-Host "  Validator required: $($validatorRequiredPackets.Count)"
    Write-Host ""
}

if ($null -eq $workerRegistry) {
    Write-MissingInput -Name "Worker" -Path $workerPath
} else {
    $workers = @($workerRegistry.workers)
    $standbyWorkers = @($workers | Where-Object { $_.status -eq "standby" })
    $assignedWorkers = @($workers | Where-Object { $null -ne $_.assigned_packet_id })

    Write-Host "Worker summary:"
    Write-Host "  Source: $($inputs.worker_registry)"
    Write-Host "  Registry: $($workerRegistry.registry_name)"
    Write-Host "  Mode: $($workerRegistry.mode)"
    Write-Host "  Total workers: $($workers.Count)"
    Write-Host "  Standby workers: $($standbyWorkers.Count)"
    Write-Host "  Assigned workers: $($assignedWorkers.Count)"
    Write-Host ""
}

if ($null -eq $approvalInbox) {
    Write-MissingInput -Name "Approval" -Path $approvalPath
} else {
    $approvalPackets = @($approvalInbox.packets)
    $pendingApprovals = @($approvalPackets | Where-Object { $_.approval_state -eq "pending_apply_approval" })
    $approvedPackets = @($approvalPackets | Where-Object { $_.approval_state -eq "approved" })
    $blockedPackets = @($approvalPackets | Where-Object { $_.approval_state -eq "blocked" })

    Write-Host "Approval summary:"
    Write-Host "  Source: $($inputs.approval_inbox)"
    Write-Host "  Inbox: $($approvalInbox.inbox_name)"
    Write-Host "  Mode: $($approvalInbox.mode)"
    Write-Host "  Total approval packets: $($approvalPackets.Count)"
    Write-Host "  Pending APPLY approvals: $($pendingApprovals.Count)"
    Write-Host "  Approved packets: $($approvedPackets.Count)"
    Write-Host "  Blocked packets: $($blockedPackets.Count)"
    Write-Host ""
}

if ($null -eq $validatorChain) {
    Write-MissingInput -Name "Validator" -Path $validatorPath
} else {
    $validators = @($validatorChain.validators)
    $requiredValidators = @($validators | Where-Object { $_.validator_type -eq "required" })
    $optionalValidators = @($validators | Where-Object { $_.validator_type -eq "optional" })
    $blockedValidators = @($validators | Where-Object { $_.blocked -eq $true -or $_.validator_type -eq "blocked" })
    $readyValidators = @($validators | Where-Object { $_.status -eq "ready" })

    Write-Host "Validator summary:"
    Write-Host "  Source: $($inputs.validator_chain)"
    Write-Host "  Chain: $($validatorChain.chain_name)"
    Write-Host "  Mode: $($validatorChain.mode)"
    Write-Host "  Total validators: $($validators.Count)"
    Write-Host "  Required validators: $($requiredValidators.Count)"
    Write-Host "  Optional validators: $($optionalValidators.Count)"
    Write-Host "  Ready validators: $($readyValidators.Count)"
    Write-Host "  Blocked validators: $($blockedValidators.Count)"
    Write-Host ""
}

if ($null -eq $recoveryBootstrap) {
    Write-MissingInput -Name "Recovery" -Path $recoveryPath
} else {
    $state = $recoveryBootstrap.last_known_orchestration_state
    $unfinishedPackets = @($recoveryBootstrap.unfinished_packets)
    $pendingRecoveryApprovals = @($recoveryBootstrap.pending_approvals)
    $lastValidatedAt = if ([string]::IsNullOrWhiteSpace([string]$state.last_validated_at)) { "UNKNOWN" } else { $state.last_validated_at }

    Write-Host "Recovery summary:"
    Write-Host "  Source: $($inputs.recovery_bootstrap)"
    Write-Host "  Bootstrap: $($recoveryBootstrap.bootstrap_name)"
    Write-Host "  Mode: $($recoveryBootstrap.mode)"
    Write-Host "  Last phase: $($state.phase)"
    Write-Host "  Last stage: $($state.stage)"
    Write-Host "  Last state: $($state.state)"
    Write-Host "  Last checkpoint: $($state.last_checkpoint)"
    Write-Host "  Last validated at: $lastValidatedAt"
    Write-Host "  Unfinished packets: $($unfinishedPackets.Count)"
    Write-Host "  Pending recovery approvals: $($pendingRecoveryApprovals.Count)"
    Write-Host ""
}

Write-Host "Snapshot safety rules:"
foreach ($rule in @($snapshot.safety_rules)) {
    Write-Host "  - $rule"
}
Write-Host ""

Write-Host "Next safe action: $($snapshot.next_safe_action)"
