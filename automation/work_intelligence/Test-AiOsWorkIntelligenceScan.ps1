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
  "docs/AI_OS/work_intelligence/AIOS_WORK_INTELLIGENCE_ARCHITECTURE.md"
)

$requiredFolders = @(
  "automation/work_intelligence",
  "Reports/work_intelligence",
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
}

if ($failures.Count -gt 0) {
  Write-Host ""
  Write-Host "AI_OS WORK INTELLIGENCE VALIDATION: FAIL" -ForegroundColor Red
  exit 1
}

Write-Host ""
Write-Host "AI_OS WORK INTELLIGENCE VALIDATION: PASS" -ForegroundColor Green
exit 0
