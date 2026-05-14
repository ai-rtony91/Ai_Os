[CmdletBinding()]
param(
    [string]$PacketTablePath = "Reports/dispatcher/runtime/packet_runtime_table.example.json",
    [string]$RecoveryStatusPath = "Reports/dispatcher/runtime/recovery_runtime_status.example.json"
)

$ErrorActionPreference = "Stop"

function Test-AIOSRecoveryResume {
    [CmdletBinding()]
    param(
        [string]$PacketTablePath = "Reports/dispatcher/runtime/packet_runtime_table.example.json",
        [string]$RecoveryStatusPath = "Reports/dispatcher/runtime/recovery_runtime_status.example.json"
    )

    $findings = New-Object System.Collections.Generic.List[object]
    $checked = @($PacketTablePath, $RecoveryStatusPath)
    $status = "PASS"

    foreach ($path in $checked) {
        if (-not (Test-Path -LiteralPath $path)) {
            $status = "REVIEW_REQUIRED"
            $findings.Add([pscustomobject]@{ status = "REVIEW_REQUIRED"; message = "Recovery input is missing: $path" }) | Out-Null
        }
    }

    if ($findings.Count -gt 0) {
        return [pscustomobject]@{
            schema = "AIOS_VALIDATOR_RESULT.v1"
            validator = "recovery_resume"
            stage = "recovery_resume"
            status = $status
            findings = $findings.ToArray()
            checked_paths = $checked
            blocked_actions = @("resume_apply", "reassign_packet", "release_lock", "commit", "push")
            next_safe_action = "Review missing recovery evidence before resuming work."
        }
    }

    try {
        $packetData = Get-Content -LiteralPath $PacketTablePath -Raw | ConvertFrom-Json
        $recoveryData = Get-Content -LiteralPath $RecoveryStatusPath -Raw | ConvertFrom-Json
    }
    catch {
        return [pscustomobject]@{
            schema = "AIOS_VALIDATOR_RESULT.v1"
            validator = "recovery_resume"
            stage = "recovery_resume"
            status = "FAIL"
            findings = @([pscustomobject]@{ status = "FAIL"; message = "Recovery runtime JSON could not parse."; detail = $_.Exception.Message })
            checked_paths = $checked
            blocked_actions = @("resume_apply", "reassign_packet", "release_lock", "commit", "push")
            next_safe_action = "Fix recovery JSON before resuming work."
        }
    }

    $packets = @($packetData.packets)
    foreach ($packet in $packets) {
        if ($packet.status -match "APPLY_STARTED|APPLY_INTERRUPTED") {
            $status = "BLOCKED"
            $findings.Add([pscustomobject]@{ status = "BLOCKED"; message = "Interrupted APPLY state requires human review: $($packet.packet_id)" }) | Out-Null
        }
        elseif (-not $packet.worker_id -or $packet.worker_id -eq "UNASSIGNED") {
            if ($status -ne "BLOCKED") { $status = "REVIEW_REQUIRED" }
            $findings.Add([pscustomobject]@{ status = "REVIEW_REQUIRED"; message = "Packet has no active owner: $($packet.packet_id)" }) | Out-Null
        }
    }

    if ($recoveryData.dispatcher_status -eq "REVIEW_REQUIRED" -or $recoveryData.recovery_status -eq "REVIEW_REQUIRED") {
        if ($status -ne "BLOCKED") { $status = "REVIEW_REQUIRED" }
        $findings.Add([pscustomobject]@{ status = "REVIEW_REQUIRED"; message = "Recovery status requires human review." }) | Out-Null
    }

    if ($findings.Count -eq 0) {
        $findings.Add([pscustomobject]@{ status = "PASS"; message = "No interrupted APPLY or orphan packet state was found." }) | Out-Null
    }

    [pscustomobject]@{
        schema = "AIOS_VALIDATOR_RESULT.v1"
        validator = "recovery_resume"
        stage = "recovery_resume"
        status = $status
        findings = $findings.ToArray()
        checked_paths = $checked
        blocked_actions = @("resume_apply", "reassign_packet", "release_lock", "commit", "push")
        next_safe_action = "Review packet, lock, heartbeat, and git status evidence before resuming work."
    }
}

if ($MyInvocation.InvocationName -ne ".") {
    Test-AIOSRecoveryResume -PacketTablePath $PacketTablePath -RecoveryStatusPath $RecoveryStatusPath | ConvertTo-Json -Depth 8
}
