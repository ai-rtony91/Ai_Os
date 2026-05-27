[CmdletBinding()]
param(
    [switch]$OutputJson
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Resolve-AiOsPath {
    param([Parameter(Mandatory = $true)][string]$Path)

    if ([System.IO.Path]::IsPathRooted($Path)) {
        return $Path
    }

    return Join-Path (Get-Location).Path $Path
}

function Get-AiOsFileCount {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [string]$Filter = "*.json"
    )

    $full = Resolve-AiOsPath -Path $Path
    if (-not (Test-Path -LiteralPath $full -PathType Container)) { return 0 }
    return @((Get-ChildItem -LiteralPath $full -Filter $Filter -File -ErrorAction SilentlyContinue | Where-Object { $_.Name -ne ".gitkeep" })).Count
}

function Invoke-AiOsJsonHelper {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [string]$Switch = "-OutputJson"
    )

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return [pscustomobject]@{
            status = "MISSING"
            path = $Path
        }
    }

    try {
        return powershell -NoProfile -ExecutionPolicy Bypass -File $Path $Switch | ConvertFrom-Json
    }
    catch {
        return [pscustomobject]@{
            status = "ERROR"
            path = $Path
            error = $_.Exception.Message
        }
    }
}

$pendingInputCount = Get-AiOsFileCount -Path "inputs/pending" -Filter "*.txt"
$proposedPacketCount = Get-AiOsFileCount -Path "automation/orchestration/work_packets/proposed" -Filter "*.json"
$approvedPacketCount = Get-AiOsFileCount -Path "automation/orchestration/work_packets/approved" -Filter "*.json"
$activePacketCount = Get-AiOsFileCount -Path "automation/orchestration/work_packets/active" -Filter "*.json"
$completePacketCount = Get-AiOsFileCount -Path "automation/orchestration/work_packets/complete" -Filter "*.json"
$rejectedPacketCount = Get-AiOsFileCount -Path "automation/orchestration/work_packets/rejected" -Filter "*.json"

$approvalSummary = Invoke-AiOsJsonHelper -Path "automation/orchestration/approval_inbox/Get-AiOsApprovalInboxSummary.DRY_RUN.ps1" -Switch "-QuietJson"
$workerInboxPath = Resolve-AiOsPath -Path "automation/orchestration/workers/inbox/AIOS_WORKER_INBOX.json"
$workerInboxStatus = "MISSING"
$workerInboxOpenCount = 0
if (Test-Path -LiteralPath $workerInboxPath -PathType Leaf) {
    try {
        $workerInbox = Get-Content -LiteralPath $workerInboxPath -Raw | ConvertFrom-Json
        $workerInboxStatus = "FOUND"
        $workerInboxOpenCount = @($workerInbox.items | Where-Object { $_.status -in @("inbox", "claimed", "running") }).Count
    }
    catch {
        $workerInboxStatus = "ERROR"
    }
}

$recommendation = [ordered]@{
    packet_id = "NO_PACKET_RECOMMENDED"
    title = "No packet recommendation"
    reason = "No pending orchestration input was detected."
    recommended_command = "No command recommended."
    status = "NO_ACTION"
    stop_condition = "Stop after DRY_RUN recommendation."
}

if ($pendingInputCount -gt 0) {
    $recommendation = [ordered]@{
        packet_id = "NEXT-CONVERT-INPUT-TO-PACKET-PROPOSAL"
        title = "Convert pending operator input into packet proposal"
        reason = "inputs/pending contains pending .txt files."
        recommended_command = "powershell -NoProfile -ExecutionPolicy Bypass -File automation/intake/Convert-AiOsInputToPacketProposal.DRY_RUN.ps1 -InputRoot inputs -OutputJson"
        status = "RECOMMENDED"
        stop_condition = "Stop after proposal preview; do not write packet files without separate approval."
    }
}
elseif ($proposedPacketCount -gt 0) {
    $recommendation = [ordered]@{
        packet_id = "NEXT-CREATE-PACKET-APPROVAL-PREVIEW"
        title = "Create approval request preview for proposed packet"
        reason = "Proposed packets exist and need approval request preview."
        recommended_command = "powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/approval_inbox/New-AiOsPacketApprovalRequest.DRY_RUN.ps1 -PacketPath <proposed-packet-path> -OutputJson"
        status = "RECOMMENDED"
        stop_condition = "Stop after approval request preview; no approval mutation."
    }
}
elseif ($approvedPacketCount -gt 0) {
    $recommendation = [ordered]@{
        packet_id = "NEXT-CREATE-WORKER-READY-PREVIEW"
        title = "Create worker-ready packet preview"
        reason = "Approved packets exist and need worker-ready preview."
        recommended_command = "powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/workers/inbox/New-AiOsWorkerReadyPacket.DRY_RUN.ps1 -PacketPath <approved-packet-path> -OutputJson"
        status = "RECOMMENDED"
        stop_condition = "Stop after worker-ready preview; do not edit worker inbox."
    }
}
elseif ($activePacketCount -gt 0) {
    $recommendation = [ordered]@{
        packet_id = "NEXT-REVIEW-ACTIVE-PACKET-STATE"
        title = "Review active packet state"
        reason = "Active packets exist and should be reviewed before creating more work."
        recommended_command = "powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/work_packets/Get-AiOsPacketStateRecommendation.DRY_RUN.ps1 -QuietJson"
        status = "RECOMMENDED"
        stop_condition = "Stop after packet state recommendation."
    }
}

$result = [pscustomobject]@{
    schema = "AIOS_NEXT_PACKET_RECOMMENDATION.v1"
    mode = "DRY_RUN"
    generated_utc = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    state = [pscustomobject]@{
        pending_input_count = $pendingInputCount
        proposed_packet_count = $proposedPacketCount
        approved_packet_count = $approvedPacketCount
        active_packet_count = $activePacketCount
        complete_packet_count = $completePacketCount
        rejected_packet_count = $rejectedPacketCount
        approval_summary_status = if ($approvalSummary.PSObject.Properties.Name -contains "schema") { "FOUND" } else { [string]$approvalSummary.status }
        pending_approval_count = @($approvalSummary.pending_approvals).Count
        approved_action_count = @($approvalSummary.approved_actions).Count
        blocked_action_count = @($approvalSummary.blocked_actions).Count
        worker_inbox_status = $workerInboxStatus
        worker_inbox_open_count = $workerInboxOpenCount
    }
    recommendation = [pscustomobject]$recommendation
    writes_performed = 0
    worker_execution_performed = "NO"
    commit_performed = "NO"
    push_performed = "NO"
    next_safe_action = $recommendation.recommended_command
}

if ($OutputJson) {
    $result | ConvertTo-Json -Depth 10
    exit 0
}

Write-Host "AI_OS Next Packet Recommendation"
Write-Host "Mode: DRY_RUN"
Write-Host "Recommendation: $($result.recommendation.title)"
Write-Host "Reason: $($result.recommendation.reason)"
Write-Host "Writes performed: 0"
Write-Host "Worker execution performed: NO"
Write-Host "Next safe action: $($result.next_safe_action)"
