[CmdletBinding()]
param(
    [string]$StateDirectory = "automation/orchestration/auto_loop/state",
    [switch]$Latest
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-AiOsFullPath {
    param([Parameter(Mandatory = $true)][string]$Path)
    if ([System.IO.Path]::IsPathRooted($Path)) { return [System.IO.Path]::GetFullPath($Path) }
    return [System.IO.Path]::GetFullPath((Join-Path (Get-Location).Path $Path))
}

function Test-AiOsPathInside {
    param([string]$Path, [string]$AllowedRoot)
    $fullPath = Get-AiOsFullPath -Path $Path
    $fullRoot = Get-AiOsFullPath -Path $AllowedRoot
    return $fullPath.StartsWith($fullRoot, [System.StringComparison]::OrdinalIgnoreCase)
}

function Get-AiOsCount {
    param([string]$Path, [string]$Filter)
    if (-not (Test-Path -LiteralPath $Path)) { return 0 }
    return @(Get-ChildItem -Path $Path -Filter $Filter -File -ErrorAction SilentlyContinue).Count
}

if (-not (Test-AiOsPathInside -Path $StateDirectory -AllowedRoot "automation/orchestration/auto_loop/state")) {
    throw "StateDirectory must stay under automation/orchestration/auto_loop/state."
}

$packetDir = Join-Path $StateDirectory "packets"
$lockDir = Join-Path $StateDirectory "locks"
$approvalDir = Join-Path $StateDirectory "approvals"
$validatorDir = Join-Path $StateDirectory "validator_runs"
$runtimeDir = Join-Path $StateDirectory "runtime_snapshots"
$resumeDir = Join-Path $StateDirectory "resume"

$latestPacket = $null
if (Test-Path -LiteralPath $packetDir) {
    $latestPacket = Get-ChildItem -Path $packetDir -Filter "PACKET_*.json" -File -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1
}

$packet = $null
$approval = $null
$validator = $null
if ($latestPacket) {
    $packet = Get-Content -Raw -LiteralPath $latestPacket.FullName | ConvertFrom-Json
    $approvalPath = Join-Path $approvalDir "APPROVAL_$($packet.packet_id).json"
    $validatorPath = Join-Path $validatorDir "VALIDATOR_RUN_$($packet.packet_id).json"
    if (Test-Path -LiteralPath $approvalPath) { $approval = Get-Content -Raw -LiteralPath $approvalPath | ConvertFrom-Json }
    if (Test-Path -LiteralPath $validatorPath) { $validator = Get-Content -Raw -LiteralPath $validatorPath | ConvertFrom-Json }
}

$blockedRecords = [System.Collections.Generic.List[string]]::new()
foreach ($path in @($packetDir, $lockDir, $approvalDir, $validatorDir, $runtimeDir, $resumeDir)) {
    if (-not (Test-Path -LiteralPath $path)) { continue }
    foreach ($file in Get-ChildItem -Path $path -Filter "*.json" -File -ErrorAction SilentlyContinue) {
        $text = Get-Content -Raw -LiteralPath $file.FullName
        if ($text -match '"BLOCKED"|: "BLOCK"') {
            $blockedRecords.Add($file.FullName)
        }
    }
}

$summary = [ordered]@{
    packet_record_count = Get-AiOsCount -Path $packetDir -Filter "PACKET_*.json"
    lock_record_count = Get-AiOsCount -Path $lockDir -Filter "LOCK_*.json"
    approval_record_count = Get-AiOsCount -Path $approvalDir -Filter "APPROVAL_*.json"
    validator_run_record_count = Get-AiOsCount -Path $validatorDir -Filter "VALIDATOR_RUN_*.json"
    runtime_snapshot_count = Get-AiOsCount -Path $runtimeDir -Filter "RUNTIME_SNAPSHOT_*.json"
    resume_record_count = Get-AiOsCount -Path $resumeDir -Filter "RESUME_*.json"
    latest_packet_id = if ($packet) { $packet.packet_id } else { $null }
    latest_approval_state = if ($approval) { $approval.approval_state } else { $null }
    latest_validation_state = if ($validator) { $validator.validation_state } else { $null }
    latest_next_safe_action = if ($packet) { $packet.next_safe_action } else { $null }
    any_blocked = ($blockedRecords.Count -gt 0)
    blocked_records = @($blockedRecords)
    did = @("Read sandbox auto-loop state record counts and latest status.")
    did_not = @("Did not mutate active state, queues, inboxes, registries, runtime, telemetry/runtime, stage, commit, push, merge, or rebase.")
}

Write-Output ($summary | ConvertTo-Json -Depth 8)
