[CmdletBinding()]
param(
    [string]$GoalPath = "control/operation_glue/GOAL_INTAKE.example.json",
    [switch]$Apply,
    [switch]$OutputJson
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-AiOsUtcTimestamp {
    return (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
}

function Get-AiOsFileTimestamp {
    return (Get-Date).ToUniversalTime().ToString("yyyyMMdd-HHmmss")
}

function ConvertTo-AiOsSafeId {
    param([string]$Value)
    $safe = ($Value -replace "[^A-Za-z0-9_-]", "-").Trim("-")
    if ([string]::IsNullOrWhiteSpace($safe)) { return "unknown-goal" }
    return $safe.ToLowerInvariant()
}

function Read-AiOsJson {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "Goal intake file not found: $Path"
    }
    return Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json
}

function Get-AiOsRecommendedWorker {
    param([object]$Goal)
    $preference = [string]$Goal.worker_preference
    if ($preference -and $preference -ne "AUTO") { return $preference }

    $text = ("{0} {1} {2}" -f $Goal.objective, $Goal.target_area, $Goal.notes).ToLowerInvariant()
    if ($text -match "dashboard|ui|mock-data") { return "Claude West" }
    if ($text -match "validate|validator|check") { return "Validator" }
    if ($text -match "summary|supervisor|morning|overnight") { return "Supervisor" }
    return "Codex East"
}

function Get-AiOsPacketMode {
    param([object]$Goal)
    $requested = [string]$Goal.mode_requested
    if ([bool]$Goal.protected_action_expected) { return "PROTECTED_ACTION_REQUIRED" }
    if ($requested) { return $requested }
    return "DRY_RUN"
}

function Get-AiOsBlockedPathHits {
    param([object]$Goal)
    $haystack = ("{0} {1} {2} {3}" -f $Goal.objective, $Goal.target_area, $Goal.notes, (@($Goal.allowed_paths) -join " ")).ToLowerInvariant()
    $hits = @()
    foreach ($blockedPath in @($Goal.blocked_paths)) {
        $blocked = ([string]$blockedPath).ToLowerInvariant()
        if (-not [string]::IsNullOrWhiteSpace($blocked) -and $haystack.Contains($blocked)) {
            $hits += [string]$blockedPath
        }
    }
    return @($hits | Select-Object -Unique)
}

$goal = Read-AiOsJson -Path $GoalPath
$blockedHits = @(Get-AiOsBlockedPathHits -Goal $goal)
$mode = Get-AiOsPacketMode -Goal $goal
$recommendedWorker = Get-AiOsRecommendedWorker -Goal $goal
$protectedActionGateRequired = [bool]$goal.protected_action_expected -or $mode -eq "PROTECTED_ACTION_REQUIRED" -or $blockedHits.Count -gt 0
$approvalMarker = if ($protectedActionGateRequired) { "BLOCK_PROTECTED_ACTION" } elseif ([bool]$goal.approval_required) { "HUMAN_REVIEW_REQUIRED" } else { "NOT_REQUIRED" }
$safeGoalId = ConvertTo-AiOsSafeId -Value ([string]$goal.goal_id)
$timestamp = Get-AiOsFileTimestamp
$packetId = "WORKER_PACKET_{0}_{1}" -f $timestamp, $safeGoalId

$packet = [ordered]@{
    schema                         = "AIOS_OPERATION_GLUE_WORKER_PACKET.v0_1"
    packet_id                      = $packetId
    source_goal_id                 = [string]$goal.goal_id
    created_at                     = Get-AiOsUtcTimestamp
    recommended_worker             = $recommendedWorker
    mode                           = $mode
    mission                        = [string]$goal.objective
    allowed_paths                  = @($goal.allowed_paths)
    blocked_paths                  = @($goal.blocked_paths)
    blocked_path_hits              = $blockedHits
    validation_required            = @(
        "git diff --check",
        "PowerShell parse for generated scripts",
        "JSON parse for generated state",
        "Operation Glue DRY_RUN functional checks"
    )
    protected_action_gate_required = $protectedActionGateRequired
    approval_marker_required       = $approvalMarker
    next_safe_action               = if ($protectedActionGateRequired) {
        "Stop and route through the Protected Action Gate before execution."
    } else {
        "Run the worker packet in the recommended lane, then import the worker result."
    }
}

$outputPath = "DRY_RUN_NO_FILE_WRITTEN"
if ($Apply) {
    $outDir = "control/operation_glue/worker_packets"
    New-Item -ItemType Directory -Force -Path $outDir | Out-Null
    $outputPath = Join-Path $outDir ("{0}.json" -f $packetId)
    $packet | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $outputPath -Encoding UTF8
}

$result = [ordered]@{
    schema             = "AIOS_OPERATION_GLUE_PACKET_GENERATOR_RESULT.v0_1"
    mode               = if ($Apply) { "APPLY" } else { "DRY_RUN" }
    goal_path          = $GoalPath
    output_path        = $outputPath
    wrote_file         = [bool]$Apply
    worker_packet      = $packet
    next_safe_action   = $packet.next_safe_action
    protected_boundary = "No staging, commit, push, merge, reset, clean, branch deletion, broker, OANDA, wallet, secrets, deploy, or live trading action performed."
}

if ($OutputJson) {
    $result | ConvertTo-Json -Depth 10
    exit 0
}

Write-Host "AI_OS Operation Glue - Worker Packet From Goal"
Write-Host ("Mode: {0}" -f $result.mode)
Write-Host ("Goal: {0}" -f $goal.goal_id)
Write-Host ("Recommended worker: {0}" -f $recommendedWorker)
Write-Host ("Packet mode: {0}" -f $mode)
Write-Host ("Protected Action Gate required: {0}" -f $protectedActionGateRequired)
Write-Host ("Output: {0}" -f $outputPath)
Write-Host ("Next safe action: {0}" -f $result.next_safe_action)
Write-Host "No commit, push, merge, reset, clean, branch deletion, or protected action performed."
Write-Host ""
$result | ConvertTo-Json -Depth 10
