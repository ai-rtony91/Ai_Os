param(
    [switch]$DryRun,
    [switch]$NoPublish,
    [int]$MaxMinutes = 30
)

$ErrorActionPreference = "Stop"

$repoRoot = "C:\Dev\Ai.Os"
$statePath = "Reports/forex_delivery/AIOS_FOREX_PROMOTION_PIPELINE_V1_STATE.json"
$checkpointPath = "Reports/forex_delivery/AIOS_FOREX_PROMOTION_PIPELINE_V1_CHECKPOINT.md"
$ownerApprovalCardPath = "Reports/forex_delivery/AIOS_FOREX_PROMOTION_PIPELINE_V1_OWNER_APPROVAL_CARD.md"
$nextCodexPacketPath = "Reports/forex_delivery/AIOS_FOREX_PROMOTION_PIPELINE_NEXT_CODEX_PACKET_V1.md"

Write-Output "FOREX_PROMOTION_PIPELINE_STARTED"

$pythonArgs = @(
    "automation/forex_engine/forex_promotion_pipeline_v1.py",
    "--repo-root", $repoRoot,
    "--state-path", $statePath,
    "--checkpoint-path", $checkpointPath,
    "--owner-approval-card-path", $ownerApprovalCardPath,
    "--next-codex-packet-path", $nextCodexPacketPath,
    "--report-path", "Reports/forex_delivery/AIOS_FOREX_PROMOTION_PIPELINE_V1_REPORT.md"
)

if ($DryRun) {
    $pythonArgs += "--dry-run"
}
if ($NoPublish) {
    $pythonArgs += "--no-publish"
}

$pythonOutput = & python @pythonArgs 2>&1
if ($LASTEXITCODE -ne 0) {
    throw "FOREX_PROMOTION_PIPELINE_FAILED:$pythonOutput"
}

$decision = $pythonOutput | ConvertFrom-Json -ErrorAction SilentlyContinue
if (-not $decision) {
    throw "FOREX_PROMOTION_PIPELINE_INVALID_OUTPUT:$pythonOutput"
}

$status = $decision.status
$selectedGate = $decision.selected_gate_id
$nextAction = $decision.next_action
$stopReason = if ($decision.PSObject.Properties.Name -contains "stop_reason") { $decision.stop_reason } else { "UNKNOWN" }

Write-Output "PROMOTION_STATUS:$status"
Write-Output "SELECTED_GATE:$selectedGate"
Write-Output "NEXT_ACTION:$nextAction"
Write-Output "STATE_PATH:$statePath"
Write-Output "CHECKPOINT_PATH:$checkpointPath"
Write-Output "OWNER_APPROVAL_CARD_PATH:$ownerApprovalCardPath"
Write-Output "NEXT_CODEX_PACKET_PATH:$nextCodexPacketPath"
Write-Output "FOREX_PROMOTION_PIPELINE_STOP_REASON:$stopReason"
