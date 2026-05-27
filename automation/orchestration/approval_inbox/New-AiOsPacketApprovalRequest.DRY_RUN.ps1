[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$PacketPath,
    [switch]$OutputJson
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-AiOsProp {
    param($Object, [string[]]$Names)

    foreach ($name in $Names) {
        if ($null -ne $Object -and $Object.PSObject.Properties.Name -contains $name) {
            return $Object.$name
        }
    }
    return $null
}

if (-not (Test-Path -LiteralPath $PacketPath -PathType Leaf)) {
    throw "Packet file not found: $PacketPath"
}

$packet = Get-Content -LiteralPath $PacketPath -Raw | ConvertFrom-Json
$packetId = [string](Get-AiOsProp -Object $packet -Names @("packet_id", "id"))
if ([string]::IsNullOrWhiteSpace($packetId)) {
    throw "Packet is missing packet_id."
}

$approvalId = "approval-$packetId"
$allowedPaths = @(Get-AiOsProp -Object $packet -Names @("allowed_paths", "allowed_write_boundary"))
$blockedPaths = @(Get-AiOsProp -Object $packet -Names @("blocked_paths", "forbidden_paths"))

$preview = [pscustomobject]@{
    schema = "AIOS_PACKET_APPROVAL_REQUEST_PREVIEW.v1"
    mode = "DRY_RUN"
    approval_id = $approvalId
    packet_id = $packetId
    requested_action = "APPROVE_PACKET_FOR_WORKER_PREVIEW"
    requested_mode = [string](Get-AiOsProp -Object $packet -Names @("mode"))
    approval_status = "pending_review"
    approved_by_human = $false
    allowed_paths = $allowedPaths
    blocked_paths = $blockedPaths
    validator_chain_required = $true
    commit_package_required = $false
    push_blocked_until_final_review = $true
    approval_notes = @(
        "This DRY_RUN preview does not authorize APPLY.",
        "Human approval is required before packet assignment or worker execution."
    )
    source_packet_path = $PacketPath
    writes_performed = 0
    commit_performed = "NO"
    push_performed = "NO"
    next_safe_action = "Human operator reviews this approval request preview."
}

if ($OutputJson) {
    $preview | ConvertTo-Json -Depth 10
    exit 0
}

Write-Host "AI_OS Packet Approval Request Preview"
Write-Host "Mode: DRY_RUN"
Write-Host "Approval id: $($preview.approval_id)"
Write-Host "Packet id: $($preview.packet_id)"
Write-Host "Approval status: $($preview.approval_status)"
Write-Host "Writes performed: 0"
Write-Host "Next safe action: $($preview.next_safe_action)"
