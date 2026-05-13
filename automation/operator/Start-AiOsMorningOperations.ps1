param(
  [switch]$LaunchWorkers
)

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path ".").Path

function Get-LatestPath {
  param(
    [string]$Directory,
    [string]$Filter
  )
  $fullDirectory = Join-Path $RepoRoot $Directory
  if (-not (Test-Path -LiteralPath $fullDirectory)) {
    return "UNKNOWN"
  }
  $latest = Get-ChildItem -LiteralPath $fullDirectory -File -Filter $Filter -ErrorAction SilentlyContinue |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1
  if (-not $latest) {
    return "UNKNOWN"
  }
  return $latest.FullName.Substring($RepoRoot.Length + 1)
}

Write-Host "AI_OS Morning Operations Startup" -ForegroundColor Cyan
Write-Host "Repo: $RepoRoot"
Write-Host ""

Write-Host "Running work intelligence validator..." -ForegroundColor Cyan
powershell -ExecutionPolicy Bypass -File automation/work_intelligence/Test-AiOsWorkIntelligenceScan.ps1
if ($LASTEXITCODE -ne 0) {
  throw "Work intelligence validation failed. Morning startup stopped."
}

Write-Host ""
Write-Host "Generating morning snapshot and operator voice briefing..." -ForegroundColor Cyan
powershell -ExecutionPolicy Bypass -File automation/work_intelligence/Invoke-AiOsWorkIntelligenceScan.ps1 -SaveSnapshot -GenerateBriefing
if ($LASTEXITCODE -ne 0) {
  throw "Work intelligence scan failed. Morning startup stopped."
}

$gitStatus = git status --short --branch
$latestSnapshotPath = Get-LatestPath -Directory "Reports/work_intelligence/daily" -Filter "DAILY_WORK_INTELLIGENCE_SNAPSHOT_*.json"
$latestBriefingPath = Get-LatestPath -Directory "Reports/work_intelligence/briefings" -Filter "OPERATOR_VOICE_BRIEFING_*.md"

Write-Host ""
Write-Host "Repo status:" -ForegroundColor Cyan
$gitStatus | ForEach-Object { Write-Host $_ }
Write-Host ""
Write-Host "Latest snapshot: $latestSnapshotPath"
Write-Host "Latest briefing: $latestBriefingPath"
Write-Host "Next safe action: review the latest briefing, then choose one approved DRY_RUN or APPLY task."

if ($LaunchWorkers) {
  Write-Host ""
  Write-Host "LaunchWorkers requested. Starting parallel DRY_RUN crew..." -ForegroundColor Yellow
  powershell -ExecutionPolicy Bypass -File automation/operator/Start-AiOsParallelDryRunCrew.ps1
} else {
  Write-Host ""
  Write-Host "Workers not launched. Use -LaunchWorkers to open the parallel DRY_RUN crew."
}
