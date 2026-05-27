[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$PacketPath,
    [string]$ApprovalReference = "",
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

$resolverPath = "automation/orchestration/workers/Resolve-AiOsWorkerForPacket.DRY_RUN.ps1"
$workerResolution = $null
$workerResolutionStatus = "NOT_RUN"
if (Test-Path -LiteralPath $resolverPath -PathType Leaf) {
    try {
        $workerResolution = powershell -NoProfile -ExecutionPolicy Bypass -File $resolverPath -PacketPath $PacketPath -QuietJson | ConvertFrom-Json
        $workerResolutionStatus = "PASS"
    }
    catch {
        $workerResolutionStatus = "REVIEW"
        $workerResolution = [pscustomobject]@{
            error = $_.Exception.Message
        }
    }
}

$selectedWorkerId = ""
if ($null -ne $workerResolution -and $workerResolution.PSObject.Properties.Name -contains "selected_worker" -and $null -ne $workerResolution.selected_worker) {
    $selectedWorkerId = [string]$workerResolution.selected_worker.worker_id
}

$created = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
$status = if ([string](Get-AiOsProp -Object $packet -Names @("status")) -in @("APPROVED", "approved")) { "WORKER_READY_PREVIEW" } else { "NEEDS_REVIEW" }

$preview = [pscustomobject]@{
    schema = "AIOS_WORKER_READY_PACKET_PREVIEW.v1"
    mode = "DRY_RUN"
    packet_id = $packetId
    objective = [string](Get-AiOsProp -Object $packet -Names @("objective", "intent", "title"))
    allowed_paths = @(Get-AiOsProp -Object $packet -Names @("allowed_paths", "allowed_write_boundary"))
    blocked_paths = @(Get-AiOsProp -Object $packet -Names @("blocked_paths", "forbidden_paths"))
    safety_rules = @(Get-AiOsProp -Object $packet -Names @("safety_rules"))
    validation_commands = @(Get-AiOsProp -Object $packet -Names @("validation_commands"))
    expected_output = [string](Get-AiOsProp -Object $packet -Names @("expected_output", "final_report_format"))
    approval_reference = if ([string]::IsNullOrWhiteSpace($ApprovalReference)) { "MISSING_APPROVAL_REFERENCE" } else { $ApprovalReference }
    lock_owner = $selectedWorkerId
    lock_required = [bool](Get-AiOsProp -Object $packet -Names @("lock_required"))
    assigned_worker = $selectedWorkerId
    worker_resolution_status = $workerResolutionStatus
    worker_resolution = $workerResolution
    created_timestamp = $created
    status = $status
    writes_performed = 0
    worker_execution_performed = "NO"
    commit_performed = "NO"
    push_performed = "NO"
    next_safe_action = if ($status -eq "WORKER_READY_PREVIEW") { "Review worker-ready preview before any approved inbox mutation." } else { "Approve packet and provide approval reference before worker inbox mutation." }
}

if ($OutputJson) {
    $preview | ConvertTo-Json -Depth 12
    exit 0
}

Write-Host "AI_OS Worker Ready Packet Preview"
Write-Host "Mode: DRY_RUN"
Write-Host "Packet id: $($preview.packet_id)"
Write-Host "Status: $($preview.status)"
Write-Host "Assigned worker: $($preview.assigned_worker)"
Write-Host "Writes performed: 0"
Write-Host "Worker execution performed: NO"
Write-Host "Next safe action: $($preview.next_safe_action)"
