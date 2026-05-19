param(
  [switch]$Force
)

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

$repoRoot = Get-AiOsRepoRoot
$processInfoPath = Join-Path $repoRoot "telemetry\runtime\runtime_process.json"

Write-Host ""
Write-Host "AI_OS RUNTIME STOP" -ForegroundColor Cyan
Write-Host "Repo: $repoRoot"
Write-Host ""

if (-not (Test-Path -LiteralPath $processInfoPath)) {
  Write-Host "No background runtime process record found." -ForegroundColor Yellow
  Write-Host "If the runtime is running in the foreground, stop it with Ctrl+C in that terminal."
  exit 0
}

try {
  $processInfo = Get-Content -LiteralPath $processInfoPath -Raw | ConvertFrom-Json
} catch {
  Write-Host "Runtime process record could not be read." -ForegroundColor Red
  Write-Host "Path: $processInfoPath"
  exit 2
}

$processId = [int]$processInfo.processId
$process = Get-Process -Id $processId -ErrorAction SilentlyContinue

if (-not $process) {
  Write-Host "Runtime process is not running." -ForegroundColor Yellow
  Write-Host "Recorded process ID: $processId"
  exit 0
}

Write-Host "Runtime process found."
Write-Host "Process ID: $processId"
Write-Host "Name:       $($process.ProcessName)"
Write-Host ""

if (-not $Force) {
  Write-Host "No stop signal sent." -ForegroundColor Yellow
  Write-Host "To stop this background runtime, rerun:"
  Write-Host "powershell -ExecutionPolicy Bypass -File scripts\control\Stop-AiOsRuntime.ps1 -Force"
  exit 0
}

Stop-Process -Id $processId -ErrorAction Stop
Write-Host "Stop signal sent to runtime process." -ForegroundColor Green
exit 0
