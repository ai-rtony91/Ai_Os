Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$orchestrationRoot = $PSScriptRoot
$inboxPath = Join-Path $orchestrationRoot "approval_inbox.example.json"

function Read-JsonFile {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "Required file was not found: $Path"
    }

    Get-Content -Raw -LiteralPath $Path | ConvertFrom-Json
}

function Write-PacketSection {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Title,

        [Parameter(Mandatory = $true)]
        [object[]]$Packets
    )

    Write-Host $Title

    if ($Packets.Count -eq 0) {
        Write-Host "  None"
        Write-Host ""
        return
    }

    foreach ($packet in $Packets) {
        $approvedBy = if ([string]::IsNullOrWhiteSpace([string]$packet.approved_by)) { "UNAPPROVED" } else { $packet.approved_by }
        $approvalTimestamp = if ([string]::IsNullOrWhiteSpace([string]$packet.approval_timestamp)) { "none" } else { $packet.approval_timestamp }
        $blockReason = if ([string]::IsNullOrWhiteSpace([string]$packet.block_reason)) { "none" } else { $packet.block_reason }

        Write-Host "  Packet: $($packet.packet_id)"
        Write-Host "    Name: $($packet.packet_name)"
        Write-Host "    Approval state: $($packet.approval_state)"
        Write-Host "    APPLY requested: $($packet.apply_requested)"
        Write-Host "    Approved by: $approvedBy"
        Write-Host "    Approval timestamp: $approvalTimestamp"
        Write-Host "    Block reason: $blockReason"
        Write-Host "    Allowed paths:"
        foreach ($path in @($packet.allowed_paths)) {
            Write-Host "      - $path"
        }
        Write-Host "    Blocked paths:"
        foreach ($path in @($packet.blocked_paths)) {
            Write-Host "      - $path"
        }
        Write-Host "    Safety notes:"
        foreach ($note in @($packet.safety_notes)) {
            Write-Host "      - $note"
        }
        Write-Host ""
    }
}

$inbox = Read-JsonFile -Path $inboxPath
$packets = @($inbox.packets)

Write-Host "AI_OS Approval Inbox Display"
Write-Host "Mode: $($inbox.mode)"
Write-Host "Inbox: $($inbox.inbox_name)"
Write-Host "Purpose: $($inbox.purpose)"
Write-Host ""
Write-Host "Safety: display-only. No files are created. No approvals are changed. No packets are launched."
Write-Host ""

if ($packets.Count -eq 0) {
    Write-Host "Approval packets: none found in approval_inbox.example.json"
    exit 0
}

$pendingPackets = @($packets | Where-Object { $_.approval_state -eq "pending_apply_approval" })
$approvedPackets = @($packets | Where-Object { $_.approval_state -eq "approved" })
$blockedPackets = @($packets | Where-Object { $_.approval_state -eq "blocked" })

Write-Host "Approval summary:"
Write-Host "  Total packets: $($packets.Count)"
Write-Host "  Pending APPLY approvals: $($pendingPackets.Count)"
Write-Host "  Approved packets: $($approvedPackets.Count)"
Write-Host "  Blocked packets: $($blockedPackets.Count)"
Write-Host ""

Write-PacketSection -Title "Pending APPLY approvals:" -Packets $pendingPackets
Write-PacketSection -Title "Approved packets:" -Packets $approvedPackets
Write-PacketSection -Title "Blocked packets:" -Packets $blockedPackets

Write-Host "Next safe action: review approval state only; use a separate approved APPLY workflow before changing packet state."
