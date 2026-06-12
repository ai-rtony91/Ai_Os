param(
    [string]$PacketRoot = "automation/orchestration/work_packets/active",
    [string]$ApprovalRoot = "automation/orchestration/approval_inbox",
    [switch]$QuietJson,
    [switch]$OutputJson
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

$approvedStatuses = @("approved", "approved_for_apply", "apply_approved", "completed")
$matches = @()
$pendingReviews = @()

function Get-AiOsApprovalPacketId {
    param([object]$Approval)

    foreach ($name in @("packet_id", "packetId", "work_packet_id", "approved_packet_id")) {
        if ($Approval.PSObject.Properties.Name -contains $name) {
            return [string]$Approval.$name
        }
    }

    return ""
}

$packets = @(Get-ChildItem -LiteralPath $PacketRoot -Filter "*.json" -File -ErrorAction SilentlyContinue)
$approvals = @(Get-ChildItem -LiteralPath $ApprovalRoot -Filter "APPLY_APPROVAL_GATE*.json" -File -ErrorAction SilentlyContinue)

foreach ($packetFile in $packets) {
    $packet = Get-Content -Raw -LiteralPath $packetFile.FullName | ConvertFrom-Json

    if ($packet.status -ne "awaiting_approval") {
        continue
    }

    foreach ($approvalFile in $approvals) {
        $approval = Get-Content -Raw -LiteralPath $approvalFile.FullName | ConvertFrom-Json
        $approvalPacketId = Get-AiOsApprovalPacketId -Approval $approval
        $approvalStatus = if ($approval.PSObject.Properties.Name -contains "approval_status") { [string]$approval.approval_status } else { "" }
        $approvedByHuman = ($approval.PSObject.Properties.Name -contains "approved_by_human" -and $approval.approved_by_human -eq $true)

        if ($approvalPacketId -ne [string]$packet.packet_id) {
            continue
        }

        if ($approvedByHuman -and $approvalStatus -in $approvedStatuses) {
            $matches += [pscustomobject]@{
                packet_id = $packet.packet_id
                packet_status = $packet.status
                approval_file = $approvalFile.FullName
                approval_status = $approvalStatus
                approved_by_human = $true
                recommended_next = "Use separately approved APPLY helper after canonical approval gate evidence is verified."
            }
        } else {
            $pendingReviews += [pscustomobject]@{
                packet_id = $packet.packet_id
                packet_status = $packet.status
                approval_file = $approvalFile.FullName
                approval_status = $approvalStatus
                approved_by_human = $approvedByHuman
                recommended_next = "Human Owner review is still required; no approval mutation was performed."
            }
        }
    }
}

$result = [pscustomobject]@{
    mode = "READ_ONLY"
    approval_source = $ApprovalRoot
    matches_found = @($matches).Count
    matches = $matches
    pending_review_count = @($pendingReviews).Count
    pending_reviews = $pendingReviews
}

if ($QuietJson -or $OutputJson) {
    $result | ConvertTo-Json -Depth 8
    exit 0
}

Write-Host "COPY START - Find-AiOsApprovalMatch.DRY_RUN.ps1"
Write-Host "AI_OS Auto Approval Detection" -ForegroundColor Cyan
Write-Host "approval_source: $($result.approval_source)"
Write-Host "matches_found: $($result.matches_found)"
Write-Host "pending_review_count: $($result.pending_review_count)"

foreach ($match in @($matches)) {
    Write-Host ""
    Write-Host "MATCH"
    Write-Host "packet_id: $($match.packet_id)"
    Write-Host "packet_status: $($match.packet_status)"
    Write-Host "approval_file: $($match.approval_file)"
    Write-Host "approval_status: $($match.approval_status)"
    Write-Host "recommended_next: $($match.recommended_next)"
}

foreach ($pending in @($pendingReviews)) {
    Write-Host ""
    Write-Host "PENDING REVIEW"
    Write-Host "packet_id: $($pending.packet_id)"
    Write-Host "packet_status: $($pending.packet_status)"
    Write-Host "approval_file: $($pending.approval_file)"
    Write-Host "approval_status: $($pending.approval_status)"
    Write-Host "recommended_next: $($pending.recommended_next)"
}

Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host "COPY END - Find-AiOsApprovalMatch.DRY_RUN.ps1"
