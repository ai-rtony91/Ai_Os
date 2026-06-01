param(
  [string]$ConfigPath = "automation/work_intelligence/AIOS_WORK_INTELLIGENCE_CONFIG.json",
  [switch]$SaveSnapshot,
  [switch]$GenerateBriefing,
  [switch]$SaveQueueHistory
)

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path ".").Path
$ConfigFullPath = Join-Path $RepoRoot $ConfigPath

if (-not (Test-Path -LiteralPath $ConfigFullPath)) {
  throw "Config not found: $ConfigFullPath"
}

$config = Get-Content -LiteralPath $ConfigFullPath -Raw | ConvertFrom-Json
if ($config.mode -ne "READ_ONLY") {
  throw "Config mode must be READ_ONLY."
}

function Get-CommandText {
  param([string]$Command)
  $output = Invoke-Expression $Command 2>$null
  if ($null -eq $output) { return "" }
  return ($output | Out-String).Trim()
}

function Count-Files {
  param([string]$Filter)
  return @(Get-ChildItem -LiteralPath $RepoRoot -Recurse -File -Filter $Filter -ErrorAction SilentlyContinue).Count
}

function ConvertTo-SafeFileTimestamp {
  return (Get-Date).ToString("yyyyMMdd_HHmmss")
}

function Save-DailySnapshot {
  param(
    [pscustomobject]$Snapshot,
    [string]$OutputDirectory
  )
  $snapshotDir = Join-Path $RepoRoot $OutputDirectory
  New-Item -ItemType Directory -Force -Path $snapshotDir | Out-Null
  $snapshotPath = Join-Path $snapshotDir ("DAILY_WORK_INTELLIGENCE_SNAPSHOT_{0}.json" -f (ConvertTo-SafeFileTimestamp))
  $Snapshot | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $snapshotPath -Encoding UTF8
  return $snapshotPath
}

function Save-QueueHistory {
  param(
    [pscustomobject]$Snapshot,
    [string]$OutputDirectory = "Reports/work_intelligence/queue"
  )
  $queueDir = Join-Path $RepoRoot $OutputDirectory
  New-Item -ItemType Directory -Force -Path $queueDir | Out-Null
  $queueSnapshot = [pscustomobject]@{
    timestamp = (Get-Date).ToString("o")
    branch = $Snapshot.branch
    clean_git_status = $Snapshot.clean_git_status
    queue_count = @($Snapshot.work_queue).Count
    work_queue = $Snapshot.work_queue
  }
  $queuePath = Join-Path $queueDir ("WORK_QUEUE_SNAPSHOT_{0}.json" -f (ConvertTo-SafeFileTimestamp))
  $latestPath = Join-Path $queueDir "LATEST_WORK_QUEUE.json"
  $queueSnapshot | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $queuePath -Encoding UTF8
  $queueSnapshot | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $latestPath -Encoding UTF8
  return $queuePath
}

function Save-OperatorVoiceBriefing {
  param(
    [pscustomobject]$Snapshot,
    [string]$OutputDirectory
  )
  $briefingDir = Join-Path $RepoRoot $OutputDirectory
  New-Item -ItemType Directory -Force -Path $briefingDir | Out-Null
  $briefingPath = Join-Path $briefingDir ("OPERATOR_VOICE_BRIEFING_{0}.md" -f (ConvertTo-SafeFileTimestamp))
  $repoState = if ($Snapshot.clean_git_status -eq $true) { "clean" } else { "dirty" }
  $latestReport = if (@($Snapshot.latest_report_references).Count -gt 0) { $Snapshot.latest_report_references[0].path } else { "UNKNOWN" }
  @(
    "# AI_OS Operator Voice Briefing",
    "",
    "## Repo Health",
    "AI_OS nervous system check: the repo is $repoState on branch `$($Snapshot.branch)`.",
    "",
    "## Current Counts",
    "- Files: $($Snapshot.total_files)",
    "- Reports: $($Snapshot.total_reports)",
    "- Validators: $($Snapshot.total_validators)",
    "- TODO markers: $($Snapshot.unresolved_todos)",
    "- FIXME markers: $($Snapshot.unresolved_fixmes)",
    "",
    "## Latest Evidence",
    "- Latest checkpoint: $($Snapshot.latest_checkpoint_reference)",
    "- Latest report: $latestReport",
    "",
    "## Safety Notes",
    "This briefing is informational only. It does not approve APPLY, commit, push, or external execution.",
    "",
    "## Next Safe Action",
    $Snapshot.next_safe_action
  ) | Set-Content -LiteralPath $briefingPath -Encoding UTF8
  return $briefingPath
}

function Get-LatestFileRefs {
  param([string[]]$Roots, [int]$Take = 5)
  $items = @()
  foreach ($root in $Roots) {
    $full = Join-Path $RepoRoot $root
    if (Test-Path -LiteralPath $full) {
      $items += Get-ChildItem -LiteralPath $full -Recurse -File -ErrorAction SilentlyContinue
    }
  }
  return @($items | Sort-Object LastWriteTime -Descending | Select-Object -First $Take | ForEach-Object {
    [pscustomobject]@{
      path = $_.FullName.Substring($RepoRoot.Length + 1)
      last_write_time = $_.LastWriteTime.ToString("o")
    }
  })
}

function Count-Marker {
  param([string]$Pattern)
  $scanFiles = Get-ChildItem -LiteralPath $RepoRoot -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object { $_.FullName -notmatch "\\.git\\" }
  $matches = $scanFiles | Select-String -Pattern $Pattern -ErrorAction SilentlyContinue
  return @($matches).Count
}

function Get-RelativePath {
  param([System.IO.FileSystemInfo]$Item)
  return ($Item.FullName.Substring($RepoRoot.Length + 1) -replace "\\", "/")
}

function Add-FocusScore {
  param(
    [hashtable]$Scores,
    [System.Collections.Generic.List[object]]$Evidence,
    [string]$Focus,
    [string]$Subsystem,
    [string]$Path,
    [string]$Reason
  )
  if (-not $Scores.ContainsKey($Focus)) {
    $Scores[$Focus] = 0
  }
  $Scores[$Focus] += 1
  $Evidence.Add([pscustomobject]@{
    focus = $Focus
    subsystem = $Subsystem
    path = $Path
    reason = $Reason
  }) | Out-Null
}

function Get-FocusSignalForPath {
  param([string]$Path)
  $normalized = ($Path -replace "\\", "/").ToLowerInvariant()
  if ($normalized -match "work_intelligence") {
    return @{ focus = "Work Intelligence"; subsystem = "work_intelligence" }
  }
  if ($normalized -match "automation/operator|docs/ai_os/operator|reports/operator") {
    return @{ focus = "Operator Orchestration"; subsystem = "operator" }
  }
  if ($normalized -match "trading_lab|trading_laboratory|reports/trading_lab") {
    return @{ focus = "Trading Lab"; subsystem = "trading_lab" }
  }
  if ($normalized -match "apps/dashboard") {
    return @{ focus = "Dashboard UI"; subsystem = "dashboard" }
  }
  return $null
}

function Get-FocusRecommendation {
  param(
    [string]$Focus,
    [int]$TodoCount
  )
  switch ($Focus) {
    "Work Intelligence" { return "Review latest operator voice briefing." }
    "Operator Orchestration" { return "Run morning startup flow." }
    "Trading Lab" { return "Prepare next DRY_RUN workload." }
    "Dashboard UI" { return "Review dashboard validation and preview." }
    default {
      if ($TodoCount -gt 0) {
        return "Review unresolved TODO markers."
      }
      return "UNKNOWN"
    }
  }
}

function Get-FocusDetection {
  param(
    [object[]]$RecentFiles,
    [object[]]$CheckpointRefs,
    [object[]]$ReportRefs,
    [int]$TodoCount
  )
  $scores = @{}
  $evidence = New-Object System.Collections.Generic.List[object]

  foreach ($file in @($RecentFiles)) {
    $relative = Get-RelativePath -Item $file
    $signal = Get-FocusSignalForPath -Path $relative
    if ($signal) {
      Add-FocusScore -Scores $scores -Evidence $evidence -Focus $signal.focus -Subsystem $signal.subsystem -Path $relative -Reason "recent_file"
    }
  }

  foreach ($ref in @($CheckpointRefs)) {
    $signal = Get-FocusSignalForPath -Path $ref.path
    if ($signal) {
      Add-FocusScore -Scores $scores -Evidence $evidence -Focus $signal.focus -Subsystem $signal.subsystem -Path $ref.path -Reason "latest_checkpoint"
    }
  }

  foreach ($ref in @($ReportRefs)) {
    $signal = Get-FocusSignalForPath -Path $ref.path
    if ($signal) {
      Add-FocusScore -Scores $scores -Evidence $evidence -Focus $signal.focus -Subsystem $signal.subsystem -Path $ref.path -Reason "latest_report"
    }
  }

  if ($scores.Count -eq 0) {
    return [pscustomobject]@{
      current_focus_area = "UNKNOWN"
      active_subsystem = "UNKNOWN"
      recommended_next_workload = (Get-FocusRecommendation -Focus "UNKNOWN" -TodoCount $TodoCount)
      focus_evidence_sources = @()
    }
  }

  $ranked = @($scores.GetEnumerator() | Sort-Object Value -Descending)
  $top = $ranked[0]
  $isTie = $ranked.Count -gt 1 -and $ranked[1].Value -eq $top.Value
  if ($top.Value -lt 2 -or $isTie) {
    return [pscustomobject]@{
      current_focus_area = "UNKNOWN"
      active_subsystem = "UNKNOWN"
      recommended_next_workload = (Get-FocusRecommendation -Focus "UNKNOWN" -TodoCount $TodoCount)
      focus_evidence_sources = @($evidence)
    }
  }

  $topEvidence = @($evidence | Where-Object { $_.focus -eq $top.Key })
  $subsystem = if ($topEvidence.Count -gt 0) { $topEvidence[0].subsystem } else { "UNKNOWN" }
  return [pscustomobject]@{
    current_focus_area = $top.Key
    active_subsystem = $subsystem
    recommended_next_workload = (Get-FocusRecommendation -Focus $top.Key -TodoCount $TodoCount)
    focus_evidence_sources = $topEvidence
  }
}

function Add-SecurityWarning {
  param(
    [System.Collections.Generic.List[object]]$Warnings,
    [string]$Type,
    [string]$Severity,
    [string]$Category,
    [string]$Path
  )
  $allowedSeverities = @("HIGH", "MEDIUM", "LOW", "INFO")
  $allowedCategories = @("secret_material", "secret_wording_review", "execution_boundary_review", "git_safety", "destructive_command", "protected_file_status", "policy_mention")
  if ($allowedSeverities -notcontains $Severity) {
    throw "Unknown security warning severity: $Severity"
  }
  if ($allowedCategories -notcontains $Category) {
    throw "Unknown security warning category: $Category"
  }
  $Warnings.Add([pscustomobject]@{
    warning_type = $Type
    severity = $Severity
    category = $Category
    path = $Path
  }) | Out-Null
}

function Test-PolicyReferencePath {
  param([string]$Path)
  $normalized = ($Path -replace "\\", "/").ToLowerInvariant()
  return (
    $normalized -match "^docs/ai_os/(security|secrets|governance|risk|risk_controls|compliance|legal|approval|change_control)" -or
    $normalized -match "readme" -or
    $normalized -match "policy" -or
    $normalized -match "workflow" -or
    $normalized -match "contract" -or
    $normalized -match "safety" -or
    $normalized -match "governance"
  )
}

function New-SecurityWarningSummary {
  param(
    [object[]]$Warnings,
    [int]$SuppressedPolicyMentions
  )
  $high = @($Warnings | Where-Object { $_.severity -eq "HIGH" }).Count
  $medium = @($Warnings | Where-Object { $_.severity -eq "MEDIUM" }).Count
  $low = @($Warnings | Where-Object { $_.severity -eq "LOW" }).Count
  $info = @($Warnings | Where-Object { $_.severity -eq "INFO" }).Count
  return [pscustomobject]@{
    security_warning_count = @($Warnings).Count
    high_risk_count = $high
    medium_risk_count = $medium
    low_risk_count = $low
    info_count = $info
    suppressed_policy_mentions = $SuppressedPolicyMentions
  }
}

function Get-StaleWorkItems {
  param(
    [object[]]$ReportRefs,
    [object[]]$CheckpointRefs
  )
  $items = New-Object System.Collections.Generic.List[object]
  $now = Get-Date
  $rules = @(
    @{ pattern = "Reports/work_intelligence/daily/"; item_type = "daily_snapshot"; stale_after_days = 1 },
    @{ pattern = "Reports/work_intelligence/briefings/"; item_type = "operator_briefing"; stale_after_days = 1 },
    @{ pattern = "Reports/"; item_type = "report"; stale_after_days = 7 },
    @{ pattern = "checkpoint"; item_type = "checkpoint"; stale_after_days = 14 }
  )

  foreach ($ref in @($ReportRefs + $CheckpointRefs)) {
    if (-not $ref.path -or -not $ref.last_write_time) { continue }
    $matchedRule = $null
    foreach ($rule in $rules) {
      if (($ref.path -replace "\\", "/").StartsWith($rule.pattern) -or ($ref.path -replace "\\", "/").ToLowerInvariant().Contains($rule.pattern)) {
        $matchedRule = $rule
        break
      }
    }
    if (-not $matchedRule) { continue }
    $lastWrite = [datetime]::Parse($ref.last_write_time)
    $ageDays = ($now - $lastWrite).TotalDays
    if ($ageDays -gt $matchedRule.stale_after_days) {
      $items.Add([pscustomobject]@{
        item_type = $matchedRule.item_type
        path = $ref.path
        last_write_time = $ref.last_write_time
        stale_after_days = $matchedRule.stale_after_days
      }) | Out-Null
    }
  }

  return @($items | Sort-Object item_type, path -Unique)
}

function Get-WorkMarkerCount {
  param(
    [object[]]$Refs,
    [string]$Pattern
  )
  $count = 0
  foreach ($ref in @($Refs)) {
    if (-not $ref.path) { continue }
    $fullPath = Join-Path $RepoRoot $ref.path
    $pathMatches = $ref.path -match $Pattern
    $contentMatches = $false
    if (Test-Path -LiteralPath $fullPath) {
      $content = Get-Content -LiteralPath $fullPath -Raw -ErrorAction SilentlyContinue
      if (-not [string]::IsNullOrWhiteSpace($content)) {
        $contentMatches = $content -match $Pattern
      }
    }
    if ($pathMatches -or $contentMatches) {
      $count += 1
    }
  }
  return $count
}

function Test-ProtectedWorkerPath {
  param(
    [string]$Path,
    [string[]]$ProtectedFiles
  )
  if ([string]::IsNullOrWhiteSpace($Path)) { return $false }
  $normalized = ($Path -replace "\\", "/").Trim()
  foreach ($protected in @($ProtectedFiles)) {
    $protectedPath = ($protected -replace "\\", "/").Trim()
    if ($normalized -ieq $protectedPath) {
      return $true
    }
  }
  return $false
}

function Get-WorkerReportEvidence {
  param(
    [string]$WorkerReportDir,
    [string[]]$ProtectedFiles
  )
  $requiredFields = @("worker_id", "label", "mode", "files_planned", "files_deleted", "validation_commands", "summary")
  $reports = New-Object System.Collections.Generic.List[object]
  $issues = New-Object System.Collections.Generic.List[object]
  $plannedFileMap = @{}

  if (-not (Test-Path -LiteralPath $WorkerReportDir)) {
    $issues.Add([pscustomobject]@{
      issue_type = "missing_worker_report_folder"
      status = "REVIEW"
      path = "Reports/operator/worker-reports"
      detail = "Worker report folder is missing."
    }) | Out-Null
    $issueCount = $issues.Count
    return [pscustomobject]@{
      worker_report_presence = "MISSING"
      worker_report_count = 0
      valid_worker_report_count = 0
      invalid_worker_report_count = 0
      worker_report_issue_count = $issueCount
      worker_report_evidence = [object[]]@()
      worker_report_issues = $issues.ToArray()
      worker_conflict_count = 0
      worker_conflicts = [object[]]@()
    }
  }

  $reportFiles = @(Get-ChildItem -LiteralPath $WorkerReportDir -File -Filter "*.json" -ErrorAction SilentlyContinue)
  if (@($reportFiles).Count -eq 0) {
    $issues.Add([pscustomobject]@{
      issue_type = "empty_worker_report_folder"
      status = "REVIEW"
      path = "Reports/operator/worker-reports"
      detail = "Worker report folder exists but contains no JSON worker reports."
    }) | Out-Null
    $issueCount = $issues.Count
    return [pscustomobject]@{
      worker_report_presence = "EMPTY"
      worker_report_count = 0
      valid_worker_report_count = 0
      invalid_worker_report_count = 0
      worker_report_issue_count = $issueCount
      worker_report_evidence = [object[]]@()
      worker_report_issues = $issues.ToArray()
      worker_conflict_count = 0
      worker_conflicts = [object[]]@()
    }
  }

  foreach ($file in $reportFiles) {
    $relativePath = Get-RelativePath -Item $file
    $parsed = $null
    try {
      $parsed = Get-Content -LiteralPath $file.FullName -Raw | ConvertFrom-Json
    } catch {
      $issues.Add([pscustomobject]@{
        issue_type = "invalid_worker_report_json"
        status = "BLOCKED"
        path = $relativePath
        detail = "Worker report JSON did not parse."
      }) | Out-Null
      continue
    }

    $missingFields = @()
    foreach ($field in $requiredFields) {
      if (-not ($parsed.PSObject.Properties.Name -contains $field)) {
        $missingFields += $field
      }
    }
    if (@($missingFields).Count -gt 0) {
      $issues.Add([pscustomobject]@{
        issue_type = "worker_report_missing_required_fields"
        status = "BLOCKED"
        path = $relativePath
        detail = "Missing required fields: $($missingFields -join ', ')"
      }) | Out-Null
    }

    $filesPlanned = @($parsed.files_planned)
    $filesDeleted = @($parsed.files_deleted)
    $validationCommands = @($parsed.validation_commands)
    $protectedPlannedFiles = @($filesPlanned | Where-Object { Test-ProtectedWorkerPath -Path ([string]$_) -ProtectedFiles $ProtectedFiles })
    $protectedDeletedFiles = @($filesDeleted | Where-Object { Test-ProtectedWorkerPath -Path ([string]$_) -ProtectedFiles $ProtectedFiles })

    if (@($filesDeleted).Count -gt 0) {
      $issues.Add([pscustomobject]@{
        issue_type = "worker_report_files_deleted_present"
        status = "BLOCKED"
        path = $relativePath
        detail = "files_deleted must remain empty for worker evidence ingestion."
      }) | Out-Null
    }
    if (@($validationCommands).Count -eq 0) {
      $issues.Add([pscustomobject]@{
        issue_type = "worker_report_missing_validation_commands"
        status = "BLOCKED"
        path = $relativePath
        detail = "validation_commands is empty or missing."
      }) | Out-Null
    }
    if (@($protectedPlannedFiles + $protectedDeletedFiles).Count -gt 0) {
      $issues.Add([pscustomobject]@{
        issue_type = "worker_report_protected_file_path"
        status = "BLOCKED"
        path = $relativePath
        detail = "Worker report references protected root files."
      }) | Out-Null
    }

    foreach ($planned in $filesPlanned) {
      if ([string]::IsNullOrWhiteSpace([string]$planned)) { continue }
      $normalizedPlanned = (([string]$planned) -replace "\\", "/").Trim().ToLowerInvariant()
      if (-not $plannedFileMap.ContainsKey($normalizedPlanned)) {
        $plannedFileMap[$normalizedPlanned] = New-Object System.Collections.Generic.List[object]
      }
      $plannedFileMap[$normalizedPlanned].Add([pscustomobject]@{
        worker_id = if ($parsed.worker_id) { $parsed.worker_id } else { "UNKNOWN" }
        source_path = $relativePath
      }) | Out-Null
    }

    $reports.Add([pscustomobject]@{
      worker_id = $parsed.worker_id
      label = $parsed.label
      mode = $parsed.mode
      source_path = $relativePath
      files_planned = $filesPlanned
      files_deleted = $filesDeleted
      validation_commands = $validationCommands
      summary = $parsed.summary
      evidence_only = $true
      approval_granted = $false
    }) | Out-Null
  }

  $conflicts = New-Object System.Collections.Generic.List[object]
  foreach ($entry in $plannedFileMap.GetEnumerator()) {
    $workers = @($entry.Value | ForEach-Object { [string]$_.worker_id } | Sort-Object -Unique)
    $sources = @($entry.Value | ForEach-Object { [string]$_.source_path } | Sort-Object -Unique)
    if (@($sources).Count -gt 1) {
      $conflictId = "WORKER-CONFLICT-{0}" -f (($entry.Key.ToUpperInvariant() -replace "[^A-Z0-9]", "-").Trim("-"))
      $conflicts.Add([pscustomobject]@{
        conflict_id = $conflictId
        file_path = $entry.Key
        workers = $workers
        severity = "HIGH"
        status = "BLOCKED"
        recommended_action = "Resolve worker file ownership conflict."
      }) | Out-Null
      $issues.Add([pscustomobject]@{
        issue_type = "worker_report_overlapping_planned_files"
        status = "BLOCKED"
        path = $entry.Key
        detail = "Planned file appears in multiple worker reports: $($sources -join ', ')"
      }) | Out-Null
    }
  }

  $invalidCount = @($issues | Where-Object { $_.status -eq "BLOCKED" }).Count
  $issueCount = $issues.Count
  $presence = if ($invalidCount -gt 0) { "PRESENT_WITH_ISSUES" } else { "PRESENT" }
  return [pscustomobject]@{
    worker_report_presence = $presence
    worker_report_count = @($reportFiles).Count
    valid_worker_report_count = $reports.Count
    invalid_worker_report_count = $invalidCount
    worker_report_issue_count = $issueCount
    worker_report_evidence = $reports.ToArray()
    worker_report_issues = $issues.ToArray()
    worker_conflict_count = $conflicts.Count
    worker_conflicts = $conflicts.ToArray()
  }
}

function Get-PriorityEngineResult {
  param(
    [bool]$CleanGitStatus,
    [int]$TodoCount,
    [int]$FixmeCount,
    [int]$ValidatorCount,
    [string]$WorkerReportPresence,
    [int]$WorkerLaneCount,
    [int]$WorkerReportCount,
    [int]$WorkerReportIssueCount,
    [object[]]$SecurityWarnings,
    [pscustomobject]$SecuritySummary,
    [object[]]$ReportRefs,
    [object[]]$CheckpointRefs,
    [pscustomobject]$FocusDetection
  )

  $staleItems = Get-StaleWorkItems -ReportRefs $ReportRefs -CheckpointRefs $CheckpointRefs
  $unfinishedRefs = @($ReportRefs + $CheckpointRefs)
  $unfinishedPhaseCount = Get-WorkMarkerCount -Refs $unfinishedRefs -Pattern "(?i)\b(DRY_RUN|WORKLOAD|PENDING|UNFINISHED)\b"
  $unfinishedStageCount = Get-WorkMarkerCount -Refs $unfinishedRefs -Pattern "(?i)\b(TODO|FIXME|NEXT SAFE ACTION|NEXT_SAFE_ACTION)\b"
  $blockedMarkerCount = Get-WorkMarkerCount -Refs $unfinishedRefs -Pattern "(?i)\b(BLOCKED|blocked_reason|dependency_blocked)\b"
  $blockedWorkerCount = if ($WorkerLaneCount -gt 0 -and $WorkerReportPresence -in @("MISSING", "EMPTY")) { $WorkerLaneCount } else { 0 }
  $blockedWorkCount = $blockedMarkerCount + $blockedWorkerCount
  $highRiskWarnings = @($SecurityWarnings | Where-Object { $_.severity -eq "HIGH" })
  $protectedRootChanges = @($SecurityWarnings | Where-Object { $_.category -eq "protected_file_status" })
  $dependencyBlocked = ($blockedWorkCount -gt 0 -or $ValidatorCount -eq 0 -or $WorkerReportPresence -in @("MISSING", "EMPTY", "PRESENT_WITH_ISSUES") -or $WorkerReportIssueCount -gt 0)

  $priorityScore = 0
  $urgencyScore = 0
  if (-not $CleanGitStatus) { $priorityScore += 20; $urgencyScore += 20 }
  if ($TodoCount -gt 0) { $priorityScore += [Math]::Min(20, $TodoCount) }
  if ($FixmeCount -gt 0) { $priorityScore += [Math]::Min(30, ($FixmeCount * 2)); $urgencyScore += [Math]::Min(20, $FixmeCount) }
  if ($ValidatorCount -eq 0) { $priorityScore += 25; $urgencyScore += 25 }
  if ($blockedWorkCount -gt 0) { $priorityScore += [Math]::Min(30, ($blockedWorkCount * 5)); $urgencyScore += [Math]::Min(30, ($blockedWorkCount * 5)) }
  if (@($ReportRefs).Count -eq 0) { $priorityScore += 15 }
  if (@($staleItems).Count -gt 0) { $priorityScore += [Math]::Min(25, (@($staleItems).Count * 5)); $urgencyScore += [Math]::Min(20, (@($staleItems).Count * 4)) }
  if ($SecuritySummary.high_risk_count -gt 0) { $priorityScore += 40; $urgencyScore += 40 }
  if ($WorkerLaneCount -gt 0 -and $WorkerReportCount -eq 0) { $priorityScore += 10 }
  if ($WorkerReportIssueCount -gt 0) { $priorityScore += [Math]::Min(30, ($WorkerReportIssueCount * 5)); $urgencyScore += [Math]::Min(30, ($WorkerReportIssueCount * 5)) }
  if ($SecuritySummary.suppressed_policy_mentions -gt 0) { $priorityScore += 0 }

  $safeToApply = (
    $CleanGitStatus -eq $true -and
    $ValidatorCount -gt 0 -and
    @($protectedRootChanges).Count -eq 0 -and
    @($highRiskWarnings).Count -eq 0 -and
    $dependencyBlocked -eq $false
  )

  $recommendedAction = "UNKNOWN"
  if (@($highRiskWarnings).Count -gt 0) {
    $recommendedAction = "Review security warnings."
  } elseif ($ValidatorCount -eq 0) {
    $recommendedAction = "Resolve validator failure."
  } elseif (-not $CleanGitStatus) {
    $recommendedAction = "Commit approved work."
  } elseif (@($staleItems).Count -gt 0) {
    $recommendedAction = "Review latest briefing."
  } elseif ($dependencyBlocked) {
    $recommendedAction = "Run next DRY_RUN workload."
  } elseif ($FocusDetection.recommended_next_workload -and $FocusDetection.recommended_next_workload -ne "UNKNOWN") {
    $recommendedAction = $FocusDetection.recommended_next_workload
  }

  $activeLane = if ($FocusDetection.current_focus_area -and $FocusDetection.current_focus_area -ne "UNKNOWN") {
    $FocusDetection.current_focus_area
  } else {
    "UNKNOWN"
  }

  return [pscustomobject]@{
    priority_score = $priorityScore
    urgency_score = $urgencyScore
    dependency_blocked = $dependencyBlocked
    safe_to_apply = $safeToApply
    recommended_operator_action = $recommendedAction
    stale_work_detected = (@($staleItems).Count -gt 0)
    stale_work_items = @($staleItems)
    unfinished_phase_count = $unfinishedPhaseCount
    unfinished_stage_count = $unfinishedStageCount
    blocked_work_count = $blockedWorkCount
    active_priority_lane = $activeLane
  }
}

function Add-WorkQueueItem {
  param(
    [System.Collections.Generic.List[object]]$Queue,
    [string]$TaskId,
    [string]$Title,
    [string]$Source,
    [string]$Priority,
    [string]$Status,
    [string]$RecommendedAction,
    [string]$SuggestedWorkerLane,
    [string]$EvidenceStrength,
    [string]$RouteReason
  )
  $allowedStatuses = @("REVIEW", "BLOCKED", "READY_FOR_DRY_RUN", "UNKNOWN")
  $allowedLanes = @("Dashboard UI", "Trading Lab", "Operator Orchestration", "Work Intelligence", "Validators", "Reports", "Mock Data", "UNKNOWN")
  if ($allowedStatuses -notcontains $Status) {
    throw "Unknown work queue status: $Status"
  }
  if ($allowedLanes -notcontains $SuggestedWorkerLane) {
    throw "Unknown suggested worker lane: $SuggestedWorkerLane"
  }
  $Queue.Add([pscustomobject]@{
    queue_rank = 0
    task_id = $TaskId
    title = $Title
    source = $Source
    priority = $Priority
    status = $Status
    recommended_action = $RecommendedAction
    suggested_worker_lane = $SuggestedWorkerLane
    evidence_strength = $EvidenceStrength
    route_reason = $RouteReason
  }) | Out-Null
}

function Get-SuggestedWorkerLane {
  param([string]$Source)
  $normalized = ($Source -replace "\\", "/").ToLowerInvariant()
  if ($normalized -match "apps/dashboard/mock-data") { return "Mock Data" }
  if ($normalized -match "apps/dashboard") { return "Dashboard UI" }
  if ($normalized -match "trading_lab|trading_laboratory") { return "Trading Lab" }
  if ($normalized -match "automation/operator|docs/ai_os/operator|reports/operator") { return "Operator Orchestration" }
  if ($normalized -match "test-aios|validator|validation") { return "Validators" }
  if ($normalized -match "reports/work_intelligence/daily|reports/work_intelligence/briefings|work_intelligence|recommended_operator_action") { return "Work Intelligence" }
  if ($normalized -match "^reports/|report") { return "Reports" }
  if ($normalized -match "worker_report") { return "Operator Orchestration" }
  return "UNKNOWN"
}

function Get-RouteReason {
  param([string]$Source)
  $normalized = ($Source -replace "\\", "/").ToLowerInvariant()
  if ($normalized -match "apps/dashboard/mock-data") { return "dashboard mock-data path evidence" }
  if ($normalized -match "apps/dashboard") { return "dashboard path evidence" }
  if ($normalized -match "trading_lab|trading_laboratory") { return "trading lab path evidence" }
  if ($normalized -match "automation/operator|docs/ai_os/operator|reports/operator|worker_report") { return "operator orchestration path evidence" }
  if ($normalized -match "test-aios|validator|validation") { return "validator evidence" }
  if ($normalized -match "reports/work_intelligence/daily|reports/work_intelligence/briefings|work_intelligence|recommended_operator_action") { return "work intelligence evidence" }
  if ($normalized -match "^reports/|report") { return "report path evidence" }
  return "UNKNOWN"
}

function Get-QueuePriorityWeight {
  param([string]$Priority)
  switch ($Priority) {
    "HIGH" { return 1 }
    "MEDIUM" { return 2 }
    "LOW" { return 3 }
    default { return 9 }
  }
}

function Get-QueueStatusWeight {
  param([string]$Status)
  switch ($Status) {
    "BLOCKED" { return 1 }
    "REVIEW" { return 2 }
    "READY_FOR_DRY_RUN" { return 3 }
    default { return 9 }
  }
}

function Get-QueueSourceWeight {
  param([object]$Item)
  if ($Item.source -eq "security_warnings") { return 1 }
  if ($Item.source -eq "git status") { return 2 }
  if ($Item.task_id -match "^WI-STALE-") { return 3 }
  if ($Item.source -eq "worker_report_presence") { return 4 }
  return 9
}

function ConvertTo-RankedWorkQueue {
  param([object[]]$Queue)
  $ranked = @($Queue | Sort-Object `
    @{ Expression = { Get-QueuePriorityWeight -Priority $_.priority }; Ascending = $true }, `
    @{ Expression = { Get-QueueStatusWeight -Status $_.status }; Ascending = $true }, `
    @{ Expression = { Get-QueueSourceWeight -Item $_ }; Ascending = $true }, `
    @{ Expression = { $_.task_id }; Ascending = $true }, `
    @{ Expression = { $_.source }; Ascending = $true })

  $result = New-Object System.Collections.Generic.List[object]
  $rank = 1
  foreach ($item in $ranked) {
    $result.Add([pscustomobject]@{
      queue_rank = $rank
      task_id = $item.task_id
      title = $item.title
      source = $item.source
      priority = $item.priority
      status = $item.status
      recommended_action = $item.recommended_action
      suggested_worker_lane = $item.suggested_worker_lane
      evidence_strength = $item.evidence_strength
      route_reason = $item.route_reason
    }) | Out-Null
    $rank += 1
  }
  return $result.ToArray()
}

function Get-WorkQueue {
  param(
    [int]$TodoCount,
    [int]$FixmeCount,
    [object[]]$StaleWorkItems,
    [object[]]$SecurityWarnings,
    [string]$RecommendedOperatorAction,
    [bool]$CleanGitStatus,
    [string]$WorkerReportPresence,
    [object[]]$WorkerReportEvidence,
    [object[]]$WorkerReportIssues,
    [object[]]$WorkerConflicts
  )
  $queue = New-Object System.Collections.Generic.List[object]

  if ($TodoCount -gt 0) {
    Add-WorkQueueItem -Queue $queue -TaskId "WI-TODO-REVIEW" -Title "Review unresolved TODO markers." -Source "TODO count" -Priority "MEDIUM" -Status "REVIEW" -RecommendedAction "Review unresolved TODO markers." -SuggestedWorkerLane "Work Intelligence" -EvidenceStrength "MEDIUM" -RouteReason "TODO count evidence"
  }
  if ($FixmeCount -gt 0) {
    Add-WorkQueueItem -Queue $queue -TaskId "WI-FIXME-REVIEW" -Title "Review unresolved FIXME markers." -Source "FIXME count" -Priority "HIGH" -Status "REVIEW" -RecommendedAction "Review unresolved FIXME markers." -SuggestedWorkerLane "Work Intelligence" -EvidenceStrength "HIGH" -RouteReason "FIXME count evidence"
  }
  foreach ($item in @($StaleWorkItems)) {
    $taskId = "WI-STALE-{0}" -f (([string]$item.item_type).ToUpperInvariant() -replace "[^A-Z0-9]", "-")
    $lane = Get-SuggestedWorkerLane -Source $item.path
    $reason = Get-RouteReason -Source $item.path
    Add-WorkQueueItem -Queue $queue -TaskId $taskId -Title "Review stale work evidence." -Source $item.path -Priority "MEDIUM" -Status "REVIEW" -RecommendedAction "Review latest briefing." -SuggestedWorkerLane $lane -EvidenceStrength "MEDIUM" -RouteReason $reason
  }
  $highSecurityWarnings = @($SecurityWarnings | Where-Object { $_.severity -eq "HIGH" })
  $reviewSecurityWarnings = @($SecurityWarnings | Where-Object { $_.severity -in @("HIGH", "MEDIUM") })
  if (@($highSecurityWarnings).Count -gt 0) {
    Add-WorkQueueItem -Queue $queue -TaskId "WI-SECURITY-HIGH" -Title "Review high-risk security warnings." -Source "security_warnings" -Priority "HIGH" -Status "BLOCKED" -RecommendedAction "Review security warnings." -SuggestedWorkerLane "Work Intelligence" -EvidenceStrength "HIGH" -RouteReason "high-risk security warning evidence"
  } elseif (@($reviewSecurityWarnings).Count -gt 0) {
    Add-WorkQueueItem -Queue $queue -TaskId "WI-SECURITY-REVIEW" -Title "Review security warnings." -Source "security_warnings" -Priority "MEDIUM" -Status "REVIEW" -RecommendedAction "Review security warnings." -SuggestedWorkerLane "Work Intelligence" -EvidenceStrength "MEDIUM" -RouteReason "security warning evidence"
  }
  if (-not $CleanGitStatus) {
    Add-WorkQueueItem -Queue $queue -TaskId "WI-GIT-DIRTY" -Title "Review dirty git status." -Source "git status" -Priority "HIGH" -Status "REVIEW" -RecommendedAction "Commit approved work." -SuggestedWorkerLane "Operator Orchestration" -EvidenceStrength "HIGH" -RouteReason "dirty git status evidence"
  }
  if ($WorkerReportPresence -in @("MISSING", "EMPTY")) {
    Add-WorkQueueItem -Queue $queue -TaskId "WI-WORKER-REPORTS-MISSING" -Title "Review missing worker reports." -Source "worker_report_presence" -Priority "MEDIUM" -Status "REVIEW" -RecommendedAction "Collect worker reports before APPLY review." -SuggestedWorkerLane "Operator Orchestration" -EvidenceStrength "MEDIUM" -RouteReason "missing worker report evidence"
  }
  foreach ($issue in @($WorkerReportIssues)) {
    $status = if ($issue.status -eq "BLOCKED") { "BLOCKED" } else { "REVIEW" }
    $priority = if ($status -eq "BLOCKED") { "HIGH" } else { "MEDIUM" }
    $taskSuffix = (([string]$issue.issue_type).ToUpperInvariant() -replace "[^A-Z0-9]", "-")
    Add-WorkQueueItem -Queue $queue -TaskId "WI-WORKER-$taskSuffix" -Title "Review worker report evidence." -Source $issue.path -Priority $priority -Status $status -RecommendedAction "Review worker report evidence; this is not APPLY approval." -SuggestedWorkerLane "Operator Orchestration" -EvidenceStrength "HIGH" -RouteReason $issue.detail
  }
  if (@($WorkerConflicts).Count -gt 0) {
    Add-WorkQueueItem -Queue $queue -TaskId "WI-WORKER-FILE-CONFLICT" -Title "Resolve worker file ownership conflict." -Source "worker_conflicts" -Priority "HIGH" -Status "BLOCKED" -RecommendedAction "Resolve worker file ownership conflict." -SuggestedWorkerLane "Operator Orchestration" -EvidenceStrength "HIGH" -RouteReason "overlapping files_planned evidence"
  }
  foreach ($report in @($WorkerReportEvidence)) {
    Add-WorkQueueItem -Queue $queue -TaskId ("WI-WORKER-REPORT-{0}" -f $report.worker_id) -Title "Review worker report evidence." -Source $report.source_path -Priority "MEDIUM" -Status "REVIEW" -RecommendedAction "Review worker report evidence; this is not APPLY approval." -SuggestedWorkerLane "Operator Orchestration" -EvidenceStrength "MEDIUM" -RouteReason "worker report evidence only"
  }
  if ($RecommendedOperatorAction -and $RecommendedOperatorAction -ne "UNKNOWN") {
    Add-WorkQueueItem -Queue $queue -TaskId "WI-OPERATOR-ACTION" -Title $RecommendedOperatorAction -Source "recommended_operator_action" -Priority "MEDIUM" -Status "REVIEW" -RecommendedAction $RecommendedOperatorAction -SuggestedWorkerLane "Work Intelligence" -EvidenceStrength "MEDIUM" -RouteReason "recommended operator action evidence"
  }

  if ($queue.Count -eq 0) {
    Add-WorkQueueItem -Queue $queue -TaskId "WI-QUEUE-UNKNOWN" -Title "UNKNOWN" -Source "UNKNOWN" -Priority "UNKNOWN" -Status "UNKNOWN" -RecommendedAction "UNKNOWN" -SuggestedWorkerLane "UNKNOWN" -EvidenceStrength "UNKNOWN" -RouteReason "UNKNOWN"
  }

  return ConvertTo-RankedWorkQueue -Queue @($queue | Sort-Object task_id, source -Unique)
}

function Get-SecurityWarnings {
  param(
    [object[]]$Files,
    [string]$GitStatusText,
    [string[]]$ProtectedFiles
  )
  $warnings = New-Object System.Collections.Generic.List[object]
  $suppressedPolicyMentions = 0
  $policyMentionCap = 25
  $policyMentionDetailCount = 0
  $textExtensions = @(".ps1", ".json", ".md", ".txt", ".csv", ".yml", ".yaml", ".js", ".html", ".css")
  foreach ($file in @($Files)) {
    $relative = Get-RelativePath -Item $file
    if ($relative -match "(^|/)\.env($|\.|/)") {
      Add-SecurityWarning -Warnings $warnings -Type ".env file present" -Severity "HIGH" -Category "secret_material" -Path $relative
    }
    if ($textExtensions -notcontains $file.Extension.ToLowerInvariant()) {
      continue
    }
    $content = Get-Content -LiteralPath $file.FullName -Raw -ErrorAction SilentlyContinue
    if ([string]::IsNullOrWhiteSpace($content)) {
      continue
    }

    $isPolicyReference = Test-PolicyReferencePath -Path $relative
    $hasSecretWording = $content -match "(?i)(api[_ -]?key|\b(secret|token|password)\b)"
    $hasExecutionBoundaryWording = $content -match "(?i)\b(broker|oanda|live execution)\b"
    $hasLikelySecretMaterial = (
      $relative -match "(^|/)\.env($|\.|/)" -or
      $content -match '(?i)(api[_ -]?key|secret|token|password)\s*[:=]\s*[''"][^''"]{8,}' -or
      $content -match "(?i)(bearer\s+[a-z0-9._~+/=-]{16,}|akia[0-9a-z]{16})"
    )

    if ($hasLikelySecretMaterial) {
      Add-SecurityWarning -Warnings $warnings -Type "possible secret material present" -Severity "HIGH" -Category "secret_material" -Path $relative
    } elseif ($hasSecretWording) {
      if ($isPolicyReference) {
        $suppressedPolicyMentions += 1
        if ($policyMentionDetailCount -lt $policyMentionCap) {
          Add-SecurityWarning -Warnings $warnings -Type "secret_wording_review" -Severity "INFO" -Category "policy_mention" -Path $relative
          $policyMentionDetailCount += 1
        }
      } elseif ($relative -match "\.(ps1|json|yml|yaml|js)$|automation/|config") {
        Add-SecurityWarning -Warnings $warnings -Type "secret_wording_review" -Severity "MEDIUM" -Category "secret_wording_review" -Path $relative
      } else {
        Add-SecurityWarning -Warnings $warnings -Type "secret_wording_review" -Severity "LOW" -Category "secret_wording_review" -Path $relative
      }
    }

    if ($hasExecutionBoundaryWording) {
      if ($isPolicyReference) {
        Add-SecurityWarning -Warnings $warnings -Type "execution boundary wording" -Severity "INFO" -Category "execution_boundary_review" -Path $relative
      } elseif ($content -match "(?i)(enable|enabled|start|run|execute).{0,40}(broker|oanda|live execution|real orders|order execution)") {
        Add-SecurityWarning -Warnings $warnings -Type "execution boundary wording" -Severity "HIGH" -Category "execution_boundary_review" -Path $relative
      } else {
        Add-SecurityWarning -Warnings $warnings -Type "execution boundary wording" -Severity "MEDIUM" -Category "execution_boundary_review" -Path $relative
      }
    }
    if ($content -match "(?i)git\s+add\s+\.") {
      Add-SecurityWarning -Warnings $warnings -Type "git add dot wording" -Severity "MEDIUM" -Category "git_safety" -Path $relative
    }
    if ($content -match "(?i)\b(rm\s+-rf|remove-item\s+-recurse|git\s+reset\s+--hard|del\s+/s)\b") {
      Add-SecurityWarning -Warnings $warnings -Type "destructive command wording" -Severity "HIGH" -Category "destructive_command" -Path $relative
    }
  }

  foreach ($line in @($GitStatusText -split "`r?`n")) {
    if (-not $line -or $line.Length -lt 4) { continue }
    $path = ($line.Substring(3).Trim() -replace "\\", "/")
    foreach ($protected in $ProtectedFiles) {
      if ($path -ieq ($protected -replace "\\", "/")) {
        Add-SecurityWarning -Warnings $warnings -Type "protected root file change" -Severity "MEDIUM" -Category "protected_file_status" -Path $path
      }
    }
  }

  $sortedWarnings = @($warnings | Sort-Object warning_type, severity, category, path -Unique)
  return [pscustomobject]@{
    warnings = $sortedWarnings
    summary = (New-SecurityWarningSummary -Warnings $sortedWarnings -SuppressedPolicyMentions $suppressedPolicyMentions)
  }
}

function Get-OperatorRegistryAdapterResult {
  param(
    [string]$AdapterPath = "automation/operator/Get-AiOsOperatorRegistryAdapter.DRY_RUN.ps1",
    [string]$LegacyRegistryPath
  )

  $adapterFullPath = Join-Path $RepoRoot $AdapterPath
  $legacyFullPath = Join-Path $RepoRoot $LegacyRegistryPath

  if (Test-Path -LiteralPath $adapterFullPath -PathType Leaf) {
    try {
      $adapter = & powershell -NoProfile -ExecutionPolicy Bypass -File $adapterFullPath -RepoRoot $RepoRoot -OutputJson | ConvertFrom-Json
      if ($adapter -and $adapter.source.primary_worker_source -eq "canonical_runtime_registry") {
        return [pscustomobject]@{
          worker_lane_count = @($adapter.runtime_workers).Count
          worker_registry_source = "operator_registry_adapter"
          operator_registry_adapter_path = $AdapterPath
          legacy_worker_registry_path = $LegacyRegistryPath
          legacy_registry_role = "compatibility_evidence_only"
          legacy_registry_primary_source = $false
        }
      }
    } catch {
      # Fall back to the legacy compatibility registry only when adapter evidence cannot be read.
    }
  }

  $legacyCount = 0
  if (Test-Path -LiteralPath $legacyFullPath -PathType Leaf) {
    $legacy = Get-Content -LiteralPath $legacyFullPath -Raw | ConvertFrom-Json
    $legacyCount = @($legacy.workers).Count
  }

  return [pscustomobject]@{
    worker_lane_count = $legacyCount
    worker_registry_source = "legacy_compatibility_fallback"
    operator_registry_adapter_path = $AdapterPath
    legacy_worker_registry_path = $LegacyRegistryPath
    legacy_registry_role = "compatibility_fallback_only"
    legacy_registry_primary_source = $false
  }
}

$gitBranch = Get-CommandText "git branch --show-current"
$gitStatusShort = Get-CommandText "git status --short"
$latestCommit = Get-CommandText "git log -1 --oneline"
$allFiles = @(Get-ChildItem -LiteralPath $RepoRoot -Recurse -File -ErrorAction SilentlyContinue)
$allFolders = @(Get-ChildItem -LiteralPath $RepoRoot -Recurse -Directory -ErrorAction SilentlyContinue)
$reports = @(Get-ChildItem -LiteralPath (Join-Path $RepoRoot "Reports") -Recurse -File -ErrorAction SilentlyContinue)
$validators = @(Get-ChildItem -LiteralPath (Join-Path $RepoRoot "automation") -Recurse -File -Filter "Test-AiOs*.ps1" -ErrorAction SilentlyContinue)
$automationScripts = @(Get-ChildItem -LiteralPath (Join-Path $RepoRoot "automation") -Recurse -File -Filter "*.ps1" -ErrorAction SilentlyContinue)
$checkpoints = @()
foreach ($checkpointRoot in @($config.checkpoint_roots)) {
  $full = Join-Path $RepoRoot $checkpointRoot
  if (Test-Path -LiteralPath $full) {
    $checkpoints += Get-ChildItem -LiteralPath $full -Recurse -File -ErrorAction SilentlyContinue
  }
}

$workerLaneCount = 0
$workerReportPresence = "UNKNOWN"
$workerReportCount = 0
$validWorkerReportCount = 0
$invalidWorkerReportCount = 0
$workerReportIssueCount = 0
$workerReportEvidence = @()
$workerReportIssues = @()
$registryAdapterResult = Get-OperatorRegistryAdapterResult -LegacyRegistryPath $config.worker_registry_path
$workerLaneCount = $registryAdapterResult.worker_lane_count
$workerReportDir = Join-Path $RepoRoot $config.worker_report_directory
$workerReportResult = Get-WorkerReportEvidence -WorkerReportDir $workerReportDir -ProtectedFiles @($config.protected_files)
$workerReportPresence = $workerReportResult.worker_report_presence
$workerReportCount = $workerReportResult.worker_report_count
$validWorkerReportCount = $workerReportResult.valid_worker_report_count
$invalidWorkerReportCount = $workerReportResult.invalid_worker_report_count
$workerReportIssueCount = $workerReportResult.worker_report_issue_count
$workerReportEvidence = @($workerReportResult.worker_report_evidence)
$workerReportIssues = @($workerReportResult.worker_report_issues)
$workerConflictCount = $workerReportResult.worker_conflict_count
$workerConflicts = @($workerReportResult.worker_conflicts)

$latestCheckpointRefs = Get-LatestFileRefs -Roots @($config.checkpoint_roots)
$latestReportRefs = Get-LatestFileRefs -Roots @($config.report_roots)
$latestCheckpointReference = if (@($latestCheckpointRefs).Count -gt 0) { $latestCheckpointRefs[0].path } else { "UNKNOWN" }
$cleanGitStatus = [string]::IsNullOrWhiteSpace($gitStatusShort)
$unresolvedTodos = Count-Marker "TODO"
$unresolvedFixmes = Count-Marker "FIXME"
$recentFiles = @($allFiles | Where-Object { $_.FullName -notmatch "\\.git\\" } | Sort-Object LastWriteTime -Descending | Select-Object -First 25)
$focusDetection = Get-FocusDetection -RecentFiles $recentFiles -CheckpointRefs $latestCheckpointRefs -ReportRefs $latestReportRefs -TodoCount $unresolvedTodos
$securityWarningResult = Get-SecurityWarnings -Files $allFiles -GitStatusText $gitStatusShort -ProtectedFiles @($config.protected_files)
$securityWarnings = @($securityWarningResult.warnings)
$securityWarningSummary = $securityWarningResult.summary
$priorityEngine = Get-PriorityEngineResult `
  -CleanGitStatus $cleanGitStatus `
  -TodoCount $unresolvedTodos `
  -FixmeCount $unresolvedFixmes `
  -ValidatorCount $validators.Count `
  -WorkerReportPresence $workerReportPresence `
  -WorkerLaneCount $workerLaneCount `
  -WorkerReportCount $workerReportCount `
  -WorkerReportIssueCount $workerReportIssueCount `
  -SecurityWarnings $securityWarnings `
  -SecuritySummary $securityWarningSummary `
  -ReportRefs $latestReportRefs `
  -CheckpointRefs $latestCheckpointRefs `
  -FocusDetection $focusDetection
$workQueue = Get-WorkQueue `
  -TodoCount $unresolvedTodos `
  -FixmeCount $unresolvedFixmes `
  -StaleWorkItems $priorityEngine.stale_work_items `
  -SecurityWarnings $securityWarnings `
  -RecommendedOperatorAction $priorityEngine.recommended_operator_action `
  -CleanGitStatus $cleanGitStatus `
  -WorkerReportPresence $workerReportPresence `
  -WorkerReportEvidence $workerReportEvidence `
  -WorkerReportIssues $workerReportIssues `
  -WorkerConflicts $workerConflicts

$snapshot = [pscustomobject]@{
  schema = "AIOS_WORK_INTELLIGENCE_SCAN_RESULT.v2"
  timestamp = (Get-Date).ToString("o")
  read_only = $true
  repo_root = $RepoRoot
  branch = $gitBranch
  clean_git_status = $cleanGitStatus
  git_clean = $cleanGitStatus
  git_status_short = $gitStatusShort
  latest_commit = $latestCommit
  total_files = $allFiles.Count
  total_folders = $allFolders.Count
  total_reports = $reports.Count
  total_validators = $validators.Count
  total_checkpoints = $checkpoints.Count
  total_scripts = $automationScripts.Count
  total_automation_scripts = $automationScripts.Count
  total_json_files = Count-Files "*.json"
  total_markdown_files = Count-Files "*.md"
  worker_lane_count = $workerLaneCount
  worker_registry_source = $registryAdapterResult.worker_registry_source
  operator_registry_adapter_path = $registryAdapterResult.operator_registry_adapter_path
  legacy_worker_registry_path = $registryAdapterResult.legacy_worker_registry_path
  legacy_registry_role = $registryAdapterResult.legacy_registry_role
  legacy_registry_primary_source = $registryAdapterResult.legacy_registry_primary_source
  worker_report_count = $workerReportCount
  valid_worker_report_count = $validWorkerReportCount
  invalid_worker_report_count = $invalidWorkerReportCount
  worker_report_issue_count = $workerReportIssueCount
  unresolved_todos = $unresolvedTodos
  unresolved_fixmes = $unresolvedFixmes
  unresolved_todo_markers = $unresolvedTodos
  unresolved_fixme_markers = $unresolvedFixmes
  worker_report_presence = $workerReportPresence
  worker_report_evidence = $workerReportEvidence
  worker_report_issues = $workerReportIssues
  worker_conflict_count = $workerConflictCount
  worker_conflicts = $workerConflicts
  validation_health = "UNKNOWN_UNTIL_VALIDATOR_RUN"
  latest_checkpoint_reference = $latestCheckpointReference
  latest_checkpoint_references = $latestCheckpointRefs
  latest_report_references = $latestReportRefs
  current_focus_area = $focusDetection.current_focus_area
  active_subsystem = $focusDetection.active_subsystem
  recommended_next_workload = $focusDetection.recommended_next_workload
  focus_evidence_sources = $focusDetection.focus_evidence_sources
  security_warnings = $securityWarnings
  security_warning_count = $securityWarningSummary.security_warning_count
  high_risk_count = $securityWarningSummary.high_risk_count
  medium_risk_count = $securityWarningSummary.medium_risk_count
  low_risk_count = $securityWarningSummary.low_risk_count
  info_count = $securityWarningSummary.info_count
  suppressed_policy_mentions = $securityWarningSummary.suppressed_policy_mentions
  priority_score = $priorityEngine.priority_score
  urgency_score = $priorityEngine.urgency_score
  dependency_blocked = $priorityEngine.dependency_blocked
  safe_to_apply = $priorityEngine.safe_to_apply
  recommended_operator_action = $priorityEngine.recommended_operator_action
  stale_work_detected = $priorityEngine.stale_work_detected
  stale_work_items = $priorityEngine.stale_work_items
  unfinished_phase_count = $priorityEngine.unfinished_phase_count
  unfinished_stage_count = $priorityEngine.unfinished_stage_count
  blocked_work_count = $priorityEngine.blocked_work_count
  active_priority_lane = $priorityEngine.active_priority_lane
  work_queue = $workQueue
  current_operator_phase = "UNKNOWN"
  next_safe_action = "Review this read-only snapshot and run the work intelligence validator."
}

if ($SaveSnapshot -or $config.scanner.save_to_reports_enabled -eq $true) {
  $savedSnapshotPath = Save-DailySnapshot -Snapshot $snapshot -OutputDirectory $config.snapshot_output_directory
  Write-Host "Saved daily work intelligence snapshot: $savedSnapshotPath" -ForegroundColor Green
}

if ($SaveQueueHistory) {
  $savedQueueHistoryPath = Save-QueueHistory -Snapshot $snapshot
  Write-Host "Saved work queue history snapshot: $savedQueueHistoryPath" -ForegroundColor Green
}

if ($config.scanner.telemetry_append_enabled -eq $true) {
  $telemetryPath = Join-Path $RepoRoot $config.telemetry_output_path
  $telemetryDir = Split-Path -Parent $telemetryPath
  New-Item -ItemType Directory -Force -Path $telemetryDir | Out-Null
  $header = "timestamp,branch,total_files,total_reports,total_json_files,total_markdown_files,total_scripts,worker_lane_count,unresolved_todos,unresolved_fixmes,clean_git_status"
  if (-not (Test-Path -LiteralPath $telemetryPath)) {
    $header | Set-Content -LiteralPath $telemetryPath -Encoding UTF8
  }
  $row = @(
    $snapshot.timestamp,
    $snapshot.branch,
    $snapshot.total_files,
    $snapshot.total_reports,
    $snapshot.total_json_files,
    $snapshot.total_markdown_files,
    $snapshot.total_scripts,
    $snapshot.worker_lane_count,
    $snapshot.unresolved_todos,
    $snapshot.unresolved_fixmes,
    $snapshot.clean_git_status
  ) -join ","
  Add-Content -LiteralPath $telemetryPath -Value $row
}

if ($config.scanner.operator_briefing_enabled -eq $true) {
  $briefingPath = Join-Path $RepoRoot $config.operator_briefing_output_path
  $briefingDir = Split-Path -Parent $briefingPath
  New-Item -ItemType Directory -Force -Path $briefingDir | Out-Null
  @(
    "# AI_OS Master Operator Briefing",
    "",
    "## Repo Health Summary",
    "Clean git status: $($snapshot.clean_git_status)",
    "",
    "## Current Focus Area",
    $snapshot.current_focus_area,
    "",
    "## Active Phases",
    $snapshot.current_operator_phase,
    "",
    "## Active Worker Lanes",
    "Worker lanes detected: $($snapshot.worker_lane_count)",
    "",
    "## Blocked Items",
    "UNKNOWN",
    "",
    "## Validation Summary",
    $snapshot.validation_health,
    "",
    "## Next Safest Action",
    $snapshot.next_safe_action,
    "",
    "## Recommended Next Workload",
    $snapshot.recommended_next_workload
  ) | Set-Content -LiteralPath $briefingPath -Encoding UTF8
}

if ($GenerateBriefing) {
  $savedVoiceBriefingPath = Save-OperatorVoiceBriefing -Snapshot $snapshot -OutputDirectory "Reports/work_intelligence/briefings"
  Write-Host "Saved operator voice briefing: $savedVoiceBriefingPath" -ForegroundColor Green
}

$snapshot | ConvertTo-Json -Depth 8
