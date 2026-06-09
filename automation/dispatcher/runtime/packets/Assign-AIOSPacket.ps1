[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$PacketId,

    [Parameter(Mandatory = $true)]
    [string]$WorkerId,

    [string]$AssignedBy = "AIOS Operator",

    [string]$PacketRuntimeRoot = "",

    [string]$WorkerRuntimeRoot = "",

    [string]$ClaimScriptPath = "",

    [string]$LockRegistryPath = "",

    [int]$LockTtlMinutes = 240
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

function ConvertTo-AIOSPathKey {
    param([AllowNull()][string]$Path)

    if ([string]::IsNullOrWhiteSpace($Path)) {
        return ""
    }

    $key = $Path.Replace("\", "/").Trim()
    while ($key.StartsWith("./")) {
        $key = $key.Substring(2)
    }
    return $key.TrimEnd("/")
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

function Ensure-AIOSNoteProperty {
    param(
        [object]$Object,
        [string]$Name,
        [object]$Value = $null
    )

    if (-not ($Object.PSObject.Properties.Name.Contains($Name))) {
        $Object | Add-Member -NotePropertyName $Name -NotePropertyValue $Value
    }
}

function Get-AIOSObjectPropertyValue {
    param(
        [object]$Object,
        [string[]]$Names
    )

    foreach ($name in $Names) {
        if ($Object.PSObject.Properties.Name -contains $name) {
            return $Object.$name
        }
    }
    return $null
}

function Get-AIOSAllowedPaths {
    param(
        [object]$QueuePacket,
        [object]$RuntimePacket
    )

    $propertyNames = @("allowed_paths", "allowedPaths")
    $queueValue = Get-AIOSObjectPropertyValue -Object $QueuePacket -Names $propertyNames
    $runtimeValue = Get-AIOSObjectPropertyValue -Object $RuntimePacket -Names $propertyNames
    $pathSources = @()

    if ($null -ne $queueValue) {
        $pathSources += [pscustomobject]@{ label = "queue"; paths = @($queueValue) }
    }
    if ($null -ne $runtimeValue) {
        $pathSources += [pscustomobject]@{ label = "runtime"; paths = @($runtimeValue) }
    }

    if ($pathSources.Count -eq 0) {
        throw "Assignment lock claim failed closed: packet allowed_paths are missing."
    }

    $normalizedSourceSets = @()
    foreach ($source in $pathSources) {
        $normalized = @($source.paths | ForEach-Object { ConvertTo-AIOSPathKey -Path ([string]$_) } | Where-Object { -not [string]::IsNullOrWhiteSpace([string]$_) } | Sort-Object -Unique)
        if ($normalized.Count -eq 0) {
            throw "Assignment lock claim failed closed: packet allowed_paths are empty or malformed."
        }
        $normalizedSourceSets += [pscustomobject]@{ label = $source.label; paths = $normalized }
    }

    if ($normalizedSourceSets.Count -gt 1) {
        $left = ($normalizedSourceSets[0].paths -join "`n")
        $right = ($normalizedSourceSets[1].paths -join "`n")
        if ($left -ne $right) {
            throw "Assignment lock claim failed closed: queue/runtime allowed_paths disagree."
        }
    }

    return @($normalizedSourceSets[0].paths)
}

function Get-AIOSPacketLane {
    param([object]$Packet)

    $lane = Get-AIOSObjectPropertyValue -Object $Packet -Names @("lane", "lane_id", "lane_name")
    if ([string]::IsNullOrWhiteSpace([string]$lane)) {
        return "packet-assignment"
    }
    return [string]$lane
}

function Invoke-AIOSAssignmentLockClaim {
    param(
        [string]$ScriptPath,
        [string]$RegistryPath,
        [string]$PacketId,
        [string]$WorkerId,
        [string]$Lane,
        [string[]]$AllowedPaths,
        [int]$TtlMinutes
    )

    if (-not (Test-Path -LiteralPath $ScriptPath -PathType Leaf)) {
        throw "Assignment lock claim failed closed: claim script not found: $ScriptPath"
    }
    if (-not (Test-Path -LiteralPath $RegistryPath -PathType Leaf)) {
        throw "Assignment lock claim failed closed: lock registry not found: $RegistryPath"
    }

    $arguments = @(
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        $ScriptPath,
        "-WorkerId",
        $WorkerId,
        "-PacketId",
        $PacketId,
        "-Lane",
        $Lane,
        "-RegistryPath",
        $RegistryPath,
        "-ApprovalPacketId",
        $PacketId,
        "-ReleaseCondition",
        "Release with Release-AiOsFileLock.DRY_RUN.ps1 using exact worker_id and lock_id after packet stop point or operator approval.",
        "-TtlMinutes",
        ([string]$TtlMinutes),
        "-Paths"
    ) + $AllowedPaths + @("-Apply", "-OutputJson")

    $previousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    $output = @(& powershell @arguments 2>&1)
    $exitCode = $LASTEXITCODE
    $ErrorActionPreference = $previousErrorActionPreference
    if ($exitCode -ne 0) {
        throw "Assignment lock claim failed closed: claim script exited $exitCode. $($output -join ' ')"
    }

    try {
        $claim = ($output -join "`n") | ConvertFrom-Json
    }
    catch {
        throw "Assignment lock claim failed closed: claim script returned malformed JSON."
    }

    if ([string]$claim.claim_status -ne "READY_TO_CLAIM") {
        throw "Assignment lock claim failed closed: claim_status=$($claim.claim_status)."
    }
    if ([int]$claim.writes_performed -ne 1) {
        throw "Assignment lock claim failed closed: writes_performed must be exactly 1."
    }
    if ($null -eq $claim.lock -or [string]::IsNullOrWhiteSpace([string]$claim.lock.lock_id)) {
        throw "Assignment lock claim failed closed: lock_id is missing."
    }

    return $claim
}

$repoRoot = Get-AIOSRepoRoot
Set-Location -LiteralPath $repoRoot

if ([string]::IsNullOrWhiteSpace($PacketRuntimeRoot)) {
    $PacketRuntimeRoot = Join-Path $repoRoot "Reports/dispatcher/runtime/packets"
}
if ([string]::IsNullOrWhiteSpace($WorkerRuntimeRoot)) {
    $WorkerRuntimeRoot = Join-Path $repoRoot "Reports/dispatcher/runtime/workers"
}
if ([string]::IsNullOrWhiteSpace($ClaimScriptPath)) {
    $ClaimScriptPath = Join-Path $repoRoot "automation/orchestration/locks/Claim-AiOsFileLock.DRY_RUN.ps1"
}
if ([string]::IsNullOrWhiteSpace($LockRegistryPath)) {
    $LockRegistryPath = Join-Path $repoRoot "automation/orchestration/locks/FILE_LOCK_REGISTRY.json"
}

$packetQueuePath = Join-Path $PacketRuntimeRoot "packet_queue.json"
$packetRuntimePath = Join-Path $PacketRuntimeRoot "packet_runtime_table.json"
$assignmentLedgerPath = Join-Path $PacketRuntimeRoot "packet_assignment_ledger.json"
$statusHistoryPath = Join-Path $PacketRuntimeRoot "packet_status_history.json"
$activeWorkerPath = Join-Path $WorkerRuntimeRoot "active_worker_table.json"
$heartbeatPath = Join-Path $WorkerRuntimeRoot "worker_heartbeat_table.json"

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
$computedAgeSeconds = [int64][Math]::Floor(($now - $heartbeatTime).TotalSeconds)
if ($computedAgeSeconds -gt $staleAfterSeconds) {
    throw "Worker heartbeat is stale. Age seconds: $computedAgeSeconds. Limit seconds: $staleAfterSeconds."
}

$allowedPaths = Get-AIOSAllowedPaths -QueuePacket $queuePacket -RuntimePacket $runtimePacket
$packetLane = Get-AIOSPacketLane -Packet $queuePacket
$lockClaim = Invoke-AIOSAssignmentLockClaim -ScriptPath $ClaimScriptPath -RegistryPath $LockRegistryPath -PacketId $PacketId -WorkerId $WorkerId -Lane $packetLane -AllowedPaths $allowedPaths -TtlMinutes $LockTtlMinutes
$lockId = [string]$lockClaim.lock.lock_id

foreach ($packet in @($queuePacket, $runtimePacket)) {
    Ensure-AIOSNoteProperty -Object $packet -Name "worker_id" -Value $null
    Ensure-AIOSNoteProperty -Object $packet -Name "assigned_worker_id" -Value $null
    Ensure-AIOSNoteProperty -Object $packet -Name "assignment_id" -Value $null
    Ensure-AIOSNoteProperty -Object $packet -Name "assigned_at" -Value $null
    Ensure-AIOSNoteProperty -Object $packet -Name "updated_at" -Value $null
    Ensure-AIOSNoteProperty -Object $packet -Name "last_status_change_at" -Value $null
    Ensure-AIOSNoteProperty -Object $packet -Name "next_safe_action" -Value $null
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
    lock_ids = @($lockId)
    reason = "Manual-safe packet assignment after worker heartbeat validation."
    next_safe_action = $nextSafeAction
}

$statusEvent = [pscustomobject]@{
    event_id = "$PacketId-STATUS-$stamp"
    packet_id = $PacketId
    from_status = "QUEUED"
    to_status = "ASSIGNED"
    worker_id = $WorkerId
    lock_ids = @($lockId)
    changed_at = $timestamp
    changed_by = $AssignedBy
    reason = "Packet assigned to validated idle worker with current heartbeat."
    approval_required = $true
    apply_allowed = $false
    next_safe_action = $nextSafeAction
}

$assignmentLedger.assignments = @($assignmentLedger.assignments) + @($assignmentEntry)
Ensure-AIOSNoteProperty -Object $assignmentLedger -Name "next_safe_action" -Value $null
$assignmentLedger.generated_at = $timestamp
$assignmentLedger.next_safe_action = "Worker $WorkerId may run DRY_RUN only for packet $PacketId."

$statusHistory.status_events = @($statusHistory.status_events) + @($statusEvent)
Ensure-AIOSNoteProperty -Object $statusHistory -Name "next_safe_action" -Value $null
$statusHistory.generated_at = $timestamp
$statusHistory.next_safe_action = "Append the next status event only after DRY_RUN starts or packet state changes."

Ensure-AIOSNoteProperty -Object $packetQueue -Name "next_safe_action" -Value $null
$packetQueue.generated_at = $timestamp
$packetQueue.next_safe_action = "Worker $WorkerId may start DRY_RUN for packet $PacketId. No APPLY is approved."
Ensure-AIOSNoteProperty -Object $packetRuntime -Name "next_safe_action" -Value $null
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
Write-Host ("LockId: {0}" -f $lockId)
Write-Host ("Mode: DRY_RUN")
Write-Host ("ApprovalRequired: true")
Write-Host ("ApplyAllowed: false")
Write-Host ("HeartbeatAgeSeconds: {0}" -f $computedAgeSeconds)
Write-Host ("Next safe action: {0}" -f $nextSafeAction)
