param(
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

Write-Host "COPY START — Invoke-AiOsSupervisorLoop.DRY_RUN.ps1"
Write-Host "AI_OS Autonomous Supervisor Loop" -ForegroundColor Cyan
Write-Host "Mode: DRY_RUN"
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

    Write-Host "Would move packet to: $targetState"
    Write-Host "Action taken: NO"
    Write-Host "Mutation skipped: YES - DRY_RUN supervisor cannot verify proof or move packet state."
}

Write-Host ""
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host "COPY END — Invoke-AiOsSupervisorLoop.DRY_RUN.ps1"

