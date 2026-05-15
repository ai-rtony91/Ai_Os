Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$orchestrationRoot = $PSScriptRoot
$inboxPath = Join-Path $orchestrationRoot "approval_inbox.v1.example.json"

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

function Write-List {
    param([object[]]$Items)

    if ($Items.Count -eq 0) {
        Write-Host "    - None"
        return
    }

    foreach ($item in $Items) {
        Write-Host "    - $item"
    }
}

$inbox = Read-JsonFile -Path $inboxPath
$approvals = @($inbox.approvals)

Write-Host "AI_OS Approval Inbox v1 Display"
Write-Host "Mode: $($inbox.mode)"
Write-Host "Inbox: $($inbox.inbox_name)"
Write-Host "Purpose: $($inbox.purpose)"
Write-Host ""
Write-Host "Safety: display-only. No approvals, validators, merges, commits, pushes, or launches are performed."
Write-Host ""

$pending = @($approvals | Where-Object { $_.approval_state -match "pending" })
$blocked = @($approvals | Where-Object { $_.blocked -eq $true })
$validatorRequired = @($approvals | Where-Object { $_.validator_required -eq $true })
$mergeRequired = @($approvals | Where-Object { $_.merge_required -eq $true })

Write-Host "Approval summary:"
Write-Host "  Total approvals: $($approvals.Count)"
Write-Host "  Pending approvals: $($pending.Count)"
Write-Host "  Blocked approvals: $($blocked.Count)"
Write-Host "  Validator-required approvals: $($validatorRequired.Count)"
Write-Host "  Merge-required approvals: $($mergeRequired.Count)"
Write-Host ""

foreach ($approval in $approvals) {
    $blockReason = if ([string]::IsNullOrWhiteSpace([string]$approval.block_reason)) { "none" } else { $approval.block_reason }

    Write-Host "Approval: $($approval.approval_id)"
    Write-Host "  Packet: $($approval.packet_id)"
    Write-Host "  Name: $($approval.packet_name)"
    Write-Host "  State: $($approval.approval_state)"
    Write-Host "  Approval required: $($approval.approval_required)"
    Write-Host "  Validator required: $($approval.validator_required)"
    Write-Host "  Merge required: $($approval.merge_required)"
    Write-Host "  Blocked: $($approval.blocked)"
    Write-Host "  Block reason: $blockReason"
    Write-Host "  Notes: $($approval.notes)"
    Write-Host ""
}

Write-Host "Blocked actions:"
Write-List -Items @($inbox.blocked_actions)
Write-Host ""

Write-Host "Next safe action: review approval state only; use a separate approved workflow before changing approvals, validators, merges, commits, or pushes."
