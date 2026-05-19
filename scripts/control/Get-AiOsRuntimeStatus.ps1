param()

$ErrorActionPreference = "Stop"

function Get-AiOsRepoRoot {
  $scriptRoot = Split-Path -Parent $MyInvocation.ScriptName
  $repoRoot = Resolve-Path (Join-Path $scriptRoot "..\..")

  $requiredPaths = @(
    ".git",
    "project.manifest.json",
    "services\runtime\runtimeBootstrap.js"
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

function Format-Value {
  param($Value, [string]$Fallback = "UNKNOWN")

  if ($null -eq $Value -or "$Value".Trim().Length -eq 0) {
    return $Fallback
  }

  return $Value
}

$repoRoot = Get-AiOsRepoRoot
$runtimeStatePath = Join-Path $repoRoot "telemetry\runtime\runtime_state.json"
$heartbeatPath = Join-Path $repoRoot "telemetry\runtime\runtime_heartbeat.json"
$processInfoPath = Join-Path $repoRoot "telemetry\runtime\runtime_process.json"

$state = Read-JsonFile -Path $runtimeStatePath
$heartbeat = Read-JsonFile -Path $heartbeatPath
$processInfo = Read-JsonFile -Path $processInfoPath

Write-Host ""
Write-Host "AI_OS RUNTIME STATUS" -ForegroundColor Cyan
Write-Host "Repo: $repoRoot"
Write-Host ""

Write-Host "Runtime" -ForegroundColor Yellow
if ($state) {
  Write-Host "  Runtime ID:     $(Format-Value $state.runtimeId)"
  Write-Host "  Status:         $(Format-Value $state.status)"
  Write-Host "  Booted at:      $(Format-Value $state.bootedAt)"
  Write-Host "  Updated at:     $(Format-Value $state.updatedAt)"
  Write-Host "  Tick count:     $(Format-Value $state.tickCount '0')"
  Write-Host "  Recovered:      $(Format-Value $state.recoveredAfterInterruption)"
} else {
  Write-Host "  Runtime has not written state yet." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Heartbeat" -ForegroundColor Yellow
if ($heartbeat) {
  Write-Host "  Runtime ID:     $(Format-Value $heartbeat.runtimeId)"
  Write-Host "  Status:         $(Format-Value $heartbeat.status)"
  Write-Host "  Heartbeat at:   $(Format-Value $heartbeat.heartbeatAt)"
  Write-Host "  Tick count:     $(Format-Value $heartbeat.tickCount '0')"
} else {
  Write-Host "  Runtime heartbeat not found." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Process" -ForegroundColor Yellow
if ($processInfo) {
  $process = Get-Process -Id ([int]$processInfo.processId) -ErrorAction SilentlyContinue
  Write-Host "  Process ID:     $(Format-Value $processInfo.processId)"
  Write-Host "  Background:     yes"
  Write-Host "  Running:        $(if ($process) { 'yes' } else { 'no' })"
} else {
  Write-Host "  Background process record not found."
}

exit 0
