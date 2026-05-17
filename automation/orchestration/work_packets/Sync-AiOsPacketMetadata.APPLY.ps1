[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$PacketPath,
    [switch]$SyncBranch,
    [string]$WorkerId = "",
    [switch]$Apply
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

function Test-AiOsBlockedPath {
    param([string]$Path)

    $normalized = ($Path -replace "\\", "/")
    $blockedPatterns = @(
        "apps/dashboard/*",
        "apps/trading_lab/*",
        "aios/modules/trader/*",
        "automation/trading_lab/*",
        "automation/trader/*",
        "*.pem",
        "*.key",
        ".env*",
        "secrets/*",
        "credentials/*"
    )

    foreach ($pattern in $blockedPatterns) {
        if ($normalized -like $pattern) {
            return $true
        }
    }

    return $false
}

function ConvertTo-AiOsRelativePath {
    param([string]$Path)

    $resolved = Resolve-Path -LiteralPath $Path
    $root = (Get-Location).Path + [IO.Path]::DirectorySeparatorChar
    return ($resolved.Path.Replace($root, "") -replace "\\", "/")
}

function Test-AiOsPlaceholderValue {
    param([string]$Value)

    if ([string]::IsNullOrWhiteSpace($Value)) { return $true }
    if ($Value -eq "UNKNOWN") { return $true }
    if ($Value -like "*PLACEHOLDER*") { return $true }
    return $false
}

function Get-AiOsPacketSummary {
    param($Packet)

    [pscustomobject]@{
        packet_id = if ($Packet.packet_id) { [string]$Packet.packet_id } else { "UNKNOWN" }
        branch = if ($Packet.branch) { [string]$Packet.branch } else { "UNKNOWN" }
        assigned_worker = if ($Packet.assigned_worker) { [string]$Packet.assigned_worker } else { "UNKNOWN" }
        updated_utc = if ($Packet.updated_utc) { [string]$Packet.updated_utc } else { "UNKNOWN" }
        notes_count = @($Packet.notes).Count
        status = if ($Packet.status) { [string]$Packet.status } else { "UNKNOWN" }
    }
}

if (-not (Test-Path -LiteralPath $PacketPath -PathType Leaf)) {
    throw "Packet not found: $PacketPath"
}

$relativePacketPath = ConvertTo-AiOsRelativePath -Path $PacketPath
if (Test-AiOsBlockedPath -Path $relativePacketPath) {
    throw "Refusing blocked path: $relativePacketPath"
}

try {
    $packet = Get-Content -LiteralPath $PacketPath -Raw | ConvertFrom-Json
}
catch {
    throw "Packet JSON parse failed before sync: $($_.Exception.Message)"
}

if (-not ($packet.PSObject.Properties.Name -contains "packet_id") -or [string]::IsNullOrWhiteSpace([string]$packet.packet_id)) {
    throw "Packet is missing packet_id."
}

$before = Get-AiOsPacketSummary -Packet $packet
$targetBranch = $before.branch
if ($SyncBranch) {
    $targetBranch = git branch --show-current
}

$targetWorker = $before.assigned_worker
if (-not [string]::IsNullOrWhiteSpace($WorkerId)) {
    if (Test-AiOsPlaceholderValue -Value $WorkerId) {
        throw "Refusing blank, UNKNOWN, or placeholder WorkerId."
    }
    $targetWorker = $WorkerId
}

$utcNow = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
$note = "Metadata sync: branch $($before.branch) -> $targetBranch; assigned_worker $($before.assigned_worker) -> $targetWorker."

$afterPreview = [pscustomobject]@{
    packet_id = $before.packet_id
    branch = $targetBranch
    assigned_worker = $targetWorker
    updated_utc = $utcNow
    notes_count = $before.notes_count + 1
    status = $before.status
}

Write-Host "AIOS Packet Metadata Sync"
Write-Host "Mode: $(if ($Apply) { 'APPLY' } else { 'DRY_RUN_PREVIEW' })"
Write-Host "Packet path: $relativePacketPath"
Write-Host ""
Write-Host "Before:"
Write-Host "  packet_id: $($before.packet_id)"
Write-Host "  branch: $($before.branch)"
Write-Host "  assigned_worker: $($before.assigned_worker)"
Write-Host "  updated_utc: $($before.updated_utc)"
Write-Host "  notes_count: $($before.notes_count)"
Write-Host "  status: $($before.status)"
Write-Host ""
Write-Host "After:"
Write-Host "  packet_id: $($afterPreview.packet_id)"
Write-Host "  branch: $($afterPreview.branch)"
Write-Host "  assigned_worker: $($afterPreview.assigned_worker)"
Write-Host "  updated_utc: $($afterPreview.updated_utc)"
Write-Host "  notes_count: $($afterPreview.notes_count)"
Write-Host "  status: $($afterPreview.status)"
Write-Host ""
Write-Host "Note to append:"
Write-Host $note

if ($Apply) {
    $packet.branch = $targetBranch
    $packet.assigned_worker = $targetWorker
    $packet.updated_utc = $utcNow

    if (-not ($packet.PSObject.Properties.Name -contains "notes") -or $null -eq $packet.notes) {
        $packet | Add-Member -MemberType NoteProperty -Name notes -Value @()
    }
    $packet.notes = @($packet.notes) + $note

    $packet | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $PacketPath -Encoding UTF8

    try {
        Get-Content -LiteralPath $PacketPath -Raw | ConvertFrom-Json | Out-Null
    }
    catch {
        throw "Packet JSON parse failed after sync: $($_.Exception.Message)"
    }

    Write-Host ""
    Write-Host "Packet updated: YES"
}
else {
    Write-Host ""
    Write-Host "Packet updated: NO"
}

Write-Host "State moved: NO"
Write-Host "Move-AiOsPacketState.ps1 called: NO"
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
