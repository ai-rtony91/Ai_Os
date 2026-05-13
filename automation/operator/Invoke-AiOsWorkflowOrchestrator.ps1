param(
  [string]$WorkerRegistryPath = "automation/operator/AIOS_PARALLEL_WORKER_REGISTRY.json",
  [string]$WorkQueuePath = "apps/dashboard/mock-data/work-intelligence-queue-v1.example.json",
  [string]$ApprovalInboxPath = "apps/dashboard/mock-data/aios-approval-inbox-v1.example.json",
  [string]$ValidatorChainPath = "apps/dashboard/mock-data/aios-validator-chain-v1.example.json",
  [string]$ControlledApplyQueuePath = "automation/operator/AIOS_CONTROLLED_APPLY_QUEUE.example.json",
  [string]$CommitPackagePath = "automation/operator/AIOS_PHASE_27_COMMIT_PACKAGE.example.json",
  [string]$WorkerReportDirectory = "Reports/operator/worker-reports",
  [string]$OutputPath = "Reports/operator/AIOS_OPERATOR_NEXT_ACTION_PACKET.md"
)

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path ".").Path

function Read-JsonOrNull {
  param([string]$RelativePath)
  $fullPath = Join-Path $RepoRoot $RelativePath
  if (-not (Test-Path -LiteralPath $fullPath -PathType Leaf)) {
    return $null
  }
  return Get-Content -LiteralPath $fullPath -Raw | ConvertFrom-Json
}

function Format-ListValue {
  param([object[]]$Values)
  $items = @($Values | Where-Object { -not [string]::IsNullOrWhiteSpace([string]$_) })
  if ($items.Count -eq 0) {
    return "NONE"
  }
  return ($items -join ", ")
}

function Add-Section {
  param(
    [System.Collections.Generic.List[string]]$Lines,
    [string]$Title
  )
  $Lines.Add("") | Out-Null
  $Lines.Add("## $Title") | Out-Null
}

$registry = Read-JsonOrNull -RelativePath $WorkerRegistryPath
$workQueue = Read-JsonOrNull -RelativePath $WorkQueuePath
$approvalInbox = Read-JsonOrNull -RelativePath $ApprovalInboxPath
$validatorChain = Read-JsonOrNull -RelativePath $ValidatorChainPath
$applyQueue = Read-JsonOrNull -RelativePath $ControlledApplyQueuePath
$commitPackage = Read-JsonOrNull -RelativePath $CommitPackagePath

$gitStatusLines = @(git status --short --branch)
$workerReportsPath = Join-Path $RepoRoot $WorkerReportDirectory
$workerReports = @()
if (Test-Path -LiteralPath $workerReportsPath -PathType Container) {
  $workerReports = @(Get-ChildItem -LiteralPath $workerReportsPath -Filter "*.json" -File)
}

$pendingApprovals = @()
if ($approvalInbox) {
  $pendingApprovals = @($approvalInbox.approval_requests | Where-Object { $_.status -ne "APPROVED" -and $_.status -ne "CLOSED" })
}

$blockedReasons = New-Object System.Collections.Generic.List[string]
if ($validatorChain -and $validatorChain.merge_readiness -and $validatorChain.merge_readiness.severity_result -eq "BLOCKED") {
  foreach ($reason in @($validatorChain.merge_readiness.blocked_reasons)) {
    if (-not [string]::IsNullOrWhiteSpace([string]$reason)) {
      $blockedReasons.Add("Validator chain: $reason") | Out-Null
    }
  }
}
foreach ($request in $pendingApprovals) {
  if ($request.status -eq "BLOCKED") {
    $blockedReasons.Add("Approval inbox: $($request.request_id) is BLOCKED") | Out-Null
  }
}
if ($gitStatusLines.Count -gt 1) {
  $blockedReasons.Add("Git working tree has uncommitted changes") | Out-Null
}
if ($workerReports.Count -eq 0) {
  $blockedReasons.Add("No collected worker DRY_RUN reports found") | Out-Null
}

$filesReadyForApply = @()
if ($applyQueue) {
  foreach ($worker in @($applyQueue.approved_workers)) {
    foreach ($file in @($worker.files_approved)) {
      if (-not [string]::IsNullOrWhiteSpace([string]$file)) {
        $filesReadyForApply += $file
      }
    }
  }
}

$filesReadyForCommit = @()
if ($commitPackage) {
  $filesReadyForCommit = @($commitPackage.files_approved)
}

$nextSafeAction = "Review this packet. If APPLY is needed, request operator approval for the exact file list first."
if ($blockedReasons.Count -gt 0) {
  $nextSafeAction = "Resolve blocked reasons before APPLY, commit, or push."
} elseif ($pendingApprovals.Count -gt 0) {
  $nextSafeAction = "Review pending approval inbox items before APPLY."
} elseif ($filesReadyForApply.Count -gt 0) {
  $nextSafeAction = "Request operator approval for one serial APPLY item."
} elseif ($filesReadyForCommit.Count -gt 0) {
  $nextSafeAction = "Review validation evidence and exact commit package paths before staging."
}

$lines = New-Object System.Collections.Generic.List[string]
$lines.Add("# AI_OS Operator Next Action Packet") | Out-Null
$lines.Add("") | Out-Null
$lines.Add("Mode: DRY_RUN / operator-approved only") | Out-Null
$lines.Add("Generated: $(Get-Date -Format s)") | Out-Null
$lines.Add("Repo: $RepoRoot") | Out-Null
$lines.Add("Autonomous APPLY: BLOCKED") | Out-Null
$lines.Add("Autonomous commit: BLOCKED") | Out-Null
$lines.Add("Autonomous push: BLOCKED") | Out-Null
$lines.Add("Trading execution: BLOCKED") | Out-Null

Add-Section -Lines $lines -Title "Current Repo Status"
foreach ($line in $gitStatusLines) {
  $lines.Add("- $line") | Out-Null
}

Add-Section -Lines $lines -Title "Active Worker Lanes"
if ($registry) {
  foreach ($worker in @($registry.workers)) {
    $allowed = Format-ListValue -Values @($worker.allowed_paths)
    $blocked = Format-ListValue -Values @($worker.blocked_paths)
    $lines.Add("- Worker #$($worker.id) $($worker.label): lane=$($worker.lane); mode=$($worker.mode); allowed=$allowed; blocked=$blocked") | Out-Null
  }
} else {
  $lines.Add("- Worker registry missing: $WorkerRegistryPath") | Out-Null
}

Add-Section -Lines $lines -Title "Work Queue"
if ($workQueue) {
  foreach ($item in @($workQueue.queue_items)) {
    $lines.Add("- #$($item.queue_rank) [$($item.status)] $($item.title) -> $($item.recommended_action)") | Out-Null
  }
} else {
  $lines.Add("- Work queue missing: $WorkQueuePath") | Out-Null
}

Add-Section -Lines $lines -Title "DRY_RUN Report Collection"
$lines.Add("- Worker report directory: $WorkerReportDirectory") | Out-Null
$lines.Add("- Worker report count: $($workerReports.Count)") | Out-Null
foreach ($report in $workerReports) {
  $lines.Add("- $($report.Name)") | Out-Null
}

Add-Section -Lines $lines -Title "Pending Approvals"
if ($pendingApprovals.Count -gt 0) {
  foreach ($request in $pendingApprovals) {
    $lines.Add("- [$($request.status)] $($request.request_id): $($request.next_safe_action)") | Out-Null
  }
} else {
  $lines.Add("- NONE") | Out-Null
}

Add-Section -Lines $lines -Title "Validation Status"
if ($validatorChain) {
  foreach ($validator in @($validatorChain.validator_chain)) {
    $lines.Add("- [$($validator.state)] $($validator.validator_id): $($validator.label); required=$($validator.required)") | Out-Null
  }
  if ($validatorChain.merge_readiness) {
    $lines.Add("- Merge readiness: $($validatorChain.merge_readiness.state) / $($validatorChain.merge_readiness.severity_result)") | Out-Null
  }
} else {
  $lines.Add("- Validator chain missing: $ValidatorChainPath") | Out-Null
}

Add-Section -Lines $lines -Title "Controlled APPLY Lane"
if ($applyQueue) {
  $lines.Add("- Apply mode: $($applyQueue.apply_mode)") | Out-Null
  $lines.Add("- Approved worker count: $(@($applyQueue.approved_workers).Count)") | Out-Null
  $lines.Add("- git add dot allowed: $($applyQueue.git_policy.git_add_dot_allowed)") | Out-Null
} else {
  $lines.Add("- Controlled APPLY queue missing: $ControlledApplyQueuePath") | Out-Null
}

Add-Section -Lines $lines -Title "Commit Package"
if ($commitPackage) {
  $lines.Add("- Package: $($commitPackage.package_id)") | Out-Null
  $lines.Add("- Approval required: $($commitPackage.approval_required)") | Out-Null
  $lines.Add("- Draft commit message: $($commitPackage.commit_message_draft)") | Out-Null
} else {
  $lines.Add("- Commit package missing: $CommitPackagePath") | Out-Null
}

Add-Section -Lines $lines -Title "Blocked Reasons"
if ($blockedReasons.Count -gt 0) {
  foreach ($reason in $blockedReasons) {
    $lines.Add("- $reason") | Out-Null
  }
} else {
  $lines.Add("- NONE") | Out-Null
}

Add-Section -Lines $lines -Title "Exact Files Ready For APPLY"
if ($filesReadyForApply.Count -gt 0) {
  foreach ($file in $filesReadyForApply) {
    $lines.Add("- $file") | Out-Null
  }
} else {
  $lines.Add("- NONE") | Out-Null
}

Add-Section -Lines $lines -Title "Exact Files Ready For Commit"
if ($filesReadyForCommit.Count -gt 0) {
  foreach ($file in $filesReadyForCommit) {
    $lines.Add("- $file") | Out-Null
  }
} else {
  $lines.Add("- NONE") | Out-Null
}

Add-Section -Lines $lines -Title "Next Safe Action"
$lines.Add($nextSafeAction) | Out-Null

Add-Section -Lines $lines -Title "Safety Boundary"
$lines.Add("- Do not APPLY without explicit operator approval.") | Out-Null
$lines.Add("- Do not commit without explicit operator approval.") | Out-Null
$lines.Add("- Do not push without explicit operator approval.") | Out-Null
$lines.Add("- Do not use git add dot.") | Out-Null
$lines.Add("- Do not connect brokers, use API keys, store secrets, or enable live trading.") | Out-Null

$outputFullPath = Join-Path $RepoRoot $OutputPath
$outputDirectory = Split-Path -Parent $outputFullPath
if (-not (Test-Path -LiteralPath $outputDirectory -PathType Container)) {
  New-Item -ItemType Directory -Force -Path $outputDirectory | Out-Null
}
$lines | Set-Content -LiteralPath $outputFullPath -Encoding UTF8

Write-Host "AI_OS Workflow Orchestrator" -ForegroundColor Cyan
Write-Host "Mode: DRY_RUN / operator-approved only"
Write-Host "Packet written: $OutputPath"
Write-Host "Worker lanes: $(if ($registry) { @($registry.workers).Count } else { 0 })"
Write-Host "Pending approvals: $($pendingApprovals.Count)"
Write-Host "Worker reports: $($workerReports.Count)"
Write-Host "Blocked reasons: $($blockedReasons.Count)"
Write-Host "Next safe action: $nextSafeAction"
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
