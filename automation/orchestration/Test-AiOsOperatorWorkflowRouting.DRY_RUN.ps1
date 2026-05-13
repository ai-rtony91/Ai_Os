Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$mockRoot = Join-Path $repoRoot "apps\dashboard\mock-data"

$files = @(
  "aios-morning-execution-packet-v1.example.json",
  "aios-guided-action-queue-v1.example.json",
  "aios-validator-chain-v1.example.json",
  "aios-apply-routing-v1.example.json",
  "aios-session-resume-state-v1.example.json"
)

$errors = New-Object System.Collections.Generic.List[string]

function Read-AiOsJson {
  param(
    [Parameter(Mandatory = $true)]
    [string] $Path
  )

  if (-not (Test-Path -LiteralPath $Path)) {
    throw "Missing JSON file: $Path"
  }

  return Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json
}

foreach ($file in $files) {
  $path = Join-Path $mockRoot $file
  try {
    $null = Read-AiOsJson -Path $path
  } catch {
    $errors.Add($_.Exception.Message)
  }
}

$morning = Read-AiOsJson -Path (Join-Path $mockRoot "aios-morning-execution-packet-v1.example.json")
$actionQueue = Read-AiOsJson -Path (Join-Path $mockRoot "aios-guided-action-queue-v1.example.json")
$validatorChain = Read-AiOsJson -Path (Join-Path $mockRoot "aios-validator-chain-v1.example.json")
$applyRouting = Read-AiOsJson -Path (Join-Path $mockRoot "aios-apply-routing-v1.example.json")
$resumeState = Read-AiOsJson -Path (Join-Path $mockRoot "aios-session-resume-state-v1.example.json")

if ([string]::IsNullOrWhiteSpace($morning.next_safe_action)) {
  $errors.Add("Morning packet is missing next_safe_action.")
}

$requiredMorningFields = @(
  "session_date",
  "repo_path",
  "current_phase",
  "active_objective",
  "approved_scope",
  "blocked_actions",
  "pending_approvals",
  "validator_sequence",
  "next_safe_action",
  "checkpoint_reminder",
  "commit_push_reminder"
)

foreach ($field in $requiredMorningFields) {
  if (-not ($morning.PSObject.Properties.Name -contains $field)) {
    $errors.Add("Morning packet missing required field: $field")
  }
}

foreach ($item in @($actionQueue.queue_items)) {
  if ([string]::IsNullOrWhiteSpace($item.next_safe_action)) {
    $errors.Add("Guided action queue item is missing next_safe_action.")
  }
}

$requiredValidators = @(
  "ownership",
  "conflict",
  "stale_worker",
  "merge_package",
  "dashboard_integrity",
  "protected_file_boundary"
)

$validatorIds = @($validatorChain.validator_chain | ForEach-Object { $_.validator_id })
foreach ($required in $requiredValidators) {
  if ($validatorIds -notcontains $required) {
    $errors.Add("Validator chain missing required validator: $required")
  }
}

foreach ($route in @($applyRouting.routes)) {
  if ([string]::IsNullOrWhiteSpace($route.current_state)) {
    $errors.Add("APPLY route is missing current_state.")
  }
  if ([string]::IsNullOrWhiteSpace($route.next_safe_action)) {
    $errors.Add("APPLY route is missing next_safe_action.")
  }
  if ($route.current_state -eq "MERGE_READY" -and $route.approval_required -eq $true) {
    $errors.Add("Route cannot be MERGE_READY while approval_required is true.")
  }
}

if ($resumeState.PSObject.Properties.Name -contains "unfinished_apply_packages") {
  foreach ($package in @($resumeState.unfinished_apply_packages)) {
    if ($package.status -eq "MERGE_READY") {
      $errors.Add("Resume state cannot promote unfinished APPLY package as MERGE_READY.")
    }
  }
}

$requiredResumeFields = @(
  "last_completed_phase",
  "current_in_progress_phase",
  "active_workers",
  "unresolved_conflicts",
  "stale_workers",
  "uncommitted_files",
  "last_known_git_status",
  "resume_warning_state"
)

foreach ($field in $requiredResumeFields) {
  if (-not ($resumeState.PSObject.Properties.Name -contains $field)) {
    $errors.Add("Session resume state missing required field: $field")
  }
}

$protectedViolation = @(@($applyRouting.routes.blocked_files) | Where-Object {
  $_ -match "README\.md|AGENTS\.md|RISK_POLICY\.md|SOURCE_LOG\.md|ERROR_LOG\.md|HALLUCINATION_LOG\.md|AAR\.md|DAILY_REPORT\.md|White_Paper\.md"
})

if ($protectedViolation.Count -gt 0) {
  $errors.Add("Protected root file appears in blocked_files review scope. Operator approval required before any protected-file route.")
}

Write-Host "AI_OS Operator Workflow Routing DRY_RUN Validator"
Write-Host "Repo: $repoRoot"

if ($errors.Count -gt 0) {
  foreach ($errorItem in $errors) {
    Write-Host "ERROR: $errorItem"
  }
  throw "AI_OS OPERATOR WORKFLOW ROUTING VALIDATION: FAIL"
}

Write-Host "AI_OS OPERATOR WORKFLOW ROUTING VALIDATION: PASS"
