Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$orchestrationRoot = $PSScriptRoot
$controllerPath = Join-Path $orchestrationRoot "assignment_lock_controller.v1.example.json"

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

function Is-BlankOwner {
    param($Value)

    return ($null -eq $Value -or [string]::IsNullOrWhiteSpace([string]$Value) -or [string]$Value -eq "UNASSIGNED")
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

$controller = Read-JsonFile -Path $controllerPath
$locks = @($controller.assignment_locks)
$checks = @($controller.packet_conflict_checks)
$releaseRules = @($controller.release_rules)

Write-Host "AI_OS Assignment Lock Controller Display"
Write-Host "Mode: $($controller.mode)"
Write-Host "Controller: $($controller.controller_name)"
Write-Host "Purpose: $($controller.purpose)"
Write-Host ""
Write-Host "Safety: display-only. No locks are created, released, or modified. No workers or packets are launched."
Write-Host ""

if ($locks.Count -eq 0) {
    Write-Host "Assignment locks: none found in assignment_lock_controller.v1.example.json"
    exit 0
}

$ownedLocks = @($locks | Where-Object { -not (Is-BlankOwner $_.worker_id) })
$staleLocks = @($locks | Where-Object { $_.collision_status -match "stale" })
$blockedLocks = @($locks | Where-Object { $_.claim_status -eq "blocked" -or $_.collision_status -match "blocked" })
$duplicatePacketOwners = @(
    $ownedLocks |
        Group-Object packet_id |
        Where-Object { $_.Count -gt 1 } |
        ForEach-Object { $_.Name }
)
$multiPacketWorkers = @(
    $ownedLocks |
        Group-Object worker_id |
        Where-Object { $_.Count -gt 1 } |
        ForEach-Object { $_.Name }
)

Write-Host "Lock summary:"
Write-Host "  Total lock records: $($locks.Count)"
Write-Host "  Owned lock records: $($ownedLocks.Count)"
Write-Host "  Stale lock records: $($staleLocks.Count)"
Write-Host "  Blocked lock records: $($blockedLocks.Count)"
Write-Host "  Duplicate packet ownership warnings: $($duplicatePacketOwners.Count)"
Write-Host "  Multi-packet worker warnings: $($multiPacketWorkers.Count)"
Write-Host ""

Write-Host "Duplicate ownership:"
if ($duplicatePacketOwners.Count -eq 0) {
    Write-Host "  None"
} else {
    foreach ($packetId in $duplicatePacketOwners) {
        Write-Host "  - Packet $packetId has more than one worker owner."
    }
}
Write-Host ""

Write-Host "Packet conflicts and stale visibility:"
foreach ($lock in $locks) {
    $claimedAt = if ([string]::IsNullOrWhiteSpace([string]$lock.claimed_at)) { "none" } else { $lock.claimed_at }

    Write-Host "  Packet: $($lock.packet_id)"
    Write-Host "    Worker: $($lock.worker_id)"
    Write-Host "    Claim status: $($lock.claim_status)"
    Write-Host "    Claimed at: $claimedAt"
    Write-Host "    Stale after minutes: $($lock.stale_after_minutes)"
    Write-Host "    Collision status: $($lock.collision_status)"
    Write-Host "    Release rule: $($lock.release_rule)"
    Write-Host "    Release allowed by display: $($lock.release_allowed_by_display)"
    Write-Host "    Notes: $($lock.notes)"
}
Write-Host ""

Write-Host "Release-rule structure:"
foreach ($rule in $releaseRules) {
    Write-Host "  Rule: $($rule.rule_id)"
    Write-Host "    Description: $($rule.description)"
    Write-Host "    Automatic release allowed: $($rule.automatic_release_allowed)"
}
Write-Host ""

Write-Host "Conflict checks:"
foreach ($check in $checks) {
    Write-Host "  Check: $($check.check_id)"
    Write-Host "    Severity: $($check.severity)"
    Write-Host "    Display only: $($check.display_only)"
    Write-Host "    Description: $($check.description)"
}
Write-Host ""

Write-Host "Blocked actions:"
Write-List -Items @($controller.blocked_actions)
Write-Host ""

Write-Host "Next safe action: review lock warnings only; use a separate approved APPLY workflow before changing ownership or releasing locks."
