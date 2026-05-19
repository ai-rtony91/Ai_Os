Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$orchestrationRoot = $PSScriptRoot
$inboxPath = Join-Path $orchestrationRoot "approval_inbox\APPROVAL_INBOX_001.json"
$legacyInboxPath = Join-Path $orchestrationRoot "approval_inbox.example.json"

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

function Get-JsonValue {
    param(
        [AllowNull()]$Object,
        [Parameter(Mandatory = $true)][string]$Name,
        [string]$Default = ""
    )

    if ($null -eq $Object) { return $Default }
    if ($Object.PSObject.Properties.Name -contains $Name) {
        $value = $Object.$Name
        if ($null -ne $value -and -not [string]::IsNullOrWhiteSpace([string]$value)) {
            return $value
        }
    }
    return $Default
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

$usedLegacyInbox = $false
$inbox = if (Test-Path -LiteralPath $inboxPath -PathType Leaf) {
    Read-JsonFile -Path $inboxPath
} elseif (Test-Path -LiteralPath $legacyInboxPath -PathType Leaf) {
    $usedLegacyInbox = $true
    Read-JsonFile -Path $legacyInboxPath
} else {
    $null
}

if ($null -eq $inbox) {
    Write-Host "AI_OS Approval Inbox Display"
    Write-Host "Mode: UNKNOWN"
    Write-Host "Inbox: unavailable"
    Write-Host "Purpose: Display approval inbox state without modifying approvals."
    Write-Host ""
    Write-Host "Safety: display-only. No files are created. No approvals are changed. No packets are launched."
    Write-Host ""
    Write-Host "Approval summary:"
    Write-Host "  Canonical source missing: automation/orchestration/approval_inbox/APPROVAL_INBOX_001.json"
    Write-Host "  Legacy fallback not found; no approval source available."
    Write-Host ""
    Write-Host "Next safe action: restore or create the canonical approval inbox through an approved workflow."
    exit 0
}

$isLegacyPacketInbox = $inbox.PSObject.Properties.Name -contains "packets"
$packets = if ($isLegacyPacketInbox) { @($inbox.packets) } else { @() }

Write-Host "AI_OS Approval Inbox Display"
Write-Host "Mode: $(Get-JsonValue -Object $inbox -Name 'mode' -Default 'canonical approval record')"
Write-Host "Inbox: $(Get-JsonValue -Object $inbox -Name 'inbox_name' -Default (Get-JsonValue -Object $inbox -Name 'schema' -Default 'UNKNOWN'))"
Write-Host "Purpose: $(Get-JsonValue -Object $inbox -Name 'purpose' -Default 'Canonical approval inbox item for operator review.')"
Write-Host ""
Write-Host "Safety: display-only. No files are created. No approvals are changed. No packets are launched."
Write-Host ""

if (-not $isLegacyPacketInbox) {
    Write-Host "Approval summary:"
    Write-Host "  Source: automation/orchestration/approval_inbox/APPROVAL_INBOX_001.json"
    Write-Host "  Approval ID: $($inbox.approval_id)"
    Write-Host "  Packet ID: $($inbox.packet_id)"
    Write-Host "  Requested action: $($inbox.requested_action)"
    Write-Host "  Risk level: $($inbox.risk_level)"
    Write-Host "  Approval status: $($inbox.approval_status)"
    Write-Host "  Approved by human: $($inbox.approved_by_human)"
    if (Test-Path -LiteralPath $legacyInboxPath -PathType Leaf) {
        Write-Host "  Legacy packet-list fallback: approval_inbox.example.json available"
    } else {
        Write-Host "  Legacy fallback not found; canonical source used."
    }
    Write-Host ""
    Write-Host "Next safe action: review approval state only; use a separate approved APPLY workflow before changing packet state."
    exit 0
}

if ($usedLegacyInbox) {
    Write-Host "Approval source: legacy approval_inbox.example.json used because canonical source was unavailable."
    Write-Host ""
}

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
