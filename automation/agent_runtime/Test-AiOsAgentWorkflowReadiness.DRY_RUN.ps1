$ErrorActionPreference = "Stop"

Write-Host "AI_OS Agent Workflow Readiness DRY_RUN"
Write-Host "Mode: read-only"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$runtimeDir = Join-Path $repoRoot "docs\AI_OS\agent_runtime"
$dashboardFixture = Join-Path $repoRoot "apps\dashboard\mock-data\agent-workflow-status.example.json"
$queuePath = Join-Path $runtimeDir "AGENT_RUNTIME_QUEUE.json"
$ownershipPath = Join-Path $runtimeDir "AGENT_RUNTIME_OWNERSHIP_RULES.json"
$lifecyclePath = Join-Path $runtimeDir "AGENT_WORKFLOW_TASK_LIFECYCLE.json"
$handoffPath = Join-Path $runtimeDir "AGENT_WORKFLOW_HANDOFF_PACKET_SCHEMA.json"
$matrixPath = Join-Path $runtimeDir "AGENT_WORKFLOW_BLOCKED_ACTIONS_MATRIX.json"

$requiredFiles = @(
  "docs\AI_OS\agent_runtime\AGENT_WORKFLOW_STATE_MACHINE.md",
  "docs\AI_OS\agent_runtime\AGENT_WORKFLOW_TASK_LIFECYCLE.json",
  "docs\AI_OS\agent_runtime\AGENT_WORKFLOW_HANDOFF_PACKET_SCHEMA.json",
  "docs\AI_OS\agent_runtime\AGENT_WORKFLOW_RUNNER_DRY_RUN_SPEC.md",
  "docs\AI_OS\agent_runtime\AGENT_WORKFLOW_VALIDATOR_CHAIN.md",
  "docs\AI_OS\agent_runtime\AGENT_WORKFLOW_BLOCKED_ACTIONS_MATRIX.json",
  "docs\AI_OS\agent_runtime\AGENT_WORKFLOW_NEXT_ACTION_ROUTER.md",
  "docs\AI_OS\agent_runtime\AGENT_WORKFLOW_IMPLEMENTATION_PLAN.md",
  "docs\AI_OS\agent_runtime\AGENT_WORKFLOW_CODEX_SUMMARY.md",
  "automation\agent_runtime\Test-AiOsAgentWorkflowReadiness.DRY_RUN.ps1",
  "automation\agent_runtime\Get-AiOsAgentWorkflowSnapshot.DRY_RUN.ps1",
  "apps\dashboard\mock-data\agent-workflow-status.example.json",
  "Reports\health\PHASE_15_5_AGENT_WORKFLOW_HEALTH_DRY_RUN.md",
  "Reports\checkpoints\CHECKPOINT_PHASE_15_5_AGENT_WORKFLOW_ARCHITECTURE_DRY_RUN.md"
)

$requiredStates = @(
  "proposed",
  "queued",
  "ownership_checked",
  "blocked_path_checked",
  "ready_for_runner_preview",
  "runner_previewed",
  "ready_for_apply",
  "apply_completed",
  "validation_running",
  "validation_passed",
  "validation_failed",
  "ready_for_review",
  "done",
  "blocked",
  "deferred"
)

$requiredFields = @(
  "task_id",
  "created_time",
  "source",
  "user_goal",
  "phase",
  "stage",
  "lane",
  "assigned_agent",
  "task_type",
  "objective",
  "allowed_paths",
  "blocked_paths",
  "required_inputs",
  "expected_outputs",
  "validation_required",
  "validation_command",
  "current_status",
  "safety_status",
  "blocked_reason",
  "user_approval_required",
  "next_action",
  "output_summary_path",
  "validation_report_path"
)

$requiredAgents = @(
  "architecture_agent",
  "automation_agent",
  "ui_agent",
  "integration_agent",
  "reporting_agent",
  "risk_gate_agent",
  "backtest_agent",
  "trading_research_agent",
  "scaffold_gap_agent",
  "schema_gap_agent",
  "validator_gap_agent",
  "mock_data_agent",
  "naming_agent",
  "docs_patch_agent",
  "cleanup_agent",
  "dependency_notes_agent"
)

$requiredBlockedCategories = @(
  "live trading",
  "broker execution",
  "OANDA execution",
  "API keys",
  "secrets",
  "real webhooks",
  "real orders",
  "external LLM install",
  "background execution",
  "scheduled automation",
  "startup persistence",
  "payments",
  "account login systems",
  "Play Store submission",
  "profit guarantees"
)

$failures = New-Object System.Collections.Generic.List[string]

foreach ($relativePath in $requiredFiles) {
  $fullPath = Join-Path $repoRoot $relativePath
  if (-not (Test-Path -LiteralPath $fullPath)) {
    $failures.Add("Missing required file: $relativePath")
  }
}

$jsonFiles = @()
if (Test-Path -LiteralPath $runtimeDir) {
  $jsonFiles += Get-ChildItem -LiteralPath $runtimeDir -Filter "*.json" -File
}
if (Test-Path -LiteralPath $dashboardFixture) {
  $jsonFiles += Get-Item -LiteralPath $dashboardFixture
}

foreach ($jsonFile in $jsonFiles) {
  try {
    Get-Content -LiteralPath $jsonFile.FullName -Raw | ConvertFrom-Json | Out-Null
  } catch {
    $failures.Add("JSON parse failed: $($jsonFile.FullName)")
  }
}

if (Test-Path -LiteralPath $lifecyclePath) {
  $lifecycle = Get-Content -LiteralPath $lifecyclePath -Raw | ConvertFrom-Json
  foreach ($state in $requiredStates) {
    if ($lifecycle.workflow_states -notcontains $state) {
      $failures.Add("Missing workflow state: $state")
    }
  }
}

if (Test-Path -LiteralPath $handoffPath) {
  $handoff = Get-Content -LiteralPath $handoffPath -Raw | ConvertFrom-Json
  foreach ($field in $requiredFields) {
    if ($handoff.required_fields -notcontains $field) {
      $failures.Add("Missing handoff field: $field")
    }
  }
}

if (Test-Path -LiteralPath $ownershipPath) {
  $ownership = Get-Content -LiteralPath $ownershipPath -Raw | ConvertFrom-Json
  $agentNames = $ownership.agents.PSObject.Properties.Name
  foreach ($agent in $requiredAgents) {
    if ($agentNames -notcontains $agent) {
      $failures.Add("Missing agent role: $agent")
    }
  }
}

if (Test-Path -LiteralPath $matrixPath) {
  $matrix = Get-Content -LiteralPath $matrixPath -Raw | ConvertFrom-Json
  $categories = $matrix.blocked_actions | ForEach-Object { $_.category }
  foreach ($category in $requiredBlockedCategories) {
    if ($categories -notcontains $category) {
      $failures.Add("Missing blocked action category: $category")
    }
  }
}

if (Test-Path -LiteralPath $queuePath) {
  $queue = Get-Content -LiteralPath $queuePath -Raw | ConvertFrom-Json
  $hardBlockedPathPatterns = @(
    "^\s*\.git/?\s*$",
    "^\s*\.codex_backups/?\s*$",
    "^\s*\.env\s*$",
    "^apps/dashboard/css/",
    "^apps/dashboard/js/",
    "^apps/dashboard/assets/"
  )
  foreach ($task in $queue.tasks) {
    foreach ($path in @($task.allowed_paths)) {
      foreach ($pattern in $hardBlockedPathPatterns) {
        if ($path -match $pattern) {
          $failures.Add("Task $($task.task_id) allowed_paths contains blocked path: $path")
        }
      }
    }
  }
}

if (Test-Path -LiteralPath $dashboardFixture) {
  $dashboard = Get-Content -LiteralPath $dashboardFixture -Raw | ConvertFrom-Json
  if ($dashboard.live_execution_status -ne "BLOCKED") { $failures.Add("Dashboard live_execution_status is not BLOCKED.") }
  if ($dashboard.broker_status -ne "BLOCKED") { $failures.Add("Dashboard broker_status is not BLOCKED.") }
  if ($dashboard.oanda_status -ne "BLOCKED") { $failures.Add("Dashboard oanda_status is not BLOCKED.") }
  if ($dashboard.api_key_status -ne "BLOCKED") { $failures.Add("Dashboard api_key_status is not BLOCKED.") }
  if ($dashboard.secrets_status -ne "BLOCKED") { $failures.Add("Dashboard secrets_status is not BLOCKED.") }
  if ($dashboard.external_llm_install_status -ne "NOT_ENABLED") { $failures.Add("Dashboard external_llm_install_status is not NOT_ENABLED.") }
}

$scanTargets = @()
if (Test-Path -LiteralPath $runtimeDir) { $scanTargets += Get-ChildItem -LiteralPath $runtimeDir -File }
if (Test-Path -LiteralPath (Join-Path $repoRoot "automation\agent_runtime")) { $scanTargets += Get-ChildItem -LiteralPath (Join-Path $repoRoot "automation\agent_runtime") -File }
if (Test-Path -LiteralPath $dashboardFixture) { $scanTargets += Get-Item -LiteralPath $dashboardFixture }

$combinedText = ""
foreach ($file in $scanTargets) {
  $combinedText += "`n"
  $combinedText += Get-Content -LiteralPath $file.FullName -Raw
}

$unsafePatterns = @(
  '"live_execution_status"\s*:\s*"ENABLED"',
  '"broker_status"\s*:\s*"ENABLED"',
  '"oanda_status"\s*:\s*"ENABLED"',
  '"api_key_status"\s*:\s*"ENABLED"',
  '"secrets_status"\s*:\s*"ENABLED"',
  '"startup_persistence_status"\s*:\s*"ENABLED"',
  '"scheduled_automation_status"\s*:\s*"ENABLED"',
  '"background_execution_status"\s*:\s*"ENABLED"'
)

foreach ($pattern in $unsafePatterns) {
  if ($combinedText -match $pattern) {
    $failures.Add("Unsafe ENABLED status found for pattern: $pattern")
  }
}

Write-Host "Git status:"
git status --short --branch

if ($failures.Count -eq 0) {
  Write-Host "PASS: Agent workflow files are present, JSON parses, states exist, roles exist, and safety locks remain blocked."
  exit 0
}

Write-Host "FAIL: Agent workflow readiness check found issues."
foreach ($failure in $failures) {
  Write-Host "- $failure"
}
exit 1

