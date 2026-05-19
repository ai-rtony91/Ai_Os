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

Write-Host "AI_OS Worker Auto-Routing DRY_RUN Validator" -ForegroundColor Cyan
Write-Host "Repo: $RepoRoot"

$requiredFiles = @(
  "automation/operator/Invoke-AiOsWorkflowOrchestrator.ps1",
  "automation/operator/Start-AiOsParallelDryRunCrew.ps1",
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
$routing = Read-Json -RelativePath $RoutingPacketPath
$fixture = Read-Json -RelativePath "apps/dashboard/mock-data/aios-worker-auto-routing-v1.example.json"

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

if ($registry -and @($registry.workers).Count -ne 8) {
  Add-Failure "Registry must still contain 8 workers."
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
