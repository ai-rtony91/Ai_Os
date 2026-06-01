param(
  [string]$ConfigPath = "automation/work_intelligence/AIOS_WORK_INTELLIGENCE_CONFIG.json"
)

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path ".").Path
$failures = New-Object System.Collections.Generic.List[string]

function Add-Failure {
  param([string]$Message)
  $script:failures.Add($Message) | Out-Null
  Write-Host "FAIL: $Message" -ForegroundColor Red
}

Write-Host "AI_OS Work Intelligence Validator" -ForegroundColor Cyan
Write-Host "Repo: $RepoRoot"

$requiredFiles = @(
  "automation/work_intelligence/Invoke-AiOsWorkIntelligenceScan.ps1",
  "automation/work_intelligence/Test-AiOsWorkIntelligenceScan.ps1",
  "automation/work_intelligence/AIOS_WORK_INTELLIGENCE_CONFIG.json",
  "Reports/work_intelligence/.gitkeep",
  "Reports/work_intelligence/MASTER_TODO_LEDGER.example.json",
  "Reports/work_intelligence/DAILY_WORK_INTELLIGENCE_SNAPSHOT.example.json",
  "Reports/work_intelligence/WORKER_QUEUE_STATUS.example.json",
  "Reports/work_intelligence/REPO_HEALTH_SUMMARY.example.json",
  "Reports/work_intelligence/daily/.gitkeep",
  "Reports/work_intelligence/telemetry/.gitkeep",
  "Reports/work_intelligence/queue/.gitkeep",
  "Reports/work_intelligence/daily/DAILY_WORK_INTELLIGENCE_SNAPSHOT.example.json",
  "Reports/work_intelligence/telemetry/WORK_INTELLIGENCE_METRICS.example.csv",
  "Reports/work_intelligence/MASTER_OPERATOR_BRIEFING.example.md",
  "Reports/work_intelligence/briefings/.gitkeep",
  "Reports/work_intelligence/briefings/OPERATOR_VOICE_BRIEFING.example.md",
  "Reports/operator/worker-reports/.gitkeep",
  "docs/AI_OS/work_intelligence/AIOS_WORK_INTELLIGENCE_ARCHITECTURE.md",
  "docs/AI_OS/work_intelligence/AIOS_AUTONOMOUS_SNAPSHOT_WORKFLOW.md"
)

$requiredFolders = @(
  "automation/work_intelligence",
  "Reports/work_intelligence",
  "Reports/work_intelligence/daily",
  "Reports/work_intelligence/telemetry",
  "Reports/work_intelligence/queue",
  "Reports/work_intelligence/briefings",
  "Reports/operator/worker-reports",
  "docs/AI_OS/work_intelligence"
)

foreach ($folder in $requiredFolders) {
  if (-not (Test-Path -LiteralPath (Join-Path $RepoRoot $folder))) {
    Add-Failure "Missing required folder: $folder"
  }
}

foreach ($file in $requiredFiles) {
  if (-not (Test-Path -LiteralPath (Join-Path $RepoRoot $file))) {
    Add-Failure "Missing required file: $file"
  }
}

$jsonFiles = @(
  "automation/work_intelligence/AIOS_WORK_INTELLIGENCE_CONFIG.json",
  "Reports/work_intelligence/MASTER_TODO_LEDGER.example.json",
  "Reports/work_intelligence/DAILY_WORK_INTELLIGENCE_SNAPSHOT.example.json",
  "Reports/work_intelligence/daily/DAILY_WORK_INTELLIGENCE_SNAPSHOT.example.json",
  "Reports/work_intelligence/WORKER_QUEUE_STATUS.example.json",
  "Reports/work_intelligence/REPO_HEALTH_SUMMARY.example.json"
)

foreach ($jsonFile in $jsonFiles) {
  $full = Join-Path $RepoRoot $jsonFile
  if (Test-Path -LiteralPath $full) {
    try {
      Get-Content -LiteralPath $full -Raw | ConvertFrom-Json | Out-Null
    } catch {
      Add-Failure "JSON parse failed: $jsonFile :: $($_.Exception.Message)"
    }
  }
}

$forbiddenPhase161Paths = @(
  "automation/operator",
  "docs/AI_OS/operator",
  "README.md",
  "AGENTS.md",
  "RISK_POLICY.md",
  "SOURCE_LOG.md",
  "ERROR_LOG.md",
  "HALLUCINATION_LOG.md",
  "AAR.md",
  "DAILY_REPORT.md",
  "White_Paper.md"
)

$phase161AllowedPrefixes = @(
  "automation/work_intelligence/",
  "Reports/work_intelligence/",
  "docs/AI_OS/work_intelligence/"
)

$statusLines = @(git status --short)
foreach ($line in $statusLines) {
  if (-not $line) { continue }
  $path = $line.Substring(3).Trim() -replace "\\", "/"
  $isPhase161 = $false
  foreach ($prefix in $phase161AllowedPrefixes) {
    if ($path.StartsWith($prefix)) {
      $isPhase161 = $true
    }
  }
  if ($isPhase161) {
    foreach ($forbidden in $forbiddenPhase161Paths) {
      if ($path -eq $forbidden -or $path.StartsWith(($forbidden -replace "\\", "/") + "/")) {
        Add-Failure "Phase 16.1 touched forbidden path: $path"
      }
    }
  }
}

$configFullPath = Join-Path $RepoRoot $ConfigPath
if (Test-Path -LiteralPath $configFullPath) {
  $config = Get-Content -LiteralPath $configFullPath -Raw | ConvertFrom-Json
  if ($config.mode -ne "READ_ONLY") {
    Add-Failure "Config mode must be READ_ONLY."
  }
  if ($config.scanner.writes_files -ne $false) {
    Add-Failure "Scanner config must declare writes_files false."
  }
  if ($config.scanner.destructive_actions_allowed -ne $false) {
    Add-Failure "Scanner config must declare destructive_actions_allowed false."
  }
  if ($config.scanner.save_to_reports_enabled -ne $false) {
    Add-Failure "save_to_reports_enabled must be false by default."
  }
  if ($config.scanner.manual_save_snapshot_flag -ne "-SaveSnapshot") {
    Add-Failure "manual_save_snapshot_flag must be -SaveSnapshot."
  }
  if ($config.scanner.telemetry_append_enabled -ne $false) {
    Add-Failure "telemetry_append_enabled must be false by default."
  }
  if ($config.scanner.operator_briefing_enabled -ne $false) {
    Add-Failure "operator_briefing_enabled must be false by default."
  }
  foreach ($pathProperty in @("snapshot_output_directory", "telemetry_output_path", "operator_briefing_output_path")) {
    if (-not $config.$pathProperty) {
      Add-Failure "Config missing $pathProperty."
    }
  }
}

$metricsExample = Join-Path $RepoRoot "Reports/work_intelligence/telemetry/WORK_INTELLIGENCE_METRICS.example.csv"
if (Test-Path -LiteralPath $metricsExample) {
  $expectedHeader = "timestamp,branch,total_files,total_reports,total_json_files,total_markdown_files,total_scripts,worker_lane_count,unresolved_todos,unresolved_fixmes,clean_git_status"
  $actualHeader = (Get-Content -LiteralPath $metricsExample -First 1)
  if ($actualHeader -ne $expectedHeader) {
    Add-Failure "Telemetry CSV header mismatch."
  }
}

$scannerPath = Join-Path $RepoRoot "automation/work_intelligence/Invoke-AiOsWorkIntelligenceScan.ps1"
if (Test-Path -LiteralPath $scannerPath) {
  $scannerText = Get-Content -LiteralPath $scannerPath -Raw
  if (-not $scannerText.Contains('[switch]$GenerateBriefing')) {
    Add-Failure "Scanner missing GenerateBriefing switch."
  }
  if (-not $scannerText.Contains('[switch]$SaveQueueHistory')) {
    Add-Failure "Scanner missing SaveQueueHistory switch."
  }
  foreach ($queueHistoryToken in @("Save-QueueHistory", "Reports/work_intelligence/queue", "WORK_QUEUE_SNAPSHOT_", "LATEST_WORK_QUEUE.json", "queue_count")) {
    if (-not $scannerText.Contains($queueHistoryToken)) {
      Add-Failure "Scanner missing queue history token: $queueHistoryToken"
    }
  }
  foreach ($requiredField in @("current_focus_area", "active_subsystem", "recommended_next_workload", "focus_evidence_sources", "security_warnings")) {
    if (-not $scannerText.Contains($requiredField)) {
      Add-Failure "Scanner missing required field: $requiredField"
    }
  }
  foreach ($requiredField in @("security_warning_count", "high_risk_count", "medium_risk_count", "low_risk_count", "info_count", "suppressed_policy_mentions")) {
    if (-not $scannerText.Contains($requiredField)) {
      Add-Failure "Scanner missing security summary field: $requiredField"
    }
  }
  foreach ($requiredField in @("priority_score", "urgency_score", "dependency_blocked", "safe_to_apply", "recommended_operator_action", "stale_work_detected", "stale_work_items", "unfinished_phase_count", "unfinished_stage_count", "blocked_work_count", "active_priority_lane")) {
    if (-not $scannerText.Contains($requiredField)) {
      Add-Failure "Scanner missing priority field: $requiredField"
    }
  }
  foreach ($requiredField in @("worker_report_evidence", "worker_report_issues", "worker_report_issue_count", "valid_worker_report_count", "invalid_worker_report_count", "worker_conflict_count", "worker_conflicts")) {
    if (-not $scannerText.Contains($requiredField)) {
      Add-Failure "Scanner missing worker report ingestion field: $requiredField"
    }
  }
  foreach ($conflictField in @("conflict_id", "file_path", "workers", "severity", "status", "recommended_action")) {
    if (-not $scannerText.Contains($conflictField)) {
      Add-Failure "Scanner missing worker conflict field: $conflictField"
    }
  }
  foreach ($conflictToken in @("WI-WORKER-FILE-CONFLICT", "Resolve worker file ownership conflict.", "worker_conflicts")) {
    if (-not $scannerText.Contains($conflictToken)) {
      Add-Failure "Scanner missing worker conflict queue token: $conflictToken"
    }
  }
  foreach ($requiredToken in @("Get-WorkerReportEvidence", "invalid_worker_report_json", "worker_report_missing_required_fields", "worker_report_files_deleted_present", "worker_report_missing_validation_commands", "worker_report_overlapping_planned_files", "worker_report_protected_file_path", "evidence_only", "approval_granted")) {
    if (-not $scannerText.Contains($requiredToken)) {
      Add-Failure "Scanner missing worker report ingestion token: $requiredToken"
    }
  }
  foreach ($adapterToken in @("Get-OperatorRegistryAdapterResult", "operator_registry_adapter", "legacy_compatibility_fallback", "compatibility_evidence_only", "legacy_registry_primary_source")) {
    if (-not $scannerText.Contains($adapterToken)) {
      Add-Failure "Scanner missing adapter-first registry token: $adapterToken"
    }
  }
  if (-not $scannerText.Contains("work_queue")) {
    Add-Failure "Scanner missing work_queue field."
  }
  foreach ($queueField in @("queue_rank", "task_id", "title", "source", "priority", "status", "recommended_action", "suggested_worker_lane", "evidence_strength", "route_reason")) {
    if (-not $scannerText.Contains($queueField)) {
      Add-Failure "Scanner missing work queue item field: $queueField"
    }
  }
  foreach ($queueStatus in @("REVIEW", "BLOCKED", "READY_FOR_DRY_RUN", "UNKNOWN")) {
    if (-not $scannerText.Contains($queueStatus)) {
      Add-Failure "Scanner missing work queue status: $queueStatus"
    }
  }
  foreach ($workerLane in @("Dashboard UI", "Trading Lab", "Operator Orchestration", "Work Intelligence", "Validators", "Reports", "Mock Data", "UNKNOWN")) {
    if (-not $scannerText.Contains($workerLane)) {
      Add-Failure "Scanner missing suggested worker lane: $workerLane"
    }
  }
  foreach ($sortToken in @("Get-QueuePriorityWeight", "Get-QueueStatusWeight", "Get-QueueSourceWeight", "ConvertTo-RankedWorkQueue")) {
    if (-not $scannerText.Contains($sortToken)) {
      Add-Failure "Scanner missing queue sorting logic: $sortToken"
    }
  }
  if ($scannerText.Contains("Start-AiOsControlledApplyLane")) {
    Add-Failure "Scanner must not contain auto-APPLY lane launch logic."
  }
  foreach ($blockedToken in @("git commit", "git push", "git add .", "Start-AiOsParallelDryRunCrew")) {
    if ($scannerText.Contains($blockedToken)) {
      Add-Failure "Scanner must not contain blocked automation token: $blockedToken"
    }
  }
  foreach ($severity in @("HIGH", "MEDIUM", "LOW", "INFO")) {
    if (-not $scannerText.Contains($severity)) {
      Add-Failure "Scanner missing severity level: $severity"
    }
  }
  foreach ($category in @("secret_material", "secret_wording_review", "execution_boundary_review", "git_safety", "destructive_command", "protected_file_status", "policy_mention")) {
    if (-not $scannerText.Contains($category)) {
      Add-Failure "Scanner missing security warning category: $category"
    }
  }
  foreach ($allowedFocus in @("Work Intelligence", "Operator Orchestration", "Trading Lab", "Dashboard UI", "UNKNOWN")) {
    if (-not $scannerText.Contains($allowedFocus)) {
      Add-Failure "Scanner missing allowed focus fallback/value: $allowedFocus"
    }
  }
  foreach ($warningProperty in @("warning_type", "severity", "category", "path =")) {
    if (-not $scannerText.Contains($warningProperty)) {
      Add-Failure "Security warnings must include $warningProperty."
    }
  }
  if ($scannerText -notmatch "suppressedPolicyMentions") {
    Add-Failure "Scanner missing policy-only warning suppression counter."
  }
}

try {
  $scanJson = powershell -ExecutionPolicy Bypass -File automation/work_intelligence/Invoke-AiOsWorkIntelligenceScan.ps1
  $scan = $scanJson | ConvertFrom-Json
  foreach ($requiredField in @("security_warning_count", "high_risk_count", "medium_risk_count", "low_risk_count", "info_count", "suppressed_policy_mentions")) {
    if (-not ($scan.PSObject.Properties.Name -contains $requiredField)) {
      Add-Failure "Scan output missing security summary field: $requiredField"
    }
  }
  foreach ($requiredField in @("priority_score", "urgency_score", "dependency_blocked", "safe_to_apply", "recommended_operator_action", "stale_work_detected", "stale_work_items", "unfinished_phase_count", "unfinished_stage_count", "blocked_work_count", "active_priority_lane")) {
    if (-not ($scan.PSObject.Properties.Name -contains $requiredField)) {
      Add-Failure "Scan output missing priority field: $requiredField"
    }
  }
  foreach ($requiredField in @("worker_report_evidence", "worker_report_issues", "worker_report_issue_count", "valid_worker_report_count", "invalid_worker_report_count", "worker_conflict_count", "worker_conflicts")) {
    if (-not ($scan.PSObject.Properties.Name -contains $requiredField)) {
      Add-Failure "Scan output missing worker report ingestion field: $requiredField"
    }
  }
  foreach ($requiredField in @("worker_registry_source", "operator_registry_adapter_path", "legacy_worker_registry_path", "legacy_registry_role", "legacy_registry_primary_source")) {
    if (-not ($scan.PSObject.Properties.Name -contains $requiredField)) {
      Add-Failure "Scan output missing adapter-first registry field: $requiredField"
    }
  }
  if ($scan.worker_registry_source -ne "operator_registry_adapter") {
    Add-Failure "Work intelligence scan must prefer operator registry adapter."
  }
  if ($scan.legacy_registry_role -ne "compatibility_evidence_only") {
    Add-Failure "Legacy registry must be compatibility evidence only in work intelligence scan output."
  }
  if ($scan.legacy_registry_primary_source -ne $false) {
    Add-Failure "Legacy registry must not be marked as primary source."
  }
  if ($scan.worker_conflict_count -ne @($scan.worker_conflicts).Count) {
    Add-Failure "worker_conflict_count does not match worker_conflicts length."
  }
  foreach ($conflict in @($scan.worker_conflicts)) {
    foreach ($requiredConflictField in @("conflict_id", "file_path", "workers", "severity", "status", "recommended_action")) {
      if (-not ($conflict.PSObject.Properties.Name -contains $requiredConflictField)) {
        Add-Failure "Worker conflict missing field: $requiredConflictField"
      }
    }
    if ($conflict.status -ne "BLOCKED") {
      Add-Failure "Worker conflict status must be BLOCKED."
    }
  }
  if ($scan.worker_conflict_count -gt 0) {
    $conflictQueueItems = @($scan.work_queue | Where-Object { $_.task_id -eq "WI-WORKER-FILE-CONFLICT" })
    if (@($conflictQueueItems).Count -eq 0) {
      Add-Failure "Worker conflicts must produce WI-WORKER-FILE-CONFLICT queue item."
    }
  }
  if ($null -eq $scan.safe_to_apply) {
    Add-Failure "Scan output safe_to_apply must not be null."
  }
  if ($scan.worker_report_count -eq 0) {
    $missingQueueItems = @($scan.work_queue | Where-Object { $_.task_id -eq "WI-WORKER-REPORTS-MISSING" })
    if (@($missingQueueItems).Count -eq 0) {
      Add-Failure "Missing or empty worker report folder must produce WI-WORKER-REPORTS-MISSING queue item."
    }
    foreach ($missingQueueItem in $missingQueueItems) {
      if ($missingQueueItem.status -notin @("REVIEW", "BLOCKED")) {
        Add-Failure "Worker report missing queue item must be REVIEW or BLOCKED."
      }
    }
  }
  foreach ($issue in @($scan.worker_report_issues)) {
    foreach ($requiredIssueField in @("issue_type", "status", "path", "detail")) {
      if (-not ($issue.PSObject.Properties.Name -contains $requiredIssueField)) {
        Add-Failure "Worker report issue missing field: $requiredIssueField"
      }
    }
    if (@("REVIEW", "BLOCKED") -notcontains $issue.status) {
      Add-Failure "Worker report issue has invalid status: $($issue.status)"
    }
  }
  foreach ($workerReport in @($scan.worker_report_evidence)) {
    foreach ($requiredReportField in @("worker_id", "label", "mode", "source_path", "files_planned", "files_deleted", "validation_commands", "summary", "evidence_only", "approval_granted")) {
      if (-not ($workerReport.PSObject.Properties.Name -contains $requiredReportField)) {
        Add-Failure "Worker report evidence missing field: $requiredReportField"
      }
    }
    if ($workerReport.evidence_only -ne $true -or $workerReport.approval_granted -ne $false) {
      Add-Failure "Worker report evidence must remain evidence_only true and approval_granted false."
    }
  }
  if ([string]::IsNullOrWhiteSpace([string]$scan.recommended_operator_action)) {
    Add-Failure "Scan output recommended_operator_action must not be blank."
  }
  if (-not ($scan.PSObject.Properties.Name -contains "work_queue")) {
    Add-Failure "Scan output missing work_queue."
  }
  $expectedRank = 1
  foreach ($queueItem in @($scan.work_queue)) {
    foreach ($requiredQueueField in @("queue_rank", "task_id", "title", "source", "priority", "status", "recommended_action", "suggested_worker_lane", "evidence_strength", "route_reason")) {
      if (-not ($queueItem.PSObject.Properties.Name -contains $requiredQueueField)) {
        Add-Failure "Work queue item missing field: $requiredQueueField"
      }
    }
    if (@("REVIEW", "BLOCKED", "READY_FOR_DRY_RUN", "UNKNOWN") -notcontains $queueItem.status) {
      Add-Failure "Work queue item has invalid status: $($queueItem.status)"
    }
    if (@("Dashboard UI", "Trading Lab", "Operator Orchestration", "Work Intelligence", "Validators", "Reports", "Mock Data", "UNKNOWN") -notcontains $queueItem.suggested_worker_lane) {
      Add-Failure "Work queue item has invalid suggested_worker_lane: $($queueItem.suggested_worker_lane)"
    }
    if ($queueItem.queue_rank -ne $expectedRank) {
      Add-Failure "Work queue item rank is not sequential at task $($queueItem.task_id)."
    }
    $expectedRank += 1
  }
  if ($scan.security_warning_count -ne @($scan.security_warnings).Count) {
    Add-Failure "security_warning_count does not match security_warnings length."
  }
  foreach ($warning in @($scan.security_warnings)) {
    foreach ($requiredWarningField in @("warning_type", "severity", "category", "path")) {
      if (-not ($warning.PSObject.Properties.Name -contains $requiredWarningField)) {
        Add-Failure "Security warning missing field: $requiredWarningField"
      }
    }
    if (@("HIGH", "MEDIUM", "LOW", "INFO") -notcontains $warning.severity) {
      Add-Failure "Security warning has invalid severity: $($warning.severity)"
    }
    if (@("secret_material", "secret_wording_review", "execution_boundary_review", "git_safety", "destructive_command", "protected_file_status", "policy_mention") -notcontains $warning.category) {
      Add-Failure "Security warning has invalid category: $($warning.category)"
    }
  }
} catch {
  Add-Failure "Scanner output validation failed: $($_.Exception.Message)"
}

if ($failures.Count -gt 0) {
  Write-Host ""
  Write-Host "AI_OS WORK INTELLIGENCE VALIDATION: FAIL" -ForegroundColor Red
  exit 1
}

Write-Host ""
Write-Host "AI_OS WORK INTELLIGENCE VALIDATION: PASS" -ForegroundColor Green
exit 0
