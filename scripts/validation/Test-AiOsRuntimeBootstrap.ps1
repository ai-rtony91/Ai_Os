param(
  [string]$RuntimeId = "validation-runtime"
)

$ErrorActionPreference = "Stop"

$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Resolve-Path (Join-Path $ScriptRoot "..\..")
$StartScript = Join-Path $RepoRoot "scripts\runtime\Start-AiOsRuntime.ps1"
$RuntimeBootstrap = Join-Path $RepoRoot "services\runtime\runtimeBootstrap.js"
$RuntimeStateStore = Join-Path $RepoRoot "services\runtime\runtimeStateStore.js"
$PacketRestoration = Join-Path $RepoRoot "services\dispatcher\packetRestoration.js"

function Assert-True {
  param(
    [bool]$Condition,
    [string]$Message
  )

  if (-not $Condition) {
    throw $Message
  }
}

function Read-JsonFile {
  param([string]$Path)

  Assert-True (Test-Path $Path) "Expected JSON file was not created: $Path"
  return Get-Content $Path -Raw | ConvertFrom-Json
}

$ParseErrors = $null
[System.Management.Automation.PSParser]::Tokenize((Get-Content $StartScript -Raw), [ref]$ParseErrors) | Out-Null
Assert-True ($ParseErrors.Count -eq 0) "Start-AiOsRuntime.ps1 did not parse cleanly."

& node --check $RuntimeBootstrap
Assert-True ($LASTEXITCODE -eq 0) "runtimeBootstrap.js syntax check failed."

& node --check $RuntimeStateStore
Assert-True ($LASTEXITCODE -eq 0) "runtimeStateStore.js syntax check failed."

& node --check $PacketRestoration
Assert-True ($LASTEXITCODE -eq 0) "packetRestoration.js syntax check failed."

$ValidationRoot = Join-Path $env:TEMP "aios-runtime-validation-$([guid]::NewGuid().ToString('N'))"
$StateDir = Join-Path $ValidationRoot "state"
$LedgerPath = Join-Path $ValidationRoot "work_ledger.jsonl"
New-Item -ItemType Directory -Force -Path $StateDir | Out-Null
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $LedgerPath) | Out-Null

$LedgerLines = @(
  (@{
    eventId = "evt_validation_queued"
    eventType = "packet_dispatched"
    system = "AI_OS"
    source = "validation"
    summary = "Queued validation packet"
    packetId = "packet-queued"
    status = "queued"
    risk = "low"
    ts = (Get-Date).ToString("o")
  } | ConvertTo-Json -Compress),
  (@{
    eventId = "evt_validation_applied"
    eventType = "packet_applied"
    system = "AI_OS"
    source = "validation"
    summary = "Applied validation packet"
    packetId = "packet-applied"
    status = "dry_run"
    risk = "low"
    ts = (Get-Date).ToString("o")
  } | ConvertTo-Json -Compress),
  "{invalid-json"
)

$LedgerLines | Set-Content -Path $LedgerPath -Encoding UTF8

$PreviousStatePath = Join-Path $StateDir "runtime_state.json"
$PreviousState = @{
  runtimeId = $RuntimeId
  status = "running"
  updatedAt = (Get-Date).ToString("o")
} | ConvertTo-Json
[System.IO.File]::WriteAllText($PreviousStatePath, $PreviousState, [System.Text.UTF8Encoding]::new($false))

$env:AIOS_RUNTIME_STATE_DIR = $StateDir
$env:AIOS_TELEMETRY_LEDGER = $LedgerPath

Push-Location $RepoRoot
try {
  & powershell -ExecutionPolicy Bypass -File $StartScript -RuntimeId $RuntimeId -TickIntervalMs 250 -MaxTicks 2
  Assert-True ($LASTEXITCODE -eq 0) "Bounded runtime launch failed."
} finally {
  Pop-Location
}

$State = Read-JsonFile (Join-Path $StateDir "runtime_state.json")
$Heartbeat = Read-JsonFile (Join-Path $StateDir "runtime_heartbeat.json")
$CandidatePacketIds = @($State.restoration.resumeCandidates | ForEach-Object { $_.packetId })

Assert-True ($State.status -eq "shutdown") "Runtime state did not record shutdown."
Assert-True ($State.recoveredAfterInterruption -eq $true) "Runtime did not mark previous running state as recovered."
Assert-True ($State.recoveryReason -eq "previous_runtime_status_running") "Runtime did not preserve valid interrupted recovery reason."
Assert-True ($State.restoration.invalidLineCount -eq 1) "Invalid telemetry ledger line was not counted."
Assert-True ($CandidatePacketIds -contains "packet-queued") "Queued packet was not restored for resume."
Assert-True (-not ($CandidatePacketIds -contains "packet-applied")) "Applied packet was incorrectly restored for resume."
Assert-True ($Heartbeat.status -eq "shutdown") "Heartbeat did not record shutdown."
Assert-True ($Heartbeat.ledgerPath -eq $LedgerPath) "Heartbeat did not record ledger path."

$CorruptStateDir = Join-Path $ValidationRoot "corrupt-state"
New-Item -ItemType Directory -Force -Path $CorruptStateDir | Out-Null
Set-Content -Path (Join-Path $CorruptStateDir "runtime_state.json") -Value "{invalid-state" -Encoding ASCII
$env:AIOS_RUNTIME_STATE_DIR = $CorruptStateDir

Push-Location $RepoRoot
try {
  & powershell -ExecutionPolicy Bypass -File $StartScript -RuntimeId $RuntimeId -TickIntervalMs 250 -Once
  Assert-True ($LASTEXITCODE -eq 0) "Corrupt-state recovery launch failed."
} finally {
  Pop-Location
}

$CorruptRecoveryState = Read-JsonFile (Join-Path $CorruptStateDir "runtime_state.json")
Assert-True ($CorruptRecoveryState.recoveryReason -eq "invalid_runtime_state_recovered_from_telemetry") "Corrupt runtime state was not recovered from telemetry."
Assert-True ($CorruptRecoveryState.recoveryWarning.Length -gt 0) "Corrupt runtime recovery warning was not recorded."

"AI_OS runtime bootstrap validation PASS"
