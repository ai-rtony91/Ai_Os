param(
  [string]$RuntimeId = "aios-runtime-local",
  [int]$TickIntervalMs = 5000,
  [int]$MaxTicks = 0,
  [switch]$Once,
  [switch]$Background,
  [switch]$RequireCleanState
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

function Get-GitChangeCount {
  param([string]$RepoRoot)

  Push-Location $RepoRoot
  try {
    $status = git status --short
    return @($status | Where-Object { $_.Trim().Length -gt 0 }).Count
  } finally {
    Pop-Location
  }
}

$repoRoot = Get-AiOsRepoRoot
$runtimeEntrypoint = Join-Path $repoRoot "services\runtime\runtimeBootstrap.js"
$runtimeStateDir = Join-Path $repoRoot "telemetry\runtime"
$processInfoPath = Join-Path $runtimeStateDir "runtime_process.json"

if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
  throw "Node.js is required to start the AI_OS runtime."
}

$changeCount = Get-GitChangeCount -RepoRoot $repoRoot
if ($RequireCleanState -and $changeCount -gt 0) {
  throw "Clean state required. Git shows $changeCount changed file(s)."
}

New-Item -ItemType Directory -Force -Path $runtimeStateDir | Out-Null

$arguments = @(
  $runtimeEntrypoint,
  "--runtime-id", $RuntimeId,
  "--tick-ms", $TickIntervalMs
)

if ($Once) {
  $arguments += "--once"
}

if ($MaxTicks -gt 0) {
  $arguments += @("--max-ticks", $MaxTicks)
}

Write-Host ""
Write-Host "AI_OS RUNTIME START" -ForegroundColor Cyan
Write-Host "Repo:        $repoRoot"
Write-Host "Runtime ID:  $RuntimeId"
Write-Host "Tick:        $TickIntervalMs ms"
Write-Host "Mode:        $(if ($Background) { 'background' } else { 'foreground' })"
Write-Host "Git changes: $changeCount"
Write-Host ""

if ($Background) {
  $stdoutPath = Join-Path $runtimeStateDir "runtime_stdout.log"
  $stderrPath = Join-Path $runtimeStateDir "runtime_stderr.log"
  $process = Start-Process `
    -FilePath "node" `
    -ArgumentList $arguments `
    -WorkingDirectory $repoRoot `
    -WindowStyle Hidden `
    -RedirectStandardOutput $stdoutPath `
    -RedirectStandardError $stderrPath `
    -PassThru

  $processInfo = [ordered]@{
    runtimeId = $RuntimeId
    processId = $process.Id
    startedAt = (Get-Date).ToUniversalTime().ToString("o")
    repoRoot = $repoRoot
    stdout = "telemetry/runtime/runtime_stdout.log"
    stderr = "telemetry/runtime/runtime_stderr.log"
  }

  $processInfo | ConvertTo-Json -Depth 5 | Set-Content -Path $processInfoPath -Encoding UTF8

  Write-Host "Started background runtime." -ForegroundColor Green
  Write-Host "Process ID:  $($process.Id)"
  Write-Host "Status:      scripts\control\Get-AiOsRuntimeStatus.ps1"
  Write-Host "Stop:        scripts\control\Stop-AiOsRuntime.ps1"
  exit 0
}

Push-Location $repoRoot
try {
  & node @arguments
  exit $LASTEXITCODE
} finally {
  Pop-Location
}
