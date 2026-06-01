param(
  [string]$RepoRoot = "."
)

$ErrorActionPreference = "Stop"
$ResolvedRepoRoot = (Resolve-Path $RepoRoot).Path
$failures = New-Object System.Collections.Generic.List[string]

function Add-Failure {
  param([string]$Message)
  $script:failures.Add($Message) | Out-Null
  Write-Host "FAIL: $Message" -ForegroundColor Red
}

function Test-JsonFile {
  param([string]$RelativePath)
  $fullPath = Join-Path $ResolvedRepoRoot $RelativePath
  if (-not (Test-Path -LiteralPath $fullPath -PathType Leaf)) {
    Add-Failure "Missing JSON file: $RelativePath"
    return $null
  }
  try {
    return Get-Content -LiteralPath $fullPath -Raw | ConvertFrom-Json
  } catch {
    Add-Failure "JSON parse failed: $RelativePath :: $($_.Exception.Message)"
    return $null
  }
}

Write-Host "AI_OS Workflow Orchestrator DRY_RUN Validator" -ForegroundColor Cyan
Write-Host "Repo: $ResolvedRepoRoot"

$requiredFiles = @(
  "automation/operator/Invoke-AiOsWorkflowOrchestrator.ps1",
  "automation/operator/Test-AiOsWorkflowOrchestrator.DRY_RUN.ps1",
  "apps/dashboard/mock-data/aios-workflow-orchestrator-v1.example.json",
  "docs/concepts/aios-dispatcher-orchestration-concepts.md"
)

foreach ($file in $requiredFiles) {
  if (-not (Test-Path -LiteralPath (Join-Path $ResolvedRepoRoot $file) -PathType Leaf)) {
    Add-Failure "Missing required file: $file"
  }
}

$fixture = Test-JsonFile -RelativePath "apps/dashboard/mock-data/aios-workflow-orchestrator-v1.example.json"
if ($fixture) {
  if ($fixture.mode -ne "DRY_RUN_OPERATOR_APPROVED_ONLY") {
    Add-Failure "Fixture mode must be DRY_RUN_OPERATOR_APPROVED_ONLY."
  }
  foreach ($requiredSystem in @("work_queue", "worker_assignment", "dry_run_report_collection", "approval_inbox", "validator_chain", "controlled_apply_lane", "commit_package_builder", "final_git_status_check")) {
    if (@($fixture.systems_connected) -notcontains $requiredSystem) {
      Add-Failure "Fixture missing connected system: $requiredSystem"
    }
  }
  if ($fixture.blocked_actions.autonomous_apply -ne $true) {
    Add-Failure "Fixture must block autonomous APPLY."
  }
  if ($fixture.blocked_actions.autonomous_commit -ne $true) {
    Add-Failure "Fixture must block autonomous commit."
  }
  if ($fixture.blocked_actions.autonomous_push -ne $true) {
    Add-Failure "Fixture must block autonomous push."
  }
  if ($fixture.blocked_actions.git_add_dot -ne $true) {
    Add-Failure "Fixture must block git add dot."
  }
}

$adapterPath = Join-Path $ResolvedRepoRoot "automation/operator/Get-AiOsOperatorRegistryAdapter.DRY_RUN.ps1"
if (-not (Test-Path -LiteralPath $adapterPath -PathType Leaf)) {
  Add-Failure "Missing operator registry adapter."
} else {
  $adapter = & powershell -NoProfile -ExecutionPolicy Bypass -File $adapterPath -RepoRoot $ResolvedRepoRoot -OutputJson | ConvertFrom-Json
  if ($adapter.source.primary_worker_source -ne "canonical_runtime_registry") {
    Add-Failure "Operator registry adapter must be the primary worker routing source."
  }
  if ($adapter.legacy_operator_summary.compatibility_evidence_only -ne $true) {
    Add-Failure "Legacy worker registry must be compatibility evidence only."
  }
  if (@($adapter.operator_routes).Count -eq 0) {
    Add-Failure "Operator registry adapter must expose operator routes."
  }
}

$invokePath = Join-Path $ResolvedRepoRoot "automation/operator/Invoke-AiOsWorkflowOrchestrator.ps1"
if (Test-Path -LiteralPath $invokePath -PathType Leaf) {
  $invokeText = Get-Content -LiteralPath $invokePath -Raw
  foreach ($requiredToken in @("AIOS_OPERATOR_NEXT_ACTION_PACKET.md", "Get-AiOsOperatorRegistryAdapter.DRY_RUN.ps1", "operator_registry_adapter", "compatibility_evidence_only", "work-intelligence-queue-v1.example.json", "aios-approval-inbox-v1.example.json", "aios-validator-chain-v1.example.json", "AIOS_CONTROLLED_APPLY_QUEUE.example.json", "AIOS_PHASE_27_COMMIT_PACKAGE.example.json", "git status --short --branch")) {
    if (-not $invokeText.Contains($requiredToken)) {
      Add-Failure "Orchestrator missing token: $requiredToken"
    }
  }
  foreach ($blockedPattern in @("Invoke-Expression", "Start-Process", "git add .", "git add -A", "git commit", "git push")) {
    if ($invokeText.Contains($blockedPattern)) {
      Add-Failure "Orchestrator contains blocked automation token: $blockedPattern"
    }
  }
}

$docPath = Join-Path $ResolvedRepoRoot "docs/concepts/aios-dispatcher-orchestration-concepts.md"
if (Test-Path -LiteralPath $docPath -PathType Leaf) {
  $docText = Get-Content -LiteralPath $docPath -Raw
  foreach ($requiredText in @("DRY_RUN", "operator control", "work packets", "approval inbox", "validator chains", "commit packages")) {
    if (-not $docText.Contains($requiredText)) {
      Add-Failure "Documentation missing required text: $requiredText"
    }
  }
}

if ($failures.Count -gt 0) {
  Write-Host ""
  Write-Host "AI_OS WORKFLOW ORCHESTRATOR VALIDATION: FAIL" -ForegroundColor Red
  exit 1
}

Write-Host ""
Write-Host "AI_OS WORKFLOW ORCHESTRATOR VALIDATION: PASS" -ForegroundColor Green
exit 0
