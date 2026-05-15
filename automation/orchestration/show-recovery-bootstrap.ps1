Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$orchestrationRoot = $PSScriptRoot
$bootstrapPath = Join-Path $orchestrationRoot "recovery_bootstrap.example.json"

function Read-JsonFile {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "Required file was not found: $Path"
    }

    Get-Content -Raw -LiteralPath $Path | ConvertFrom-Json
}

function Write-PathList {
    param(
        [Parameter(Mandatory = $true)]
        [object[]]$Paths
    )

    if ($Paths.Count -eq 0) {
        Write-Host "    - None"
        return
    }

    foreach ($path in $Paths) {
        Write-Host "    - $path"
    }
}

$bootstrap = Read-JsonFile -Path $bootstrapPath
$state = $bootstrap.last_known_orchestration_state
$unfinishedPackets = @($bootstrap.unfinished_packets)
$pendingApprovals = @($bootstrap.pending_approvals)
$recoveryNextAction = $bootstrap.recovery_next_action

Write-Host "AI_OS Recovery Bootstrap Display"
Write-Host "Mode: $($bootstrap.mode)"
Write-Host "Bootstrap: $($bootstrap.bootstrap_name)"
Write-Host "Purpose: $($bootstrap.purpose)"
Write-Host ""
Write-Host "Safety: display-only. No files are modified. No startup tasks or scheduled tasks are created. Nothing is launched."
Write-Host ""

Write-Host "Last known orchestration state:"
Write-Host "  Phase: $($state.phase)"
Write-Host "  Stage: $($state.stage)"
Write-Host "  State: $($state.state)"
Write-Host "  Last checkpoint: $($state.last_checkpoint)"
$lastValidatedAt = if ([string]::IsNullOrWhiteSpace([string]$state.last_validated_at)) { "UNKNOWN" } else { $state.last_validated_at }
Write-Host "  Last validated at: $lastValidatedAt"
Write-Host "  Git state: $($state.git_state)"
Write-Host ""

Write-Host "Unfinished packets:"
if ($unfinishedPackets.Count -eq 0) {
    Write-Host "  None"
    Write-Host ""
} else {
    foreach ($packet in $unfinishedPackets) {
        Write-Host "  Packet: $($packet.packet_id)"
        Write-Host "    Name: $($packet.packet_name)"
        Write-Host "    Status: $($packet.status)"
        Write-Host "    Owner: $($packet.owner)"
        Write-Host "    Next step: $($packet.next_step)"
        Write-Host "    Allowed paths:"
        Write-PathList -Paths @($packet.allowed_paths)
        Write-Host "    Blocked paths:"
        Write-PathList -Paths @($packet.blocked_paths)
        Write-Host ""
    }
}

Write-Host "Pending approvals:"
if ($pendingApprovals.Count -eq 0) {
    Write-Host "  None"
    Write-Host ""
} else {
    foreach ($approval in $pendingApprovals) {
        Write-Host "  Approval: $($approval.approval_id)"
        Write-Host "    Name: $($approval.approval_name)"
        Write-Host "    State: $($approval.approval_state)"
        Write-Host "    Required before: $($approval.required_before)"
        Write-Host "    Notes: $($approval.notes)"
        Write-Host ""
    }
}

Write-Host "Recovery next action:"
Write-Host "  Action: $($recoveryNextAction.action)"
Write-Host "  Command: $($recoveryNextAction.command)"
Write-Host "  Stop condition: $($recoveryNextAction.stop_condition)"
Write-Host ""

Write-Host "Safety notes:"
foreach ($note in @($bootstrap.safety_notes)) {
    Write-Host "  - $note"
}
Write-Host ""

Write-Host "Next safe action: run the listed read-only validation command, then review git status before any separate commit approval."
