param(
  [int]$StaleHeartbeatMinutes = 2
)

$ErrorActionPreference = "Stop"

function Get-AiOsRepoRoot {
  $scriptRoot = Split-Path -Parent $MyInvocation.ScriptName
  $repoRoot = Resolve-Path (Join-Path $scriptRoot "..\..")

  $requiredPaths = @(
    ".git",
    "project.manifest.json",
    "automation\orchestration\queue\DISPATCHER_QUEUE.json"
  )

  foreach ($path in $requiredPaths) {
    $fullPath = Join-Path $repoRoot $path
    if (-not (Test-Path -LiteralPath $fullPath)) {
      throw "AI_OS repo validation failed. Missing: $path"
    }
  }

  return $repoRoot.Path
}

function Read-JsonFile {
  param([string]$Path)

  if (-not (Test-Path -LiteralPath $Path)) {
    return $null
  }

  return Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json
}

function Test-JsonLines {
  param([string]$Path)

  $result = [ordered]@{
    exists = (Test-Path -LiteralPath $Path)
    events = 0
    invalid = 0
  }

  if (-not $result.exists) {
    return $result
  }

  foreach ($line in Get-Content -LiteralPath $Path) {
    if ($line.Trim().Length -eq 0) {
      continue
    }

    try {
      $null = $line | ConvertFrom-Json
      $result.events += 1
    } catch {
      $result.invalid += 1
    }
  }

  return $result
}

$repoRoot = Get-AiOsRepoRoot
$runtimeStatePath = Join-Path $repoRoot "telemetry\runtime\runtime_state.json"
$heartbeatPath = Join-Path $repoRoot "telemetry\runtime\runtime_heartbeat.json"
$ledgerPath = Join-Path $repoRoot "telemetry\work_ledger.jsonl"
$queuePath = Join-Path $repoRoot "automation\orchestration\queue\DISPATCHER_QUEUE.json"

$state = Read-JsonFile -Path $runtimeStatePath
$heartbeat = Read-JsonFile -Path $heartbeatPath
$queue = Read-JsonFile -Path $queuePath
$ledger = Test-JsonLines -Path $ledgerPath

$items = @($queue.items)
$readyCount = @($items | Where-Object { $_.status -eq "READY" }).Count
$assignedCount = @($items | Where-Object { $_.status -eq "ASSIGNED" }).Count
$doneCount = @($items | Where-Object { $_.status -eq "DONE" }).Count
$problems = New-Object System.Collections.Generic.List[string]

if (-not $state) {
  $problems.Add("Runtime state file is missing.")
} elseif ($state.status -in @("blocked", "degraded", "failed")) {
  $problems.Add("Runtime state is $($state.status).")
}

if (-not $heartbeat) {
  $problems.Add("Runtime heartbeat file is missing.")
} else {
  $heartbeatAt = [DateTimeOffset]::Parse($heartbeat.heartbeatAt)
  $ageMinutes = ([DateTimeOffset]::UtcNow - $heartbeatAt.ToUniversalTime()).TotalMinutes
  if ($ageMinutes -gt $StaleHeartbeatMinutes) {
    $problems.Add("Runtime heartbeat is stale: $([math]::Round($ageMinutes, 1)) minutes old.")
  }
}

if ($ledger.invalid -gt 0) {
  $problems.Add("Telemetry ledger has $($ledger.invalid) invalid line(s).")
}

$health = if ($problems.Count -eq 0) { "OK" } elseif ($problems.Count -le 2) { "WARN" } else { "ACTION NEEDED" }
$healthColor = if ($health -eq "OK") { "Green" } elseif ($health -eq "WARN") { "Yellow" } else { "Red" }

Write-Host ""
Write-Host "AI_OS RUNTIME HEALTH" -ForegroundColor Cyan
Write-Host "Repo: $repoRoot"
Write-Host ""
Write-Host "Overall: $health" -ForegroundColor $healthColor
Write-Host ""

Write-Host "Runtime" -ForegroundColor Yellow
Write-Host "  Status:    $(if ($state) { $state.status } else { 'UNKNOWN' })"
Write-Host "  Heartbeat: $(if ($heartbeat) { $heartbeat.heartbeatAt } else { 'MISSING' })"

Write-Host ""
Write-Host "Queue" -ForegroundColor Yellow
Write-Host "  READY:     $readyCount"
Write-Host "  ASSIGNED:  $assignedCount"
Write-Host "  DONE:      $doneCount"

Write-Host ""
Write-Host "Telemetry" -ForegroundColor Yellow
Write-Host "  Ledger:    $(if ($ledger.exists) { 'found' } else { 'missing' })"
Write-Host "  Events:    $($ledger.events)"
Write-Host "  Invalid:   $($ledger.invalid)"

if ($problems.Count -gt 0) {
  Write-Host ""
  Write-Host "Operator action" -ForegroundColor Yellow
  foreach ($problem in $problems) {
    Write-Host "  $problem"
  }
}

exit 0
