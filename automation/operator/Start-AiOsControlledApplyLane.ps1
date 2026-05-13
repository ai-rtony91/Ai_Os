param(
  [string]$QueuePath = "automation/operator/AIOS_CONTROLLED_APPLY_QUEUE.example.json",
  [string]$RegistryPath = "automation/operator/AIOS_PARALLEL_WORKER_REGISTRY.json",
  [string]$FinalReportDirectory = "Reports/operator"
)

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path ".").Path
$QueueFullPath = Join-Path $RepoRoot $QueuePath
$RegistryFullPath = Join-Path $RepoRoot $RegistryPath
$ReportDirFullPath = Join-Path $RepoRoot $FinalReportDirectory

function Ask-OperatorApproval {
  param([string]$Prompt)
  $answer = Read-Host "$Prompt Type YES to continue"
  return $answer -eq "YES"
}

function Invoke-ValidationCommands {
  param([string[]]$Commands)
  foreach ($command in $Commands) {
    Write-Host "VALIDATION: $command" -ForegroundColor Cyan
    Invoke-Expression $command
    if ($LASTEXITCODE -ne 0) {
      throw "Validation failed: $command"
    }
  }
}

if (-not (Test-Path -LiteralPath $QueueFullPath)) {
  throw "Apply queue not found: $QueueFullPath"
}
if (-not (Test-Path -LiteralPath $RegistryFullPath)) {
  throw "Worker registry not found: $RegistryFullPath"
}

New-Item -ItemType Directory -Force -Path $ReportDirFullPath | Out-Null

$queue = Get-Content -LiteralPath $QueueFullPath -Raw | ConvertFrom-Json
$registry = Get-Content -LiteralPath $RegistryFullPath -Raw | ConvertFrom-Json
$approvedWorkers = @($queue.approved_workers)

Write-Host "AI_OS Controlled APPLY Lane" -ForegroundColor Cyan
Write-Host "Repo: $RepoRoot"
Write-Host "Codex command: UNKNOWN. This lane does not assume or execute Codex automatically."
Write-Host "Approved worker count: $($approvedWorkers.Count)"
Write-Host ""

if ($approvedWorkers.Count -eq 0) {
  Write-Host "No approved workers in queue. Nothing to APPLY."
}

foreach ($workerItem in $approvedWorkers) {
  $workerId = $workerItem.worker_id
  $worker = $registry.workers | Where-Object { $_.id -eq $workerId } | Select-Object -First 1
  if (-not $worker) {
    throw "Queue references unknown worker id: $workerId"
  }

  Write-Host "Next APPLY worker: #$($worker.id) $($worker.label) :: $($worker.lane)" -ForegroundColor Yellow
  if (-not (Ask-OperatorApproval "Approve APPLY for worker #$($worker.id) $($worker.label)?")) {
    throw "Operator stopped before APPLY for worker #$($worker.id)."
  }

  Write-Host "APPLY placeholder approved. Execute the approved worker patch manually in the active Codex session."
  Write-Host "Codex command placeholder remains UNKNOWN."

  if (-not (Ask-OperatorApproval "Confirm worker #$($worker.id) APPLY is complete and ready for validation?")) {
    throw "Operator stopped before validation for worker #$($worker.id)."
  }

  Invoke-ValidationCommands -Commands @($queue.validation_commands)
}

if ($queue.git_policy.ask_before_git_add) {
  if (Ask-OperatorApproval "Queue clean. Approve explicit git add paths now?") {
    Write-Host "Do not use git add ."
    Write-Host "Run explicit git add paths manually after reviewing git status."
  }
}

if ($queue.git_policy.ask_before_git_commit) {
  if (Ask-OperatorApproval "Approve git commit after full batch validation?") {
    Write-Host "Commit command placeholder only. No commit was performed by this script."
  }
}

if ($queue.git_policy.ask_before_git_push) {
  if (Ask-OperatorApproval "Approve one git push after commit?") {
    Write-Host "Push command placeholder only. No push was performed by this script."
  }
}

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$finalReport = Join-Path $ReportDirFullPath "AIOS_CONTROLLED_APPLY_LANE_$timestamp.md"
@(
  "# AI_OS Controlled APPLY Lane Report",
  "",
  "Repo: $RepoRoot",
  "Queue: $QueuePath",
  "Approved workers processed: $($approvedWorkers.Count)",
  "Codex command: UNKNOWN",
  "Commit performed: NO",
  "Push performed: NO"
) | Set-Content -LiteralPath $finalReport -Encoding UTF8

Write-Host "Final report written: $finalReport" -ForegroundColor Green
