param(
    [switch]$Apply
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

Write-Host "COPY START — Invoke-AiOsSupervisorLoop.DRY_RUN.ps1"
Write-Host "AI_OS Autonomous Supervisor Loop" -ForegroundColor Cyan
Write-Host "Mode: $(if ($Apply) { 'APPLY' } else { 'DRY_RUN' })"
Write-Host ""

$nextJson = powershell -ExecutionPolicy Bypass -File automation/orchestration/next_step/Resolve-AiOsNextStep.DRY_RUN.ps1 -QuietJson | ConvertFrom-Json

Write-Host "PACKET"
Write-Host "packet_id: $($nextJson.packet_id)"
Write-Host "status: $($nextJson.status)"
Write-Host "next_step: $($nextJson.next_step)"
Write-Host ""

$command = ""

switch ($nextJson.status) {
    "active" {
        $command = "Move packet to routed."
        $targetState = "routed"
    }
    "routed" {
        $command = "Move packet to dry_run_done after DRY_RUN work."
        $targetState = "dry_run_done"
    }
    "dry_run_done" {
        $command = "Move packet to awaiting_approval."
        $targetState = "awaiting_approval"
    }
    "awaiting_approval" {
        $command = "Stop for human approval."
        $targetState = ""
    }
    "approved" {
        $command = "Move packet to applying."
        $targetState = "applying"
    }
    "applying" {
        $command = "Move packet to validated after validators pass."
        $targetState = "validated"
    }
    "validated" {
        $command = "Move packet to complete."
        $targetState = "complete"
    }
    "complete" {
        $command = "Open or review PR gate."
        $targetState = ""
    }
    default {
        $command = "Stop and inspect packet manually."
        $targetState = ""
    }
}

Write-Host "SUPERVISOR DECISION"
Write-Host "decision: $command"
Write-Host "target_state: $targetState"
Write-Host ""

if ([string]::IsNullOrWhiteSpace($targetState)) {
    Write-Host "Action taken: NO"
    Write-Host "Reason: approval, PR, complete, blocked, failed, or unknown state requires operator."
} else {
    $packetPath = $nextJson.latest_packet_file
    Write-Host "packet_path: $packetPath"

    if ($Apply) {
        powershell -ExecutionPolicy Bypass -File checkpoints/verify_success.ps1

        if ($LASTEXITCODE -ne 0) {
            Write-Host ''
            Write-Host 'SUPERVISOR BLOCKED: proof verification failed' -ForegroundColor Red
            exit 1
        }

        powershell -ExecutionPolicy Bypass -File automation/orchestration/work_packets/Move-AiOsPacketState.ps1 -PacketPath $packetPath -TargetState $targetState -Worker "supervisor_loop" -Apply
        Write-Host "Action taken: YES"
    } else {
        powershell -ExecutionPolicy Bypass -File checkpoints/verify_success.ps1

        if ($LASTEXITCODE -ne 0) {
            Write-Host ''
            Write-Host 'SUPERVISOR BLOCKED: proof verification failed' -ForegroundColor Red
            exit 1
        }

        powershell -ExecutionPolicy Bypass -File automation/orchestration/work_packets/Move-AiOsPacketState.ps1 -PacketPath $packetPath -TargetState $targetState -Worker "supervisor_loop"
        Write-Host "Action taken: NO"
    }
}

Write-Host ""
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host "COPY END — Invoke-AiOsSupervisorLoop.DRY_RUN.ps1"

