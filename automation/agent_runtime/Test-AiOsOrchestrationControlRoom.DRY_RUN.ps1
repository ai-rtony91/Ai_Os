$ErrorActionPreference = "Stop"

Write-Host "AI_OS Orchestration Control Room DRY_RUN"
Write-Host "Mode: read-only"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$fixturePath = Join-Path $repoRoot "apps\dashboard\mock-data\aios-orchestration-control-room.example.json"

if (-not (Test-Path -LiteralPath $fixturePath)) {
  throw "Missing orchestration control room fixture."
}

$fixture = Get-Content -LiteralPath $fixturePath -Raw | ConvertFrom-Json

$requiredSources = @(
  "docs/AI_OS/agent_runtime/AGENT_RUNTIME_QUEUE.json",
  "docs/AI_OS/agent_runtime/AGENT_RUNTIME_STATUS.json",
  "docs/AI_OS/agent_runtime/AGENT_RUNTIME_OWNERSHIP_RULES.json",
  "docs/AI_OS/agent_runtime/AGENT_WORKFLOW_TASK_LIFECYCLE.json",
  "docs/AI_OS/agent_runtime/AGENT_WORKFLOW_BLOCKED_ACTIONS_MATRIX.json"
)

$requiredCards = @(
  "Active Queue",
  "Agent Ownership",
  "Task State",
  "Validator Status",
  "Blocked Action Locks",
  "Next Safe Action",
  "Runtime Health",
  "Human Approval Gate"
)

$criticalCards = @(
  "Active Queue",
  "Task State",
  "Blocked Action Locks",
  "Next Safe Action"
)

$blockedFields = @(
  "live_execution_status",
  "broker_status",
  "oanda_status",
  "api_key_status",
  "secrets_status",
  "real_webhook_status",
  "real_order_status",
  "background_execution_status",
  "scheduled_automation_status",
  "startup_persistence_status"
)

foreach ($source in $requiredSources) {
  if ($fixture.source_references -notcontains $source) {
    throw "Missing source reference: $source"
  }
}

$cardTitles = $fixture.cards | ForEach-Object { $_.title }
foreach ($card in $requiredCards) {
  if ($cardTitles -notcontains $card) {
    throw "Missing visible panel card: $card"
  }
}

foreach ($card in $criticalCards) {
  $match = $fixture.cards | Where-Object { $_.title -eq $card } | Select-Object -First 1
  if (-not $match) {
    throw "Missing critical card: $card"
  }
  if ($match.default_visible -ne $true) {
    throw "Critical card must be visible by default: $card"
  }
}

$advancedCards = $fixture.cards | Where-Object { $_.default_visible -eq $false }
if ($advancedCards.Count -lt 4) {
  throw "Advanced diagnostics must contain ownership, validator, runtime health, and approval gate cards."
}

if ($fixture.display.advanced_diagnostics_collapsed -ne $true) {
  throw "Advanced diagnostics must be collapsed by default."
}

if ($fixture.display.mobile_layout -ne "single_column_no_horizontal_scroll") {
  throw "Mobile layout rule is missing."
}

foreach ($field in $blockedFields) {
  if ($fixture.$field -ne "BLOCKED") {
    throw "$field must remain BLOCKED."
  }
  if ($fixture.safety_locks.$field -ne "BLOCKED") {
    throw "safety_locks.$field must remain BLOCKED."
  }
}

if ($fixture.external_llm_install_status -ne "NOT_ENABLED") {
  throw "external_llm_install_status must remain NOT_ENABLED."
}

if ($fixture.safety_locks.external_llm_install_status -ne "NOT_ENABLED") {
  throw "safety_locks.external_llm_install_status must remain NOT_ENABLED."
}

Write-Host "PASS: Orchestration control room fixture is local mock-only, reviewable, and safety locked."
