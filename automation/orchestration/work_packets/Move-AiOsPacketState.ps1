param(
    [Parameter(Mandatory = $true)][string]$PacketPath,
    [Parameter(Mandatory = $true)][string]$TargetState,
    [string]$Worker = "human_operator",
    [switch]$Apply
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

$allowedTransitions = @{
    "active"              = @("routed")
    "new"                 = @("routed")
    "routed"              = @("dry_run_done", "blocked")
    "dry_run_done"        = @("awaiting_approval", "blocked")
    "awaiting_approval"   = @("approved", "blocked")
    "approved"            = @("applying", "blocked")
    "applying"            = @("validated", "failed")
    "validated"           = @("complete")
    "blocked"             = @("routed")
    "failed"              = @("routed")
    "complete"            = @()
}

Write-Host ("COPY START " + [char]0x2014 + " Move-AiOsPacketState.ps1")
Write-Host "AI_OS Packet State Transition" -ForegroundColor Cyan
Write-Host "Mode: $(if ($Apply) { 'APPLY' } else { 'DRY_RUN' })"

if (-not (Test-Path -LiteralPath $PacketPath -PathType Leaf)) {
    throw "Packet not found: $PacketPath"
}

$packet = Get-Content -LiteralPath $PacketPath -Raw | ConvertFrom-Json
$currentState = $packet.status

Write-Host ""
Write-Host "Packet: $($packet.packet_id)"
Write-Host "Current state: $currentState"
Write-Host "Target state: $TargetState"
Write-Host "Worker: $Worker"

if (-not ($allowedTransitions.ContainsKey($currentState))) {
    throw "Unknown current state: $currentState"
}

if ($allowedTransitions[$currentState] -notcontains $TargetState) {
    throw "Illegal transition: $currentState -> $TargetState"
}

$utcNow = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")

if (-not ($packet.PSObject.Properties.Name -contains "history")) {
    $packet | Add-Member -MemberType NoteProperty -Name history -Value @()
}

$historyEntry = [pscustomobject]@{
    from_state = $currentState
    to_state = $TargetState
    utc = $utcNow
    worker = $Worker
    apply = [bool]$Apply
}

Write-Host ""
Write-Host "Transition allowed." -ForegroundColor Green

if ($Apply) {
    $packet.status = $TargetState
    $packet.updated_utc = $utcNow
    $packet.history = @($packet.history) + $historyEntry
    $packet | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $PacketPath -Encoding UTF8
    Write-Host "Packet updated: YES" -ForegroundColor Green
} else {
    Write-Host "Packet updated: NO"
}

Write-Host ""
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host ("COPY END " + [char]0x2014 + " Move-AiOsPacketState.ps1")
