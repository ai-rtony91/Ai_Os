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

Write-Host "AI_OS Parallel DRY_RUN Crew Launcher" -ForegroundColor Cyan
Write-Host "Repo: $RepoRoot"
Write-Host "Codex command: UNKNOWN. Add the local Codex command later where marked."
Write-Host ""

foreach ($worker in $registry.workers) {
  $title = "AI_OS DRY_RUN Worker $($worker.id) - $($worker.label)"
  $lane = $worker.lane
  $reportPath = $worker.report_path
  $workerId = $worker.id
  $workerLabel = $worker.label

  Write-Host ("Opening Worker {0}: {1} :: {2}" -f $workerId, $workerLabel, $lane)

  $windowScript = @"
`$Host.UI.RawUI.WindowTitle = '$title'
Set-Location -LiteralPath '$RepoRoot'
Write-Host 'AI_OS PARALLEL DRY_RUN WORKER' -ForegroundColor Cyan
Write-Host 'Worker: #$workerId $workerLabel'
Write-Host 'Lane: $lane'
Write-Host 'Mode: DRY_RUN only. Do not edit files.'
Write-Host 'Report target: $reportPath'
Write-Host ''
Write-Host 'Required worker output JSON fields: worker_id, label, mode, files_planned, files_deleted, validation_commands, summary.'
Write-Host ''
Write-Host 'Codex command placeholder: UNKNOWN'
Write-Host 'Later, add the approved local Codex command here after operator confirmation.'
Write-Host ''
Write-Host 'Stop condition: produce a DRY_RUN report only. No APPLY, no commit, no push.'
Read-Host 'Press Enter to close this worker window'
"@

  Start-Process powershell -ArgumentList @("-NoExit", "-Command", $windowScript)
}

Write-Host ""
Write-Host "Launched $($registry.workers.Count) labeled PowerShell worker windows."
Write-Host "No Codex CLI command was assumed or executed."
