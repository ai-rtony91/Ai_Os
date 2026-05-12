$ErrorActionPreference = "Stop"

Write-Host "AI_OS Agent Workflow Snapshot DRY_RUN"
Write-Host "Mode: read-only"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$runtimeDir = Join-Path $repoRoot "docs\AI_OS\agent_runtime"
$lifecyclePath = Join-Path $runtimeDir "AGENT_WORKFLOW_TASK_LIFECYCLE.json"
$matrixPath = Join-Path $runtimeDir "AGENT_WORKFLOW_BLOCKED_ACTIONS_MATRIX.json"
$dashboardPath = Join-Path $repoRoot "apps\dashboard\mock-data\agent-workflow-status.example.json"

$lifecycle = Get-Content -LiteralPath $lifecyclePath -Raw | ConvertFrom-Json
$matrix = Get-Content -LiteralPath $matrixPath -Raw | ConvertFrom-Json
$dashboard = Get-Content -LiteralPath $dashboardPath -Raw | ConvertFrom-Json

Write-Host "Runtime status: $($dashboard.runtime_status)"
Write-Host "Active lane: $($dashboard.active_lane)"
Write-Host "Active agent: $($dashboard.active_agent)"
Write-Host "Queued tasks: $($dashboard.queued_tasks)"
Write-Host "Blocked tasks: $($dashboard.blocked_tasks)"
Write-Host "Ready for review tasks: $($dashboard.ready_for_review_tasks)"
Write-Host "Last validator status: $($dashboard.last_validator_status)"
Write-Host "Next safe action: $($dashboard.next_safe_action)"
Write-Host "Live execution: $($dashboard.live_execution_status)"
Write-Host "Broker: $($dashboard.broker_status)"
Write-Host "OANDA: $($dashboard.oanda_status)"
Write-Host "External LLM install: $($dashboard.external_llm_install_status)"
Write-Host "Workflow states: $($lifecycle.workflow_states.Count)"
Write-Host "Blocked action categories: $($matrix.blocked_actions.Count)"

