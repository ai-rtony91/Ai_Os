[CmdletBinding()]
param(
    [string]$WorkerId = "EAST_OCC_01",
    [string]$PacketId = "PACKET_ID_REQUIRED",
    [string[]]$AssignedPaths = @()
)

$ErrorActionPreference = "Stop"

$blockedPatterns = @(
    "broker/",
    "OANDA/",
    "api_keys/",
    "live_trading/",
    "live_order/",
    "real_orders"
)

$blockedMatches = @(
    foreach ($path in $AssignedPaths) {
        foreach ($pattern in $blockedPatterns) {
            if ($path -like "*$pattern*") { $path }
        }
    }
) | Select-Object -Unique

$lockStatus = if ($blockedMatches.Count -gt 0) { "BLOCKED" } elseif ($AssignedPaths.Count -eq 0) { "REVIEW_REQUIRED" } else { "REVIEW_REQUIRED" }

[pscustomobject]@{
    schema = "AIOS_CREW_ASSIGNMENT_RECOMMENDATION.v1"
    mode = "DRY_RUN_READ_ONLY"
    worker_id = $WorkerId
    packet_id = $PacketId
    assigned_paths = $AssignedPaths
    lock_status = $lockStatus
    blocked_path_matches = $blockedMatches
    recommendation = if ($lockStatus -eq "BLOCKED") { "Do not assign. Blocked path present." } else { "Run lock collision validation before APPLY." }
    modifies_files = $false
    commits = $false
    pushes = $false
    next_safe_action = "Run Test-WorkerClaimCollision.DRY_RUN.ps1 and lock registry validation before assignment."
} | ConvertTo-Json -Depth 8
