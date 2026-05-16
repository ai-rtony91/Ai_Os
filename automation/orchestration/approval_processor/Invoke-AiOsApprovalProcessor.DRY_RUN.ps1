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
