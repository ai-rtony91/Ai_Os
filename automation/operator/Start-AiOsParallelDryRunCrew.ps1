param(
  [string]$RegistryPath = "automation/operator/AIOS_PARALLEL_WORKER_REGISTRY.json"
)

$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path ".").Path
$RegistryFullPath = Join-Path $RepoRoot $RegistryPath

if (-not (Test-Path -LiteralPath $RegistryFullPath)) {
  throw "Registry not found: $RegistryFullPath"
}

$registry = Get-Content -LiteralPath $RegistryFullPath -Raw | ConvertFrom-Json
$codexLaunch = $registry.codex_launch
$codexLaunchEnabled = $codexLaunch -and $codexLaunch.enabled -eq $true -and $codexLaunch.command -and $codexLaunch.command -ne "UNKNOWN"

Write-Host "AI_OS Parallel DRY_RUN Crew Launcher" -ForegroundColor Cyan
Write-Host "Repo: $RepoRoot"
if ($codexLaunchEnabled) {
  Write-Host "Codex launch: ENABLED via registry command."
} else {
  Write-Host "Codex launch: instruction-window fallback. Command is unavailable, disabled, or UNKNOWN."
}
Write-Host ""

foreach ($worker in $registry.workers) {
  $title = "AI_OS DRY_RUN Worker $($worker.id) - $($worker.label)"
  $lane = $worker.lane
  $reportPath = $worker.report_path
  $workerId = $worker.id
  $workerLabel = $worker.label
  $allowedPaths = @($worker.allowed_paths) -join ", "
  $blockedPaths = @($worker.blocked_paths) -join ", "
  $promptSeed = $worker.codex_prompt_seed
  $codexCommand = if ($codexLaunch.command) { $codexLaunch.command } else { "UNKNOWN" }
  $codexArgumentsJson = @($codexLaunch.arguments) | ConvertTo-Json -Compress
  $codexPromptArgumentName = if ($codexLaunch.prompt_argument_name) { $codexLaunch.prompt_argument_name } else { "UNKNOWN" }
  $dryRunPrompt = @"
AI_OS PARALLEL DRY_RUN WORKER
Worker: #$workerId $workerLabel
Lane: $lane
Allowed paths: $allowedPaths
Blocked paths: $blockedPaths
Mode: DRY_RUN only. Do not edit files.
Report target: $reportPath
Rules:
- Inspect only the assigned lane.
- Produce DRY_RUN findings only.
- List planned files and validation commands.
- Do not APPLY.
- Do not commit.
- Do not push.
- Do not touch protected root files.
Prompt seed:
$promptSeed
"@

  Write-Host ("Opening Worker {0}: {1} :: {2}" -f $workerId, $workerLabel, $lane)

  $windowScript = @"
`$Host.UI.RawUI.WindowTitle = '$title'
Set-Location -LiteralPath '$RepoRoot'
Write-Host 'AI_OS PARALLEL DRY_RUN WORKER' -ForegroundColor Cyan
Write-Host 'Worker: #$workerId $workerLabel'
Write-Host 'Lane: $lane'
Write-Host 'Allowed paths: $allowedPaths'
Write-Host 'Blocked paths: $blockedPaths'
Write-Host 'Mode: DRY_RUN only. Do not edit files.'
Write-Host 'Report target: $reportPath'
Write-Host ''
Write-Host 'DRY_RUN rules: inspect only assigned lane; no edits; no APPLY; no commit; no push; no protected root files.'
Write-Host 'Required worker output JSON fields: worker_id, label, mode, files_planned, files_deleted, validation_commands, summary.'
Write-Host ''
Write-Host 'Codex prompt seed:'
Write-Host @'
$promptSeed
'@
Write-Host ''
if ('$codexLaunchEnabled' -eq 'True') {
  `$codexCommand = '$codexCommand'
  `$codexArgsJson = @'
$codexArgumentsJson
'@
  `$codexArgs = @(`$codexArgsJson | ConvertFrom-Json)
  `$promptArgumentName = '$codexPromptArgumentName'
  `$workerPrompt = @'
$dryRunPrompt
'@
  if (`$promptArgumentName -and `$promptArgumentName -ne 'UNKNOWN') {
    `$codexArgs += @(`$promptArgumentName, `$workerPrompt)
  } else {
    `$env:AIOS_CODEX_WORKER_PROMPT = `$workerPrompt
  }
  if (Get-Command `$codexCommand -ErrorAction SilentlyContinue) {
    Write-Host 'Launching configured Codex command from registry.' -ForegroundColor Green
    & `$codexCommand @codexArgs
  } else {
    Write-Host 'Configured Codex command was not found. Instruction-window fallback remains active.' -ForegroundColor Yellow
    Write-Host 'Worker prompt is available in AIOS_CODEX_WORKER_PROMPT if prompt_argument_name is UNKNOWN.'
  }
} else {
  Write-Host 'Codex command unavailable or disabled. Instruction-window fallback is active.'
}
Write-Host ''
Write-Host 'Stop condition: produce a DRY_RUN report only. No APPLY, no commit, no push.'
Read-Host 'Press Enter to close this worker window'
"@

  Start-Process powershell -ArgumentList @("-NoExit", "-Command", $windowScript)

  if ($codexLaunchEnabled) {
    Write-Host "Configured Codex launch is enabled for worker #$workerId. Command is read from registry."
    Write-Host "Prompt prepared for worker #${workerId}:"
    Write-Host $dryRunPrompt
  }
}

Write-Host ""
Write-Host "Launched $($registry.workers.Count) labeled PowerShell worker windows."
if ($codexLaunchEnabled) {
  Write-Host "Codex command is configured but not hardcoded by this script."
} else {
  Write-Host "No Codex command was assumed or executed."
}
