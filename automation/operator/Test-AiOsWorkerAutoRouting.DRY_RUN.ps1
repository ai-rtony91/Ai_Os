param(
  [string]$RoutingPacketPath = "Reports/operator/AIOS_WORKER_ROUTING_PACKET.json",
  [string]$RegistryPath = "automation/operator/AIOS_PARALLEL_WORKER_REGISTRY.json"
)

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path ".").Path
$failures = New-Object System.Collections.Generic.List[string]

function Add-Failure {
  param([string]$Message)
  $script:failures.Add($Message) | Out-Null
  Write-Host "FAIL: $Message" -ForegroundColor Red
}

function Read-Json {
  param([string]$RelativePath)
  $fullPath = Join-Path $RepoRoot $RelativePath
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

function Read-OptionalJson {
  param([string]$RelativePath)
  $fullPath = Join-Path $RepoRoot $RelativePath
  if (-not (Test-Path -LiteralPath $fullPath -PathType Leaf)) {
    return $null
  }
  try {
    return Get-Content -LiteralPath $fullPath -Raw | ConvertFrom-Json
  } catch {
    Add-Failure "JSON parse failed: $RelativePath :: $($_.Exception.Message)"
    return $null
  }
}

Write-Host "AI_OS Worker Auto-Routing DRY_RUN Validator" -ForegroundColor Cyan
Write-Host "Repo: $RepoRoot"

$requiredFiles = @(
  "automation/operator/Invoke-AiOsWorkflowOrchestrator.ps1",
  "automation/operator/Start-AiOsParallelDryRunCrew.ps1",
  "automation/operator/Get-AiOsOperatorRegistryAdapter.DRY_RUN.ps1",
  "automation/operator/Test-AiOsWorkerAutoRouting.DRY_RUN.ps1",
  "apps/dashboard/mock-data/aios-worker-auto-routing-v1.example.json",
  "docs/concepts/aios-dispatcher-orchestration-concepts.md"
)

foreach ($file in $requiredFiles) {
  if (-not (Test-Path -LiteralPath (Join-Path $RepoRoot $file) -PathType Leaf)) {
    Add-Failure "Missing required file: $file"
  }
}

$registry = Read-Json -RelativePath $RegistryPath
$routing = Read-OptionalJson -RelativePath $RoutingPacketPath
$fixture = Read-Json -RelativePath "apps/dashboard/mock-data/aios-worker-auto-routing-v1.example.json"

$adapterScript = Join-Path $RepoRoot "automation/operator/Get-AiOsOperatorRegistryAdapter.DRY_RUN.ps1"
$adapter = $null
if (-not (Test-Path -LiteralPath $adapterScript -PathType Leaf)) {
  Add-Failure "Missing operator registry adapter: automation/operator/Get-AiOsOperatorRegistryAdapter.DRY_RUN.ps1"
} else {
  try {
    $adapter = & powershell -NoProfile -ExecutionPolicy Bypass -File $adapterScript -RepoRoot $RepoRoot -OutputJson | ConvertFrom-Json
  } catch {
    Add-Failure "Operator registry adapter failed: $($_.Exception.Message)"
  }
}

if ($adapter) {
  if ($adapter.schema -ne "AIOS_OPERATOR_REGISTRY_ADAPTER.v1") {
    Add-Failure "Operator registry adapter schema mismatch."
  }
  if ($adapter.mode -ne "READ_ONLY") {
    Add-Failure "Operator registry adapter must be READ_ONLY."
  }
  if ($adapter.source.primary_worker_source -ne "canonical_runtime_registry") {
    Add-Failure "Operator registry adapter must declare canonical_runtime_registry as primary worker source."
  }
  if ($adapter.source.legacy_operator_registry_role -ne "compatibility_evidence_only") {
    Add-Failure "Legacy operator registry must be compatibility evidence only."
  }
  if (@($adapter.runtime_workers).Count -eq 0) {
    Add-Failure "Operator registry adapter must expose runtime_workers."
  }
  if (@($adapter.operator_routes).Count -ne @($adapter.runtime_workers).Count) {
    Add-Failure "Operator registry adapter operator_routes must match runtime_workers count."
  }
  foreach ($route in @($adapter.operator_routes)) {
    foreach ($field in @("worker_id", "numeric_id", "label", "lane", "allowed_paths", "blocked_paths", "dry_run_task", "report_path", "validation_commands", "stop_condition", "source")) {
      if (-not ($route.PSObject.Properties.Name -contains $field)) {
        Add-Failure "Adapter operator route missing field: $field"
      }
    }
    if ($route.source -ne "canonical_runtime_registry") {
      Add-Failure "Adapter operator route must identify canonical runtime registry source."
    }
    if ([string]::IsNullOrWhiteSpace([string]$route.dry_run_task)) {
      Add-Failure "Adapter operator route $($route.worker_id) dry_run_task is blank."
    }
    if (@($route.validation_commands).Count -eq 0) {
      Add-Failure "Adapter operator route $($route.worker_id) missing validation_commands."
    }
    if ($route.stop_condition -notmatch "No APPLY" -or $route.stop_condition -notmatch "no commit" -or $route.stop_condition -notmatch "no push") {
      Add-Failure "Adapter operator route $($route.worker_id) stop condition must block APPLY, commit, and push."
    }
  }
  if ($adapter.safety.writes_files -ne $false -or $adapter.safety.launches_workers -ne $false -or $adapter.safety.changes_json -ne $false) {
    Add-Failure "Operator registry adapter must remain read-only and non-launching."
  }
  if ($adapter.legacy_operator_summary.active_primary_source -ne $false -or $adapter.legacy_operator_summary.compatibility_evidence_only -ne $true) {
    Add-Failure "Legacy operator summary must prove the legacy registry is not the primary source."
  }
}

if (-not $adapter) {
  Add-Failure "Operator registry adapter is required as the primary worker source."
}

if ($fixture) {
  if ($fixture.mode -ne "DRY_RUN_ONLY") {
    Add-Failure "Fixture mode must be DRY_RUN_ONLY."
  }
  if ($fixture.routing_packet_path -ne $RoutingPacketPath) {
    Add-Failure "Fixture routing_packet_path mismatch."
  }
  if ($fixture.blocked_actions.autonomous_apply -ne $true -or $fixture.blocked_actions.autonomous_commit -ne $true -or $fixture.blocked_actions.autonomous_push -ne $true) {
    Add-Failure "Fixture must block autonomous APPLY, commit, and push."
  }
}

if ($routing) {
  if ($routing.schema -ne "AIOS_WORKER_ROUTING_PACKET.v1") {
    Add-Failure "Routing packet schema mismatch."
  }
  if ($routing.mode -ne "DRY_RUN_ONLY") {
    Add-Failure "Routing packet mode must be DRY_RUN_ONLY."
  }
  if (@($routing.workers).Count -ne 8) {
    Add-Failure "Routing packet must include 8 workers."
  }
  foreach ($worker in @($routing.workers)) {
    foreach ($field in @("worker_id", "label", "lane", "allowed_paths", "blocked_paths", "dry_run_task", "report_path", "validation_commands", "stop_condition")) {
      if (-not ($worker.PSObject.Properties.Name -contains $field)) {
        Add-Failure "Worker route missing field: $field"
      }
    }
    if ([string]::IsNullOrWhiteSpace([string]$worker.dry_run_task)) {
      Add-Failure "Worker #$($worker.worker_id) dry_run_task is blank."
    }
    if (@($worker.validation_commands).Count -eq 0) {
      Add-Failure "Worker #$($worker.worker_id) missing validation_commands."
    }
    if ($worker.stop_condition -notmatch "No APPLY" -or $worker.stop_condition -notmatch "no commit" -or $worker.stop_condition -notmatch "no push") {
      Add-Failure "Worker #$($worker.worker_id) stop condition must block APPLY, commit, and push."
    }
  }
  $worker8 = @($routing.workers | Where-Object { $_.worker_id -eq 8 }) | Select-Object -First 1
  if (-not $worker8) {
    Add-Failure "Routing packet missing worker 8."
  } elseif ($worker8.mode -ne "DRY_RUN_ONLY_REVIEW_ONLY" -or $worker8.dry_run_task -notmatch "Review") {
    Add-Failure "Worker 8 must remain review-only."
  }
}

if ($registry) {
  if (@($registry.workers).Count -ne 8) {
    Add-Failure "Legacy compatibility registry must still contain 8 workers."
  }
  if (-not $registry.codex_launch) {
    Add-Failure "Legacy compatibility registry must still expose codex_launch configuration."
  }
}

$orchestratorText = Get-Content -LiteralPath (Join-Path $RepoRoot "automation/operator/Invoke-AiOsWorkflowOrchestrator.ps1") -Raw
foreach ($token in @("AIOS_WORKER_ROUTING_PACKET.json", "ConvertTo-WorkerRoutingItem", "validation_commands", "stop_condition")) {
  if (-not $orchestratorText.Contains($token)) {
    Add-Failure "Orchestrator missing routing token: $token"
  }
}

$launcherText = Get-Content -LiteralPath (Join-Path $RepoRoot "automation/operator/Start-AiOsParallelDryRunCrew.ps1") -Raw
foreach ($token in @("AIOS_WORKER_ROUTING_PACKET.json", "routing packet missing; falling back to registry", "AIOS_CODEX_WORKER_PROMPT", "Assigned routing task")) {
  if (-not $launcherText.Contains($token)) {
    Add-Failure "Launcher missing routing token: $token"
  }
}

foreach ($blockedPattern in @("git add .", "git add -A", "git commit", "git push", "OANDA")) {
  if ($orchestratorText.Contains($blockedPattern)) {
    Add-Failure "Orchestrator contains blocked token: $blockedPattern"
  }
}

if ($failures.Count -gt 0) {
  Write-Host ""
  Write-Host "AI_OS WORKER AUTO-ROUTING VALIDATION: FAIL" -ForegroundColor Red
  exit 1
}

Write-Host ""
Write-Host "AI_OS WORKER AUTO-ROUTING VALIDATION: PASS" -ForegroundColor Green
exit 0
