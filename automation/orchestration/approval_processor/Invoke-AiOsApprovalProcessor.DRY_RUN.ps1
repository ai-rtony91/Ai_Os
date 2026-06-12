param(
    [string]$ApprovalRoot = "automation/orchestration/approval_inbox",
    [string]$PacketRoot = "automation/orchestration/work_packets",
    [switch]$QuietJson,
    [switch]$OutputJson
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

$applyApprovalStatuses = @("approved", "approved_for_apply", "apply_approved", "completed")
$approvalFiles = @(Get-ChildItem -LiteralPath $ApprovalRoot -Filter "APPLY_APPROVAL_GATE*.json" -File -ErrorAction SilentlyContinue)
$activePacketRoot = Join-Path $PacketRoot "active"
$packetFiles = @(Get-ChildItem -LiteralPath $activePacketRoot -Filter "*.json" -File -ErrorAction SilentlyContinue)
$reviews = @()

function Get-AiOsApprovalPacketId {
    param([object]$Approval)

    foreach ($name in @("packet_id", "packetId", "work_packet_id", "approved_packet_id")) {
        if ($Approval.PSObject.Properties.Name -contains $name) {
            return [string]$Approval.$name
        }
    }

    return ""
}

function Test-AiOsApprovalIsExplicit {
    param([object]$Approval)

    $approvalStatus = if ($Approval.PSObject.Properties.Name -contains "approval_status") { [string]$Approval.approval_status } else { "" }
    $approvedByHuman = ($Approval.PSObject.Properties.Name -contains "approved_by_human" -and $Approval.approved_by_human -eq $true)
    return ($approvedByHuman -and $approvalStatus -in $applyApprovalStatuses)
}

foreach ($approvalFile in $approvalFiles) {
    try {
        $approval = Get-Content -Raw -LiteralPath $approvalFile.FullName | ConvertFrom-Json
    }
    catch {
        $reviews += [pscustomobject]@{
            approval_file = $approvalFile.FullName
            packet_id = ""
            review_status = "invalid_approval_json"
            approval_status = "UNKNOWN"
            approved_by_human = $false
            recommended_next = "Fix approval JSON before any packet-state change."
            mutation_performed = "NO"
        }
        continue
    }

    $approvalPacketId = Get-AiOsApprovalPacketId -Approval $approval
    $approvalStatus = if ($approval.PSObject.Properties.Name -contains "approval_status") { [string]$approval.approval_status } else { "UNKNOWN" }
    $approvedByHuman = ($approval.PSObject.Properties.Name -contains "approved_by_human" -and $approval.approved_by_human -eq $true)

    if ([string]::IsNullOrWhiteSpace($approvalPacketId)) {
        $reviews += [pscustomobject]@{
            approval_file = $approvalFile.FullName
            packet_id = ""
            review_status = "skipped_missing_packet_id"
            approval_status = $approvalStatus
            approved_by_human = $approvedByHuman
            recommended_next = "Approval gate must name a packet_id before it can be matched."
            mutation_performed = "NO"
        }
        continue
    }

    foreach ($packetFile in $packetFiles) {
        $packet = Get-Content -Raw -LiteralPath $packetFile.FullName | ConvertFrom-Json
        if ($packet.status -ne "awaiting_approval") {
            continue
        }

        if ([string]$packet.packet_id -ne $approvalPacketId) {
            continue
        }

        $explicit = Test-AiOsApprovalIsExplicit -Approval $approval
        $reviews += [pscustomobject]@{
            approval_file = $approvalFile.FullName
            packet_file = $packetFile.FullName
            packet_id = [string]$packet.packet_id
            packet_status = [string]$packet.status
            review_status = if ($explicit) { "matched_explicit_approval" } else { "matched_pending_human_approval" }
            approval_status = $approvalStatus
            approved_by_human = $approvedByHuman
            recommended_next = if ($explicit) {
                "Use the separately approved packet-state mover; this DRY_RUN processor does not mutate packet state."
            } else {
                "Human Owner approval gate is not open; no packet-state change is allowed."
            }
            would_move_packet_to = if ($explicit) { "approved" } else { "" }
            mutation_performed = "NO"
        }
    }
}

$matchedExplicitCount = @($reviews | Where-Object { $_.review_status -eq "matched_explicit_approval" }).Count
$result = [pscustomobject]@{
    mode = "DRY_RUN"
    approval_source = $ApprovalRoot
    packet_source = $activePacketRoot
    approval_gate_count = $approvalFiles.Count
    active_packet_count = $packetFiles.Count
    matched_explicit_approval_count = $matchedExplicitCount
    review_count = @($reviews).Count
    reviews = $reviews
    approvals_performed = "NO"
    approval_inbox_mutated = "NO"
    packet_mutation_performed = "NO"
    commit_performed = "NO"
    push_performed = "NO"
    recommended_next = if ($matchedExplicitCount -gt 0) {
        "Run only a separately approved APPLY packet-state transition after reviewing this evidence."
    } else {
        "No explicit matching approval gate is ready for packet-state mutation."
    }
}

if ($QuietJson -or $OutputJson) {
    $result | ConvertTo-Json -Depth 8
    exit 0
}

Write-Host "COPY START - Invoke-AiOsApprovalProcessor.DRY_RUN.ps1"
Write-Host "AI_OS Approval Processor" -ForegroundColor Cyan
Write-Host "Mode: DRY_RUN"
Write-Host "Approval source: $($result.approval_source)"
Write-Host "Approval gate count: $($result.approval_gate_count)"
Write-Host "Active packet count: $($result.active_packet_count)"
Write-Host "Matched explicit approval count: $($result.matched_explicit_approval_count)"
Write-Host ""

foreach ($review in @($reviews)) {
    Write-Host "REVIEW"
    Write-Host "packet_id: $($review.packet_id)"
    Write-Host "review_status: $($review.review_status)"
    Write-Host "approval_status: $($review.approval_status)"
    Write-Host "approved_by_human: $($review.approved_by_human)"
    Write-Host "recommended_next: $($review.recommended_next)"
    Write-Host "mutation_performed: NO"
    Write-Host ""
}

if ($reviews.Count -eq 0) {
    Write-Host "No canonical approval gate matched an awaiting-approval active packet."
}

Write-Host "Approvals performed: NO"
Write-Host "Approval inbox mutated: NO"
Write-Host "Packet mutation performed: NO"
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host "COPY END - Invoke-AiOsApprovalProcessor.DRY_RUN.ps1"
