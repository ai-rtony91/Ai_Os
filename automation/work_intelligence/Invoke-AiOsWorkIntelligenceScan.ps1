param(
  [string]$ConfigPath = "automation/work_intelligence/AIOS_WORK_INTELLIGENCE_CONFIG.json",
  [switch]$SaveSnapshot
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
  current_focus_area = "UNKNOWN"
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
    "Review the generated work intelligence snapshot."
  ) | Set-Content -LiteralPath $briefingPath -Encoding UTF8
}

$snapshot | ConvertTo-Json -Depth 8
