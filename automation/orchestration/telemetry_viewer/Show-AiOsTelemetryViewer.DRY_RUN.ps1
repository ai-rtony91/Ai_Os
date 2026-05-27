[CmdletBinding()]
param([switch]$OutputJson)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

function Get-AiOsJsonCount {
    param(
        [string]$Path,
        [string]$Property
    )

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return [pscustomobject]@{ path = $Path; status = "MISSING"; item_count = 0 }
    }

    try {
        $json = Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json
        $items = if ($json.PSObject.Properties.Name -contains $Property) { @($json.$Property) } else { @() }
        $itemCount = ($items | Measure-Object).Count
        return [pscustomobject]@{ path = $Path; status = "READ"; item_count = $itemCount }
    }
    catch {
        return [pscustomobject]@{ path = $Path; status = "INVALID_JSON"; item_count = 0 }
    }
}

$workerRegistry = Get-AiOsJsonCount -Path "automation/orchestration/workers/AIOS_WORKER_REGISTRY.json" -Property "workers"
$assignmentRegistry = Get-AiOsJsonCount -Path "automation/orchestration/workers/AIOS_WORKER_ASSIGNMENT_REGISTRY.example.json" -Property "workers"
$commandQueue = Get-AiOsJsonCount -Path "automation/orchestration/command_queue/AIOS_COMMAND_QUEUE.json" -Property "items"
$approvalQueue = Get-AiOsJsonCount -Path "automation/orchestration/approval_inbox/AIOS_APPROVAL_QUEUE.example.json" -Property "items"
$validatorChain = if (Test-Path -LiteralPath "automation/orchestration/validators/VALIDATOR_CHAIN_001.json") { "PRESENT" } else { "MISSING" }
$runtimeState = if (Test-Path -LiteralPath "automation/runtime/state/AIOS_RUNTIME_STATE.json") { "PRESENT" } else { "MISSING" }
$ledgerPath = "telemetry/work_ledger.jsonl"
$ledgerLines = if (Test-Path -LiteralPath $ledgerPath -PathType Leaf) { @(Get-Content -LiteralPath $ledgerPath).Count } else { 0 }

$viewer = [pscustomobject]@{
    schema = "AIOS_TELEMETRY_VIEWER_PREVIEW.v1"
    mode = "DRY_RUN"
    visual_only = $true
    telemetry_mutation_enabled = $false
    generated_at = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    worker_activity = [pscustomobject]@{
        registry_workers = $workerRegistry.item_count
        assignment_workers = $assignmentRegistry.item_count
    }
    packet_count = 0
    queue_state = [pscustomobject]@{
        command_queue_items = $commandQueue.item_count
    }
    approval_state = [pscustomobject]@{
        approval_queue_items = $approvalQueue.item_count
    }
    pr_state = "PREVIEW_NOT_CONNECTED"
    validator_state = $validatorChain
    runtime_state = $runtimeState
    failures = "PREVIEW_NOT_CONNECTED"
    stale_workers = "PREVIEW_NOT_CONNECTED"
    command_previews = $commandQueue.item_count
    telemetry_ledger_lines = $ledgerLines
    blocked_actions = @(
        "telemetry mutation",
        "queue mutation",
        "approval mutation",
        "worker launch",
        "command execution",
        "commit",
        "push",
        "merge",
        "secrets",
        "broker/OANDA/trading/webhook/live orders"
    )
    next_safe_action = "Use this viewer as read-only HUD evidence only."
}

if ($OutputJson) {
    $viewer | ConvertTo-Json -Depth 8
    exit 0
}

Write-Host "AI_OS Telemetry Viewer"
Write-Host "Mode: DRY_RUN"
Write-Host "Visual only: $($viewer.visual_only)"
Write-Host "Workers: registry=$($viewer.worker_activity.registry_workers); assignments=$($viewer.worker_activity.assignment_workers)"
Write-Host "Command queue items: $($viewer.queue_state.command_queue_items)"
Write-Host "Approval queue items: $($viewer.approval_state.approval_queue_items)"
Write-Host "Validator state: $($viewer.validator_state)"
Write-Host "Runtime state: $($viewer.runtime_state)"
Write-Host "Telemetry ledger lines: $($viewer.telemetry_ledger_lines)"
Write-Host "Command previews: $($viewer.command_previews)"
Write-Host "Next safe action: $($viewer.next_safe_action)"
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
