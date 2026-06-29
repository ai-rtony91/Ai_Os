param(
    [switch]$DryRun,
    [switch]$NoPublish,
    [int]$MaxCycles = 12,
    [int]$MaxMinutes = 480
)

$ErrorActionPreference = "Stop"

$repoRoot = "C:\Dev\Ai.Os"
$statePath = "Reports/forex_delivery/AIOS_FOREX_AUTONOMOUS_CAMPAIGN_MANAGER_V1_STATE.json"
$checkpointPath = "Reports/forex_delivery/AIOS_FOREX_AUTONOMOUS_CAMPAIGN_MANAGER_V1_CHECKPOINT.md"
$nextPromptPath = "Reports/forex_delivery/AIOS_FOREX_AUTONOMOUS_CAMPAIGN_MANAGER_NEXT_CODEX_PROMPT_V1.md"

Write-Output "FOREX_AUTONOMOUS_CAMPAIGN_MANAGER_STARTED"

$pythonArgs = @(
    "automation/forex_engine/forex_autonomous_campaign_manager_v1.py",
    "--state-path", $statePath,
    "--checkpoint-path", $checkpointPath,
    "--next-prompt-path", $nextPromptPath,
    "--max-cycles", $MaxCycles.ToString(),
    "--max-minutes", $MaxMinutes.ToString()
)

if ($DryRun) {
    $pythonArgs += "--dry-run"
}
if ($NoPublish) {
    $pythonArgs += "--no-publish"
}

$pythonOutput = & python @pythonArgs 2>&1
if ($LASTEXITCODE -ne 0) {
    throw "FOREX_AUTONOMOUS_CAMPAIGN_MANAGER_FAILED:$pythonOutput"
}

$decision = $pythonOutput | ConvertFrom-Json -ErrorAction SilentlyContinue
if (-not $decision) {
    throw "FOREX_AUTONOMOUS_CAMPAIGN_MANAGER_INVALID_OUTPUT:$pythonOutput"
}

Write-Output "SELECTED_STAGE:$($decision.selected_stage_id)"
Write-Output "NEXT_ACTION:$($decision.next_action)"
Write-Output "CHECKPOINT_PATH:$checkpointPath"
Write-Output "NEXT_CODEX_PROMPT_PATH:$nextPromptPath"
if ($decision.PSObject.Properties.Name -contains "stop_reason") {
    Write-Output "FOREX_AUTONOMOUS_CAMPAIGN_MANAGER_STOP_REASON:$($decision.stop_reason)"
} else {
    Write-Output "FOREX_AUTONOMOUS_CAMPAIGN_MANAGER_STOP_REASON:UNKNOWN"
}
