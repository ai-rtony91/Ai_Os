param(
  [string]$RegistryPath = "automation/operator/AIOS_PARALLEL_WORKER_REGISTRY.json",
  [string]$QueuePath = "automation/operator/AIOS_CONTROLLED_APPLY_QUEUE.example.json",
  [string]$AdapterPath = "automation/operator/Get-AiOsOperatorRegistryAdapter.DRY_RUN.ps1",
  [string]$WorkerReportDirectory = "Reports/operator/worker-reports"
)

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path ".").Path
$RegistryFullPath = Join-Path $RepoRoot $RegistryPath
$QueueFullPath = Join-Path $RepoRoot $QueuePath
$AdapterFullPath = Join-Path $RepoRoot $AdapterPath
$ReportDirFullPath = Join-Path $RepoRoot $WorkerReportDirectory
$failures = New-Object System.Collections.Generic.List[string]

function Add-Failure {
  param([string]$Message)
  $script:failures.Add($Message) | Out-Null
  Write-Host "FAIL: $Message" -ForegroundColor Red
}

function Test-RelativePathProtected {
  param([string]$Path, [string[]]$ProtectedFiles)
  $normalized = ($Path -replace "\\", "/").TrimStart("/")
  foreach ($protected in $ProtectedFiles) {
    if ($normalized -ieq ($protected -replace "\\", "/")) {
      return $true
    }
  }
  return $false
}

Write-Host "AI_OS Parallel Worker Report Validator" -ForegroundColor Cyan
Write-Host "Repo: $RepoRoot"

if (-not (Test-Path -LiteralPath $AdapterFullPath -PathType Leaf)) {
  Add-Failure "Missing operator registry adapter: $AdapterPath"
} else {
  try {
    $adapter = & powershell -NoProfile -ExecutionPolicy Bypass -File $AdapterFullPath -RepoRoot $RepoRoot -OutputJson | ConvertFrom-Json
    if ($adapter.schema -ne "AIOS_OPERATOR_REGISTRY_ADAPTER.v1") {
      Add-Failure "Operator registry adapter schema mismatch."
    }
    if ($adapter.mode -ne "READ_ONLY") {
      Add-Failure "Operator registry adapter must be READ_ONLY."
    }
    if (@($adapter.runtime_workers).Count -eq 0) {
      Add-Failure "Operator registry adapter must expose runtime_workers."
    }
    if (@($adapter.operator_routes).Count -ne @($adapter.runtime_workers).Count) {
      Add-Failure "Operator registry adapter route count must match runtime worker count."
    }
    foreach ($route in @($adapter.operator_routes)) {
      foreach ($field in @("worker_id", "numeric_id", "label", "lane", "blocked_paths", "dry_run_task", "report_path", "validation_commands", "stop_condition", "source")) {
        if (-not ($route.PSObject.Properties.Name -contains $field)) {
          Add-Failure "Adapter operator route missing field: $field"
        }
      }
      if ($route.source -ne "canonical_runtime_registry") {
        Add-Failure "Adapter operator route must identify canonical runtime registry source."
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
  } catch {
    Add-Failure "Operator registry adapter failed: $($_.Exception.Message)"
  }
}

$registry = $null
if (-not (Test-Path -LiteralPath $RegistryFullPath)) {
  Add-Failure "Missing legacy compatibility registry: $RegistryPath"
} else {
  $registry = Get-Content -LiteralPath $RegistryFullPath -Raw | ConvertFrom-Json
  if (@($registry.workers).Count -ne 8) {
    Add-Failure "Legacy compatibility registry must define exactly 8 workers."
  }
  if (-not $registry.codex_launch) {
    Add-Failure "Legacy compatibility registry missing codex_launch configuration."
  } else {
    if ($registry.codex_launch.enabled -eq $false -and $registry.codex_launch.command -ne "UNKNOWN") {
      Add-Failure "Disabled codex_launch must keep command UNKNOWN by default."
    }
    if ($registry.codex_launch.fallback_to_instruction_window -ne $true) {
      Add-Failure "codex_launch must keep fallback_to_instruction_window enabled."
    }
    if (-not $registry.codex_launch.arguments) {
      Write-Host "INFO: codex_launch arguments are empty."
    }
  }
}

if (-not (Test-Path -LiteralPath $QueueFullPath)) {
  Add-Failure "Missing queue example: $QueuePath"
} else {
  $queue = Get-Content -LiteralPath $QueueFullPath -Raw | ConvertFrom-Json
  if (-not $queue.validation_commands -or @($queue.validation_commands).Count -eq 0) {
    Add-Failure "Queue must include validation_commands."
  }
  if ($queue.git_policy.git_add_dot_allowed -ne $false) {
    Add-Failure "Queue must forbid git add dot."
  }
}

if ($failures.Count -eq 0 -and (Test-Path -LiteralPath $ReportDirFullPath)) {
  $reports = @(Get-ChildItem -LiteralPath $ReportDirFullPath -Filter "*.json" -File)
  $fileOwners = @{}

  foreach ($reportFile in $reports) {
    Write-Host "Checking worker report: $($reportFile.Name)"
    $report = Get-Content -LiteralPath $reportFile.FullName -Raw | ConvertFrom-Json

    if (-not $report.validation_commands -or @($report.validation_commands).Count -eq 0) {
      Add-Failure "$($reportFile.Name) missing validation_commands."
    }

    foreach ($deleted in @($report.files_deleted)) {
      if ($deleted) {
        Add-Failure "$($reportFile.Name) reports deleted file: $deleted"
      }
    }

    foreach ($path in @($report.files_planned)) {
      if (-not $path) { continue }
      if ($registry -and (Test-RelativePathProtected -Path $path -ProtectedFiles $registry.protected_files)) {
        Add-Failure "$($reportFile.Name) touches protected file: $path"
      }
      $key = ($path -replace "\\", "/").ToLowerInvariant()
      if ($fileOwners.ContainsKey($key)) {
        Add-Failure "Overlapping planned file: $path owned by $($fileOwners[$key]) and $($reportFile.Name)"
      } else {
        $fileOwners[$key] = $reportFile.Name
      }
    }
  }
} elseif ($failures.Count -eq 0) {
  Write-Host "No worker report directory found. Registry and queue validation only."
}

if ($failures.Count -gt 0) {
  Write-Host ""
  Write-Host "AI_OS PARALLEL WORKER REPORT VALIDATION: FAIL" -ForegroundColor Red
  exit 1
}

Write-Host ""
Write-Host "AI_OS PARALLEL WORKER REPORT VALIDATION: PASS" -ForegroundColor Green
exit 0
