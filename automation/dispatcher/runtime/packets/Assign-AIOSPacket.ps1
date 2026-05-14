[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$PacketId,

    [Parameter(Mandatory = $true)]
    [string]$WorkerId,

    [string]$AssignedBy = "AIOS Operator"
)

$ErrorActionPreference = "Stop"

function Get-AIOSRepoRoot {
    $root = & git rev-parse --show-toplevel 2>$null
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($root)) {
        throw "Unable to find git repository root."
    }
    return $root.Trim()
}

function Read-AIOSJson {
    param([string]$Path)

    if (-not (Test-Path -LiteralPath $Path)) {
        throw "Required JSON file not found: $Path"
    }

    try {
        return Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json
    }
    catch {
        throw "Invalid JSON file: $Path"
    }
}

function Write-AIOSJson {
    param(
        [string]$Path,
        [object]$Value
    )

    $json = $Value | ConvertTo-Json -Depth 30
    Set-Content -LiteralPath $Path -Value $json -Encoding UTF8
}

function Test-AIOSBlank {
    param([object]$Value)
    return ($null -eq $Value -or [string]::IsNullOrWhiteSpace([string]$Value))
}

function Get-AIOSSingleById {
    param(
        [object[]]$Items,
        [string]$Field,
        [string]$Value,
        [string]$Label
    )

    $matches = @($Items | Where-Object { [string]($_.$Field) -eq $Value })
    if ($matches.Count -eq 0) {
        throw "$Label not found: $Value"
    }
    if ($matches.Count -gt 1) {
        throw "$Label is duplicated and requires review: $Value"
    }
    return $matches[0]
}

function Assert-AIOSFlag {
    param(
        [bool]$Condition,
        [string]$Message
    )

    if (-not $Condition) {
        throw $Message
    }
}

$repoRoot = Get-AIOSRepoRoot
Set-Location -LiteralPath $repoRoot

$packetQueuePath = Join-Path $repoRoot "Reports/dispatcher/runtime/packets/packet_queue.json"
$packetRuntimePath = Join-Path $repoRoot "Reports/dispatcher/runtime/packets/packet_runtime_table.json"
$assignmentLedgerPath = Join-Path $repoRoot "Reports/dispatcher/runtime/packets/packet_assignment_ledger.json"
$statusHistoryPath = Join-Path $repoRoot "Reports/dispatcher/runtime/packets/packet_status_history.json"
$activeWorkerPath = Join-Path $repoRoot "Reports/dispatcher/runtime/workers/active_worker_table.json"
$heartbeatPath = Join-Path $repoRoot "Reports/dispatcher/runtime/workers/worker_heartbeat_table.json"

$packetQueue = Read-AIOSJson -Path $packetQueuePath
$packetRuntime = Read-AIOSJson -Path $packetRuntimePath
$assignmentLedger = Read-AIOSJson -Path $assignmentLedgerPath
$statusHistory = Read-AIOSJson -Path $statusHistoryPath
$activeWorkers = Read-AIOSJson -Path $activeWorkerPath
$heartbeats = Read-AIOSJson -Path $heartbeatPath

$queuePacket = Get-AIOSSingleById -Items @($packetQueue.packets) -Field "packet_id" -Value $PacketId -Label "Queue packet"
$runtimePacket = Get-AIOSSingleById -Items @($packetRuntime.packets) -Field "packet_id" -Value $PacketId -Label "Runtime packet"
$worker = Get-AIOSSingleById -Items @($activeWorkers.workers) -Field "worker_id" -Value $WorkerId -Label "Worker"
$heartbeat = Get-AIOSSingleById -Items @($heartbeats.heartbeats) -Field "worker_id" -Value $WorkerId -Label "Worker heartbeat"

Assert-AIOSFlag -Condition ([string]$queuePacket.status -eq "QUEUED") -Message "Queue packet is not QUEUED: $($queuePacket.status)"
Assert-AIOSFlag -Condition ([string]$runtimePacket.status -eq "QUEUED") -Message "Runtime packet is not QUEUED: $($runtimePacket.status)"
Assert-AIOSFlag -Condition ([string]$queuePacket.mode -eq "DRY_RUN") -Message "Queue packet mode is not DRY_RUN."
Assert-AIOSFlag -Condition ([string]$runtimePacket.mode -eq "DRY_RUN") -Message "Runtime packet mode is not DRY_RUN."
Assert-AIOSFlag -Condition ([bool]$queuePacket.approval_required) -Message "Queue packet approval_required must be true."
Assert-AIOSFlag -Condition ([bool]$runtimePacket.approval_required) -Message "Runtime packet approval_required must be true."
Assert-AIOSFlag -Condition (-not [bool]$queuePacket.apply_allowed) -Message "Queue packet apply_allowed must be false."
Assert-AIOSFlag -Condition (-not [bool]$runtimePacket.apply_allowed) -Message "Runtime packet apply_allowed must be false."
Assert-AIOSFlag -Condition (Test-AIOSBlank -Value $runtimePacket.assigned_worker_id) -Message "Runtime packet is already assigned."
Assert-AIOSFlag -Condition (Test-AIOSBlank -Value $queuePacket.assigned_worker_id) -Message "Queue packet is already assigned."

Assert-AIOSFlag -Condition ([string]$worker.current_state -eq "IDLE") -Message "Worker state must be IDLE: $($worker.current_state)"
Assert-AIOSFlag -Condition (Test-AIOSBlank -Value $worker.assigned_packet_id) -Message "Worker already has assigned_packet_id."
Assert-AIOSFlag -Condition ([string]$heartbeat.current_state -eq "IDLE") -Message "Heartbeat worker state must be IDLE: $($heartbeat.current_state)"
Assert-AIOSFlag -Condition ([string]$heartbeat.stale_status -eq "CURRENT") -Message "Worker heartbeat must be CURRENT: $($heartbeat.stale_status)"
Assert-AIOSFlag -Condition (Test-AIOSBlank -Value $heartbeat.assigned_packet_id) -Message "Heartbeat already has assigned_packet_id."
Assert-AIOSFlag -Condition (-not (Test-AIOSBlank -Value $heartbeat.heartbeat_time)) -Message "Worker heartbeat_time is missing."

$heartbeatTime = [DateTimeOffset]::Parse([string]$heartbeat.heartbeat_time).ToUniversalTime()
$now = [DateTimeOffset]::UtcNow
$staleAfterSeconds = [int]$heartbeat.stale_after_seconds
if ($staleAfterSeconds -le 0) {
    throw "Worker stale_after_seconds must be greater than zero."
}
$computedAgeSeconds = [int][Math]::Floor(($now - $heartbeatTime).TotalSeconds)
if ($computedAgeSeconds -gt $staleAfterSeconds) {
    throw "Worker heartbeat is stale. Age seconds: $computedAgeSeconds. Limit seconds: $staleAfterSeconds."
}

if (-not $queuePacket.PSObject.Properties.Name.Contains("assignment_id")) {
    $queuePacket | Add-Member -NotePropertyName "assignment_id" -NotePropertyValue $null
}
if (-not $queuePacket.PSObject.Properties.Name.Contains("assigned_at")) {
    $queuePacket | Add-Member -NotePropertyName "assigned_at" -NotePropertyValue $null
}
if (-not $queuePacket.PSObject.Properties.Name.Contains("last_status_change_at")) {
    $queuePacket | Add-Member -NotePropertyName "last_status_change_at" -NotePropertyValue $null
}

$timestamp = $now.ToString("yyyy-MM-ddTHH:mm:ssZ")
$stamp = $now.ToString("yyyyMMddHHmmss")
$assignmentId = "ASSIGN-$PacketId-$WorkerId-$stamp"
$nextSafeAction = "Worker $WorkerId may start DRY_RUN for packet $PacketId only. APPLY, locks, staging, commit, and push remain blocked."

foreach ($packet in @($queuePacket, $runtimePacket)) {
    $packet.status = "ASSIGNED"
    $packet.worker_id = $WorkerId
    $packet.assigned_worker_id = $WorkerId
    $packet.assignment_id = $assignmentId
    $packet.assigned_at = $timestamp
    $packet.updated_at = $timestamp
    $packet.last_status_change_at = $timestamp
    $packet.mode = "DRY_RUN"
    $packet.approval_required = $true
    $packet.apply_allowed = $false
    $packet.next_safe_action = $nextSafeAction
}

$assignmentEntry = [pscustomobject]@{
    assignment_id = $assignmentId
    packet_id = $PacketId
    worker_id = $WorkerId
    from_status = "QUEUED"
    to_status = "ASSIGNED"
    assigned_at = $timestamp
    assigned_by = $AssignedBy
    mode = "DRY_RUN"
    approval_required = $true
    apply_allowed = $false
    lock_ids = @()
    reason = "Manual-safe packet assignment after worker heartbeat validation."
    next_safe_action = $nextSafeAction
}

$statusEvent = [pscustomobject]@{
    event_id = "$PacketId-STATUS-$stamp"
    packet_id = $PacketId
    from_status = "QUEUED"
    to_status = "ASSIGNED"
    worker_id = $WorkerId
    lock_ids = @()
    changed_at = $timestamp
    changed_by = $AssignedBy
    reason = "Packet assigned to validated idle worker with current heartbeat."
    approval_required = $true
    apply_allowed = $false
    next_safe_action = $nextSafeAction
}

$assignmentLedger.assignments = @($assignmentLedger.assignments) + @($assignmentEntry)
$assignmentLedger.generated_at = $timestamp
$assignmentLedger.next_safe_action = "Worker $WorkerId may run DRY_RUN only for packet $PacketId."

$statusHistory.status_events = @($statusHistory.status_events) + @($statusEvent)
$statusHistory.generated_at = $timestamp
$statusHistory.next_safe_action = "Append the next status event only after DRY_RUN starts or packet state changes."

$packetQueue.generated_at = $timestamp
$packetQueue.next_safe_action = "Worker $WorkerId may start DRY_RUN for packet $PacketId. No APPLY is approved."
$packetRuntime.generated_at = $timestamp
$packetRuntime.next_safe_action = "Worker $WorkerId may start DRY_RUN for packet $PacketId. No APPLY is approved."

Write-AIOSJson -Path $packetQueuePath -Value $packetQueue
Write-AIOSJson -Path $packetRuntimePath -Value $packetRuntime
Write-AIOSJson -Path $assignmentLedgerPath -Value $assignmentLedger
Write-AIOSJson -Path $statusHistoryPath -Value $statusHistory

Write-Host "AI_OS PACKET ASSIGNMENT"
Write-Host ("Result: ASSIGNED")
Write-Host ("PacketId: {0}" -f $PacketId)
Write-Host ("WorkerId: {0}" -f $WorkerId)
Write-Host ("AssignmentId: {0}" -f $assignmentId)
Write-Host ("Mode: DRY_RUN")
Write-Host ("ApprovalRequired: true")
Write-Host ("ApplyAllowed: false")
Write-Host ("HeartbeatAgeSeconds: {0}" -f $computedAgeSeconds)
Write-Host ("Next safe action: {0}" -f $nextSafeAction)
