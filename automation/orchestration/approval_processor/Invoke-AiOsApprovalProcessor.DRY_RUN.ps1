param(
    [string]$ApprovalRoot = "automation/orchestration/approvals",
    [string]$PacketRoot = "automation/orchestration/work_packets",
    [switch]$Apply
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

Write-Host "COPY START — Invoke-AiOsApprovalProcessor.DRY_RUN.ps1"
Write-Host "AI_OS Approval Processor" -ForegroundColor Cyan
Write-Host "Mode: $(if ($Apply) { 'APPLY' } else { 'DRY_RUN' })"
Write-Host ""

$approvalFiles = Get-ChildItem -LiteralPath $ApprovalRoot -Filter "APPROVE_PR_*.json" -File -ErrorAction SilentlyContinue
$applyApprovalStatuses = @("approved", "approved_for_apply", "apply_approved", "completed")

function Get-AiOsApprovalPacketId {
    param([object]$Approval)

    foreach ($name in @("packet_id", "packetId", "work_packet_id", "approved_packet_id")) {
        if ($Approval.PSObject.Properties.Name -contains $name) {
            return [string]$Approval.$name
        }
    }

    return ""
}

function Test-AiOsApprovalAppliesToPacket {
    param(
        [object]$Approval,
        [object]$Packet,
        [bool]$ApplyMode
    )

    $approvalPacketId = Get-AiOsApprovalPacketId -Approval $Approval
    $packetId = [string]$Packet.packet_id

    if ([string]::IsNullOrWhiteSpace($approvalPacketId)) {
        Write-Host "Approval skipped: missing packet_id binding"
        return $false
    }

    if ($approvalPacketId -ne $packetId) {
        Write-Host "Approval skipped: packet_id mismatch approval=$approvalPacketId packet=$packetId"
        return $false
    }

    if ($ApplyMode) {
        if ([string]$Approval.approved_mode -eq "DRY_RUN_ONLY") {
            Write-Host "Approval skipped: approved_mode is DRY_RUN_ONLY"
            return $false
        }

        if (($Approval.PSObject.Properties.Name -contains "approval_status") -and
            [string]$Approval.approval_status -notin $applyApprovalStatuses) {
            Write-Host "Approval skipped: approval_status is not APPLY-approved"
            return $false
        }
    }

    return $true
}

if ($approvalFiles.Count -eq 0) {
    Write-Host "No approval files found."
    Write-Host "COPY END — Invoke-AiOsApprovalProcessor.DRY_RUN.ps1"
    exit 0
}

foreach ($approvalFile in $approvalFiles) {

    Write-Host "APPROVAL FILE"
    Write-Host $approvalFile.FullName

    $approval = Get-Content -Raw -LiteralPath $approvalFile.FullName | ConvertFrom-Json

    if (-not $approval.approved) {
        Write-Host "Approval skipped: approved=false"
        continue
    }

    $packetFiles = Get-ChildItem "$PacketRoot/active" -Filter "*.json" -File -ErrorAction SilentlyContinue

    foreach ($packetFile in $packetFiles) {

        $packet = Get-Content -Raw -LiteralPath $packetFile.FullName | ConvertFrom-Json

        if ($packet.status -ne "awaiting_approval") {
            continue
        }

        Write-Host ""
        Write-Host "MATCHED PACKET"
        Write-Host "packet_id: $($packet.packet_id)"
        Write-Host "status: $($packet.status)"
        Write-Host "approval_pr: $($approval.pr_number)"

        if (-not (Test-AiOsApprovalAppliesToPacket -Approval $approval -Packet $packet -ApplyMode ([bool]$Apply))) {
            continue
        }

        if ($Apply) {

            powershell -ExecutionPolicy Bypass -File `
            automation/orchestration/work_packets/Move-AiOsPacketState.ps1 `
            -PacketPath $packetFile.FullName `
            -TargetState approved `
            -Worker approval_processor `
            -Apply

            Write-Host "Approval action applied: YES"

        } else {

            powershell -ExecutionPolicy Bypass -File `
            automation/orchestration/work_packets/Move-AiOsPacketState.ps1 `
            -PacketPath $packetFile.FullName `
            -TargetState approved `
            -Worker approval_processor

            Write-Host "Approval action applied: NO"
        }
    }
}

Write-Host ""
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host "COPY END — Invoke-AiOsApprovalProcessor.DRY_RUN.ps1"
