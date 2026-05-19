Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$orchestrationRoot = $PSScriptRoot
$snapshotPath = Join-Path $orchestrationRoot "orchestration_status_snapshot.example.json"
$repoRoot = (Resolve-Path (Join-Path $orchestrationRoot "..\..")).Path

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

    if ([System.IO.Path]::IsPathRooted($FileName)) {
        return $FileName
    }

    if ($FileName -like "automation/*" -or $FileName -like "docs/*" -or $FileName -like "archive/*") {
        return (Join-Path $repoRoot $FileName)
    }

    Join-Path $orchestrationRoot $FileName
}

function Resolve-WithFallback {
    param(
        [Parameter(Mandatory = $true)][string]$Primary,
        [string]$Fallback = ""
    )

    $primaryPath = Resolve-InputPath -FileName $Primary
    if (Test-Path -LiteralPath $primaryPath) {
        $fallbackMissing = $false
        if (-not [string]::IsNullOrWhiteSpace($Fallback)) {
            $fallbackPath = Resolve-InputPath -FileName $Fallback
            $fallbackMissing = -not (Test-Path -LiteralPath $fallbackPath)
        }
        return [pscustomobject]@{ Path = $primaryPath; Source = $Primary; UsedFallback = $false; FallbackMissing = $fallbackMissing }
    }

    if (-not [string]::IsNullOrWhiteSpace($Fallback)) {
        $fallbackPath = Resolve-InputPath -FileName $Fallback
        if (Test-Path -LiteralPath $fallbackPath) {
            return [pscustomobject]@{ Path = $fallbackPath; Source = $Fallback; UsedFallback = $true; FallbackMissing = $false }
        }
    }

    return [pscustomobject]@{ Path = $primaryPath; Source = $Primary; UsedFallback = $false; FallbackMissing = $true }
}

function Get-WorkPacketFolderSummary {
    param([Parameter(Mandatory = $true)][string]$Path)

    $states = @("active", "blocked", "complete")
    $counts = [ordered]@{}
    foreach ($state in $states) {
        $statePath = Join-Path $Path $state
        $counts[$state] = if (Test-Path -LiteralPath $statePath -PathType Container) {
            @(Get-ChildItem -LiteralPath $statePath -Filter "*.json" -File).Count
        } else {
            0
        }
    }

    [pscustomobject]@{
        mode = "FOLDER_STATE"
        queue_name = "canonical work_packets folder"
        purpose = "Displays packet folder state counts from automation/orchestration/work_packets/."
        counts = $counts
    }
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

function Get-JsonValue {
    param(
        [AllowNull()]$Object,
        [Parameter(Mandatory = $true)][string]$Name,
        [string]$Default = ""
    )

    if ($null -eq $Object) { return $Default }
    if ($Object.PSObject.Properties.Name -contains $Name) {
        $value = $Object.$Name
        if ($null -ne $value -and -not [string]::IsNullOrWhiteSpace([string]$value)) {
            return $value
        }
    }
    return $Default
}

$snapshot = Read-JsonFile -Path $snapshotPath
if ($null -eq $snapshot) {
    throw "Required file was not found: $snapshotPath"
}

$inputs = $snapshot.status_inputs
$queueRef = Resolve-WithFallback -Primary $inputs.queue -Fallback $inputs.legacy_queue_fallback
$workerRef = Resolve-WithFallback -Primary $inputs.worker_registry -Fallback $inputs.legacy_worker_registry_fallback
$approvalRef = Resolve-WithFallback -Primary $inputs.approval_inbox -Fallback $inputs.legacy_approval_inbox_fallback
$validatorRef = Resolve-WithFallback -Primary $inputs.validator_chain -Fallback $inputs.legacy_validator_chain_fallback
$recoveryPath = Resolve-InputPath -FileName $inputs.recovery_bootstrap

$queue = if (Test-Path -LiteralPath $queueRef.Path -PathType Container) { Get-WorkPacketFolderSummary -Path $queueRef.Path } else { Read-JsonFile -Path $queueRef.Path }
$workerRegistry = Read-JsonFile -Path $workerRef.Path
$approvalInbox = Read-JsonFile -Path $approvalRef.Path
$validatorChain = Read-JsonFile -Path $validatorRef.Path
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
    Write-MissingInput -Name "Queue" -Path $queueRef.Path
} elseif ($queue.mode -eq "FOLDER_STATE") {
    Write-Host "Queue summary:"
    Write-Host "  Source: $($queueRef.Source)"
    Write-Host "  Queue: $($queue.queue_name)"
    Write-Host "  Mode: $($queue.mode)"
    Write-Host "  Active packets: $($queue.counts.active)"
    Write-Host "  Blocked packets: $($queue.counts.blocked)"
    Write-Host "  Complete packets: $($queue.counts.complete)"
    if ($queueRef.FallbackMissing) {
        Write-Host "  Legacy fallback not found; canonical source used."
    } else {
        Write-Host "  Legacy fallback: available but not required."
    }
    Write-Host ""
} else {
    $packets = @($queue.packets)
    $availablePackets = @($packets | Where-Object { $_.status -eq "available" })
    $assignedPackets = @($packets | Where-Object { $null -ne $_.assigned_worker_id })
    $approvalRequiredPackets = @($packets | Where-Object { $_.approval_required -eq $true })
    $validatorRequiredPackets = @($packets | Where-Object { $_.validator_required -eq $true })

    Write-Host "Queue summary:"
    Write-Host "  Source: $($queueRef.Source)"
    if ($queueRef.UsedFallback) { Write-Host "  Fallback: legacy queue file used because canonical path was unavailable." }
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
    Write-MissingInput -Name "Worker" -Path $workerRef.Path
} else {
    $workers = @($workerRegistry.workers)
    $standbyWorkers = @($workers | Where-Object { (Get-JsonValue -Object $_ -Name "status") -eq "standby" })
    $assignedWorkers = @($workers | Where-Object { -not [string]::IsNullOrWhiteSpace((Get-JsonValue -Object $_ -Name "assigned_packet_id")) })

    Write-Host "Worker summary:"
    Write-Host "  Source: $($workerRef.Source)"
    if ($workerRef.UsedFallback) { Write-Host "  Fallback: legacy worker registry file used because canonical path was unavailable." }
    if (-not $workerRef.UsedFallback -and $workerRef.FallbackMissing) { Write-Host "  Legacy fallback not found; canonical source used." }
    Write-Host "  Registry: $(Get-JsonValue -Object $workerRegistry -Name 'registry_name' -Default (Get-JsonValue -Object $workerRegistry -Name 'registry_id' -Default 'UNKNOWN'))"
    Write-Host "  Mode: $(Get-JsonValue -Object $workerRegistry -Name 'mode' -Default 'canonical registry')"
    Write-Host "  Total workers: $($workers.Count)"
    Write-Host "  Standby workers: $($standbyWorkers.Count)"
    Write-Host "  Assigned workers: $($assignedWorkers.Count)"
    Write-Host ""
}

if ($null -eq $approvalInbox) {
    Write-MissingInput -Name "Approval" -Path $approvalRef.Path
} elseif ($approvalInbox.PSObject.Properties.Name -contains "packets") {
    $approvalPackets = @($approvalInbox.packets)
    $pendingApprovals = @($approvalPackets | Where-Object { $_.approval_state -eq "pending_apply_approval" })
    $approvedPackets = @($approvalPackets | Where-Object { $_.approval_state -eq "approved" })
    $blockedPackets = @($approvalPackets | Where-Object { $_.approval_state -eq "blocked" })

    Write-Host "Approval summary:"
    Write-Host "  Source: $($approvalRef.Source)"
    if ($approvalRef.UsedFallback) { Write-Host "  Fallback: legacy approval inbox file used because canonical path was unavailable." }
    if (-not $approvalRef.UsedFallback -and $approvalRef.FallbackMissing) { Write-Host "  Legacy fallback not found; canonical source used." }
    Write-Host "  Inbox: $($approvalInbox.inbox_name)"
    Write-Host "  Mode: $($approvalInbox.mode)"
    Write-Host "  Total approval packets: $($approvalPackets.Count)"
    Write-Host "  Pending APPLY approvals: $($pendingApprovals.Count)"
    Write-Host "  Approved packets: $($approvedPackets.Count)"
    Write-Host "  Blocked packets: $($blockedPackets.Count)"
    Write-Host ""
} else {
    Write-Host "Approval summary:"
    Write-Host "  Source: $($approvalRef.Source)"
    if ($approvalRef.FallbackMissing) { Write-Host "  Legacy fallback not found; canonical source used." }
    Write-Host "  Inbox: $($approvalInbox.schema)"
    Write-Host "  Mode: canonical single approval record"
    Write-Host "  Approval ID: $($approvalInbox.approval_id)"
    Write-Host "  Packet ID: $($approvalInbox.packet_id)"
    Write-Host "  Approval status: $($approvalInbox.approval_status)"
    Write-Host "  Approved by human: $($approvalInbox.approved_by_human)"
    Write-Host ""
}

if ($null -eq $validatorChain) {
    Write-MissingInput -Name "Validator" -Path $validatorRef.Path
} else {
    $validators = @($validatorChain.validators)
    $requiredValidators = @($validators | Where-Object { (Get-JsonValue -Object $_ -Name "validator_type") -eq "required" -or (Get-JsonValue -Object $_ -Name "required") -eq "True" })
    $optionalValidators = @($validators | Where-Object { (Get-JsonValue -Object $_ -Name "validator_type") -eq "optional" -or (Get-JsonValue -Object $_ -Name "required") -eq "False" })
    $blockedValidators = @($validators | Where-Object { (Get-JsonValue -Object $_ -Name "blocked") -eq "True" -or (Get-JsonValue -Object $_ -Name "validator_type") -eq "blocked" })
    $readyValidators = @($validators | Where-Object { (Get-JsonValue -Object $_ -Name "status") -eq "ready" -or (Get-JsonValue -Object $_ -Name "required") -eq "True" })

    Write-Host "Validator summary:"
    Write-Host "  Source: $($validatorRef.Source)"
    if ($validatorRef.UsedFallback) { Write-Host "  Fallback: legacy validator chain file used because canonical path was unavailable." }
    if (-not $validatorRef.UsedFallback -and $validatorRef.FallbackMissing) { Write-Host "  Legacy fallback not found; canonical source used." }
    Write-Host "  Chain: $(Get-JsonValue -Object $validatorChain -Name 'chain_name' -Default (Get-JsonValue -Object $validatorChain -Name 'chain_id' -Default 'UNKNOWN'))"
    Write-Host "  Mode: $(Get-JsonValue -Object $validatorChain -Name 'mode' -Default 'DRY_RUN_READ_ONLY')"
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
