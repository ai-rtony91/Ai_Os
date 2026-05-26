param(
    [switch]$QuietJson
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

$packetRoot = "automation/orchestration/work_packets/active"
$approvalRoot = "automation/orchestration/approvals"

$matches = @()

$packets = @(Get-ChildItem $packetRoot -Filter "*.json" -File -ErrorAction SilentlyContinue)
$approvals = @(Get-ChildItem $approvalRoot -Filter "APPROVE_PR_*.json" -File -ErrorAction SilentlyContinue)

foreach ($packetFile in $packets) {
    $packet = Get-Content -Raw $packetFile.FullName | ConvertFrom-Json

    if ($packet.status -ne "awaiting_approval") {
        continue
    }

    foreach ($approvalFile in $approvals) {
        $approval = Get-Content -Raw $approvalFile.FullName | ConvertFrom-Json

        if ($approval.approved -eq $true) {
            $matches += [pscustomobject]@{
                packet_id = $packet.packet_id
                packet_status = $packet.status
                approval_file = $approvalFile.FullName
                pr_number = $approval.pr_number
        recommended_next = "Use separately approved APPLY helper after packet approval is verified."
            }
        }
    }
}

$result = [pscustomobject]@{
    mode = "READ_ONLY"
    matches_found = @($matches).Count
    matches = $matches
}

if ($QuietJson) {
    $result | ConvertTo-Json -Depth 8
    exit 0
}

Write-Host "COPY START - Find-AiOsApprovalMatch.DRY_RUN.ps1"
Write-Host "AI_OS Auto Approval Detection" -ForegroundColor Cyan
Write-Host "matches_found: $($result.matches_found)"

foreach ($match in @($matches)) {
    Write-Host ""
    Write-Host "MATCH"
    Write-Host "packet_id: $($match.packet_id)"
    Write-Host "packet_status: $($match.packet_status)"
    Write-Host "approval_file: $($match.approval_file)"
    Write-Host "pr_number: $($match.pr_number)"
    Write-Host "recommended_next: $($match.recommended_next)"
}

Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host "COPY END - Find-AiOsApprovalMatch.DRY_RUN.ps1"
