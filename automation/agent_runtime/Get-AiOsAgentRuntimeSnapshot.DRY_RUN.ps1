$ErrorActionPreference = "Stop"

Write-Host "AI_OS Agent Runtime Snapshot DRY_RUN"
Write-Host "Mode: read-only"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$statusPath = Join-Path $repoRoot "docs\AI_OS\agent_runtime\AGENT_RUNTIME_STATUS.json"
$queuePath = Join-Path $repoRoot "docs\AI_OS\agent_runtime\AGENT_RUNTIME_QUEUE.json"
$gapPath = Join-Path $repoRoot "docs\AI_OS\agent_runtime\AGENT_RUNTIME_GAP_LOG.json"

$status = Get-Content -LiteralPath $statusPath -Raw | ConvertFrom-Json
$queue = Get-Content -LiteralPath $queuePath -Raw | ConvertFrom-Json
$gapLog = Get-Content -LiteralPath $gapPath -Raw | ConvertFrom-Json

$tasksByStatus = $queue.tasks | Group-Object -Property current_status | Sort-Object -Property Name
$gapsByPriority = $gapLog.gaps | Group-Object -Property priority | Sort-Object -Property Name

Write-Host "Runtime status: $($status.runtime_status)"
Write-Host "Mode: $($status.mode)"
Write-Host "Live execution: $($status.live_execution_status)"
Write-Host "Broker: $($status.broker_status)"
Write-Host "OANDA: $($status.oanda_status)"
Write-Host "External LLM install: $($status.external_llm_install_status)"
Write-Host "Current focus: $($status.current_focus)"
Write-Host "Next action: $($status.next_action)"

Write-Host "Tasks by status:"
foreach ($group in $tasksByStatus) {
  Write-Host "- $($group.Name): $($group.Count)"
}

Write-Host "Gaps by priority:"
foreach ($group in $gapsByPriority) {
  Write-Host "- $($group.Name): $($group.Count)"
}

