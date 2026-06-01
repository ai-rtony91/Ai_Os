param(
  [string]$RepoRoot = ".",
  [string]$CanonicalRegistryPath = "automation/orchestration/workers/AIOS_WORKER_REGISTRY.json",
  [string]$LegacyOperatorRegistryPath = "automation/operator/AIOS_PARALLEL_WORKER_REGISTRY.json",
  [switch]$OutputJson
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Read-JsonOrNull {
  param(
    [Parameter(Mandatory = $true)][string]$Root,
    [Parameter(Mandatory = $true)][string]$RelativePath
  )

  $fullPath = Join-Path $Root $RelativePath
  if (-not (Test-Path -LiteralPath $fullPath -PathType Leaf)) {
    return $null
  }

  Get-Content -LiteralPath $fullPath -Raw | ConvertFrom-Json
}

function ConvertTo-OperatorRoute {
  param(
    [Parameter(Mandatory = $true)]$Worker,
    [int]$Index
  )

  $workerId = [string]$Worker.worker_id
  $label = if ([string]::IsNullOrWhiteSpace([string]$Worker.window_marker)) { [string]$Worker.type } else { [string]$Worker.window_marker }
  $lane = if ([string]::IsNullOrWhiteSpace([string]$Worker.type)) { $workerId } else { [string]$Worker.type }
  $purpose = if ([string]::IsNullOrWhiteSpace([string]$Worker.purpose)) { "Review assigned AI_OS worker state only." } else { [string]$Worker.purpose }

  [pscustomobject]@{
    worker_id = $workerId
    numeric_id = $Index
    label = $label
    lane = $lane
    allowed_paths = @()
    blocked_paths = @($Worker.blocked_actions)
    mode = "DRY_RUN_ONLY"
    dry_run_task = $purpose
    report_path = "Reports/operator/worker-reports/$workerId.json"
    validation_commands = @(
      "powershell -ExecutionPolicy Bypass -File automation/operator/Test-AiOsParallelWorkerReports.ps1",
      "git diff --check",
      "git status --short --branch"
    )
    stop_condition = "Produce DRY_RUN report only. No APPLY, no commit, no push."
    source = "canonical_runtime_registry"
  }
}

$resolvedRepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path
$canonical = Read-JsonOrNull -Root $resolvedRepoRoot -RelativePath $CanonicalRegistryPath
$legacy = Read-JsonOrNull -Root $resolvedRepoRoot -RelativePath $LegacyOperatorRegistryPath

$runtimeWorkers = if ($canonical -and $canonical.workers) { @($canonical.workers) } else { @() }
$operatorRoutes = @()
$routeIndex = 1
foreach ($worker in $runtimeWorkers) {
  $operatorRoutes += ConvertTo-OperatorRoute -Worker $worker -Index $routeIndex
  $routeIndex += 1
}

$adapter = [pscustomobject]@{
  schema = "AIOS_OPERATOR_REGISTRY_ADAPTER.v1"
  mode = "READ_ONLY"
  source = @{
    canonical_registry_path = $CanonicalRegistryPath
    canonical_registry_found = $null -ne $canonical
    legacy_operator_registry_path = $LegacyOperatorRegistryPath
    legacy_operator_registry_found = $null -ne $legacy
  }
  runtime_workers = $runtimeWorkers
  operator_routes = $operatorRoutes
  legacy_operator_summary = @{
    worker_count = if ($legacy -and $legacy.workers) { @($legacy.workers).Count } else { 0 }
    kept_active = $true
    reason = "Legacy operator/window registry shape is not replaced by canonical runtime registry."
  }
  safety = @{
    writes_files = $false
    launches_workers = $false
    changes_json = $false
    changes_runtime_state = $false
  }
}

if ($OutputJson) {
  $adapter | ConvertTo-Json -Depth 8
  exit 0
}

Write-Host "AI_OS Operator Registry Adapter"
Write-Host "Mode: READ_ONLY"
Write-Host "Canonical registry found: $($adapter.source.canonical_registry_found)"
Write-Host "Runtime workers: $(@($adapter.runtime_workers).Count)"
Write-Host "Operator routes: $(@($adapter.operator_routes).Count)"
Write-Host "Legacy operator registry found: $($adapter.source.legacy_operator_registry_found)"
Write-Host "Safety: no files written, no JSON changed, no workers launched."
