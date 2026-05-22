[CmdletBinding()]
param(
    [string]$InboxPath = "automation/orchestration/approval_inbox",
    [switch]$QuietJson
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

function Read-AiOsJsonFile {
    param([string]$Path)

    try {
        return Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json
    }
    catch {
        return [pscustomobject]@{
            file = $Path
            approval_status = "blocked"
            requested_action = "JSON_PARSE_FAILED"
            packet_id = "UNKNOWN"
            error = $_.Exception.Message
        }
    }
}

if (-not (Test-Path -LiteralPath $InboxPath -PathType Container)) {
    throw "Approval inbox path not found: $InboxPath"
}

$approvalFiles = @(Get-ChildItem -LiteralPath $InboxPath -File -Filter "*.json" -ErrorAction SilentlyContinue | Where-Object { $_.Name -notlike "*.example.json" } | Sort-Object Name)
$pendingApprovals = @()
$approvedActions = @()
$blockedActions = @()

foreach ($file in $approvalFiles) {
    $item = Read-AiOsJsonFile -Path $file.FullName
    $status = if ($item.approval_status) { [string]$item.approval_status } else { "UNKNOWN" }
    $packetId = if ($item.packet_id) { [string]$item.packet_id } else { "UNKNOWN" }
    $requestedAction = if ($item.requested_action) { [string]$item.requested_action } elseif ($item.requested_mode) { [string]$item.requested_mode } else { "UNKNOWN" }

    $summary = [ordered]@{
        file = $file.Name
        packet_id = $packetId
        requested_action = $requestedAction
        approval_status = $status
        risk_level = if ($item.risk_level) { [string]$item.risk_level } else { "UNKNOWN" }
    }

    if ($status -in @("approved_for_apply", "approved")) {
        $approvedActions += [pscustomobject]$summary
    }
    elseif ($status -in @("blocked", "rejected", "expired") -or $item.error) {
        $blockedActions += [pscustomobject]$summary
    }
    else {
        $pendingApprovals += [pscustomobject]$summary
    }
}

$nextSafeCommand = "powershell -ExecutionPolicy Bypass -File automation/orchestration/approval_inbox/Get-AiOsApprovalInboxSummary.DRY_RUN.ps1"
if ($blockedActions.Count -gt 0) {
    $nextSafeCommand = "Review blocked approval items before APPLY."
}
elseif ($approvedActions.Count -gt 0) {
    $nextSafeCommand = "Review approved actions, validators, and commit package before APPLY."
}
elseif ($pendingApprovals.Count -gt 0) {
    $nextSafeCommand = "Operator reviews pending approvals; no APPLY is authorized by this summary."
}

$result = [ordered]@{
    schema = "aios_approval_inbox_summary.v1"
    mode = "DRY_RUN_READ_ONLY"
    generated_utc = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    pending_approvals = $pendingApprovals
    approved_actions = $approvedActions
    blocked_actions = $blockedActions
    next_safe_command = $nextSafeCommand
    commit_performed = "NO"
    push_performed = "NO"
}

if ($QuietJson) {
    $result | ConvertTo-Json -Depth 10
    exit 0
}

Write-Host "AIOS Approval Inbox Summary"
Write-Host "Mode: DRY_RUN_READ_ONLY"
Write-Host ""
Write-Host "pending_approvals:"
if ($pendingApprovals.Count -eq 0) { Write-Host "- none" } else { $pendingApprovals | ForEach-Object { Write-Host "- $($_.file): $($_.packet_id) [$($_.approval_status)] $($_.requested_action)" } }
Write-Host ""
Write-Host "approved_actions:"
if ($approvedActions.Count -eq 0) { Write-Host "- none" } else { $approvedActions | ForEach-Object { Write-Host "- $($_.file): $($_.packet_id) [$($_.approval_status)] $($_.requested_action)" } }
Write-Host ""
Write-Host "blocked_actions:"
if ($blockedActions.Count -eq 0) { Write-Host "- none" } else { $blockedActions | ForEach-Object { Write-Host "- $($_.file): $($_.packet_id) [$($_.approval_status)] $($_.requested_action)" } }
Write-Host ""
Write-Host "next_safe_command:"
Write-Host $nextSafeCommand
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
