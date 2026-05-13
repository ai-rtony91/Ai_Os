param(
  [string]$ConfigPath = "automation/work_intelligence/AIOS_WORK_INTELLIGENCE_CONFIG.json",
  [switch]$SaveSnapshot,
  [switch]$GenerateBriefing
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
    [string]$Path
  )
  $Warnings.Add([pscustomobject]@{
    warning_type = $Type
    path = $Path
  }) | Out-Null
}

function Get-SecurityWarnings {
  param(
    [object[]]$Files,
    [string]$GitStatusText,
    [string[]]$ProtectedFiles
  )
  $warnings = New-Object System.Collections.Generic.List[object]
  $textExtensions = @(".ps1", ".json", ".md", ".txt", ".csv", ".yml", ".yaml", ".js", ".html", ".css")
  foreach ($file in @($Files)) {
    $relative = Get-RelativePath -Item $file
    if ($relative -match "(^|/)\.env($|\.|/)") {
      Add-SecurityWarning -Warnings $warnings -Type ".env file present" -Path $relative
    }
    if ($textExtensions -notcontains $file.Extension.ToLowerInvariant()) {
      continue
    }
    $content = Get-Content -LiteralPath $file.FullName -Raw -ErrorAction SilentlyContinue
    if ([string]::IsNullOrWhiteSpace($content)) {
      continue
    }
    if ($content -match "(?i)api[_ -]?key") {
      Add-SecurityWarning -Warnings $warnings -Type "API key wording" -Path $relative
    }
    if ($content -match "(?i)\b(secret|token|password)\b") {
      Add-SecurityWarning -Warnings $warnings -Type "secret/token/password wording" -Path $relative
    }
    if ($content -match "(?i)\b(broker|oanda|live execution)\b") {
      Add-SecurityWarning -Warnings $warnings -Type "broker/OANDA/live execution wording" -Path $relative
    }
    if ($content -match "(?i)git\s+add\s+\.") {
      Add-SecurityWarning -Warnings $warnings -Type "git add dot wording" -Path $relative
    }
    if ($content -match "(?i)\b(rm\s+-rf|remove-item\s+-recurse|git\s+reset\s+--hard|del\s+/s)\b") {
      Add-SecurityWarning -Warnings $warnings -Type "destructive command wording" -Path $relative
    }
  }

  foreach ($line in @($GitStatusText -split "`r?`n")) {
    if (-not $line -or $line.Length -lt 4) { continue }
    $path = ($line.Substring(3).Trim() -replace "\\", "/")
    foreach ($protected in $ProtectedFiles) {
      if ($path -ieq ($protected -replace "\\", "/")) {
        Add-SecurityWarning -Warnings $warnings -Type "protected root file change" -Path $path
      }
    }
  }

  return @($warnings | Sort-Object warning_type, path -Unique)
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
$registryPath = Join-Path $RepoRoot $config.worker_registry_path
if (Test-Path -LiteralPath $registryPath) {
  $registry = Get-Content -LiteralPath $registryPath -Raw | ConvertFrom-Json
  $workerLaneCount = @($registry.workers).Count
}
$workerReportDir = Join-Path $RepoRoot $config.worker_report_directory
if (Test-Path -LiteralPath $workerReportDir) {
  $workerReportPresence = "PRESENT"
  $workerReportCount = @(Get-ChildItem -LiteralPath $workerReportDir -File -Filter "*.json" -ErrorAction SilentlyContinue).Count
} else {
  $workerReportPresence = "MISSING"
}

$latestCheckpointRefs = Get-LatestFileRefs -Roots @($config.checkpoint_roots)
$latestReportRefs = Get-LatestFileRefs -Roots @($config.report_roots)
$latestCheckpointReference = if (@($latestCheckpointRefs).Count -gt 0) { $latestCheckpointRefs[0].path } else { "UNKNOWN" }
$cleanGitStatus = [string]::IsNullOrWhiteSpace($gitStatusShort)
$unresolvedTodos = Count-Marker "TODO"
$unresolvedFixmes = Count-Marker "FIXME"
$recentFiles = @($allFiles | Where-Object { $_.FullName -notmatch "\\.git\\" } | Sort-Object LastWriteTime -Descending | Select-Object -First 25)
$focusDetection = Get-FocusDetection -RecentFiles $recentFiles -CheckpointRefs $latestCheckpointRefs -ReportRefs $latestReportRefs -TodoCount $unresolvedTodos
$securityWarnings = Get-SecurityWarnings -Files $allFiles -GitStatusText $gitStatusShort -ProtectedFiles @($config.protected_files)

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
  worker_report_count = $workerReportCount
  unresolved_todos = $unresolvedTodos
  unresolved_fixmes = $unresolvedFixmes
  unresolved_todo_markers = $unresolvedTodos
  unresolved_fixme_markers = $unresolvedFixmes
  worker_report_presence = $workerReportPresence
  validation_health = "UNKNOWN_UNTIL_VALIDATOR_RUN"
  latest_checkpoint_reference = $latestCheckpointReference
  latest_checkpoint_references = $latestCheckpointRefs
  latest_report_references = $latestReportRefs
  current_focus_area = $focusDetection.current_focus_area
  active_subsystem = $focusDetection.active_subsystem
  recommended_next_workload = $focusDetection.recommended_next_workload
  focus_evidence_sources = $focusDetection.focus_evidence_sources
  security_warnings = $securityWarnings
  current_operator_phase = "UNKNOWN"
  next_safe_action = "Review this read-only snapshot and run the work intelligence validator."
}

if ($SaveSnapshot -or $config.scanner.save_to_reports_enabled -eq $true) {
  $savedSnapshotPath = Save-DailySnapshot -Snapshot $snapshot -OutputDirectory $config.snapshot_output_directory
  Write-Host "Saved daily work intelligence snapshot: $savedSnapshotPath" -ForegroundColor Green
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
