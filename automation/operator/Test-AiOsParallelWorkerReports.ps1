param(
  [string]$RegistryPath = "automation/operator/AIOS_PARALLEL_WORKER_REGISTRY.json",
  [string]$QueuePath = "automation/operator/AIOS_CONTROLLED_APPLY_QUEUE.example.json",
  [string]$WorkerReportDirectory = "Reports/operator/worker-reports"
)

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path ".").Path
$RegistryFullPath = Join-Path $RepoRoot $RegistryPath
$QueueFullPath = Join-Path $RepoRoot $QueuePath
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

if (-not (Test-Path -LiteralPath $RegistryFullPath)) {
  Add-Failure "Missing registry: $RegistryPath"
} else {
  $registry = Get-Content -LiteralPath $RegistryFullPath -Raw | ConvertFrom-Json
  if (@($registry.workers).Count -ne 8) {
    Add-Failure "Registry must define exactly 8 workers."
  }
  if ($registry.codex_command -ne "UNKNOWN") {
    Add-Failure "Registry codex_command must remain UNKNOWN until approved."
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
      if (Test-RelativePathProtected -Path $path -ProtectedFiles $registry.protected_files) {
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
