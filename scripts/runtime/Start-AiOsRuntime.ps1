param(
  [string]$RuntimeId = "aios-runtime-local",
  [int]$TickIntervalMs = 5000,
  [int]$MaxTicks = 0,
  [switch]$Once
)

$ErrorActionPreference = "Stop"

$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Resolve-Path (Join-Path $ScriptRoot "..\..")
$RuntimeEntrypoint = Join-Path $RepoRoot "services\runtime\runtimeBootstrap.js"

Set-Location $RepoRoot

if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
  throw "Node.js is required to start the AI_OS runtime."
}

if (-not (Test-Path $RuntimeEntrypoint)) {
  throw "Runtime entrypoint not found: $RuntimeEntrypoint"
}

$Arguments = @(
  $RuntimeEntrypoint,
  "--runtime-id", $RuntimeId,
  "--tick-ms", $TickIntervalMs
)

if ($Once) {
  $Arguments += "--once"
}

if ($MaxTicks -gt 0) {
  $Arguments += @("--max-ticks", $MaxTicks)
}

Write-Host "[AI_OS] Starting runtime bootstrap from $RepoRoot"
Write-Host "[AI_OS] RuntimeId=$RuntimeId TickIntervalMs=$TickIntervalMs"

& node @Arguments
exit $LASTEXITCODE
