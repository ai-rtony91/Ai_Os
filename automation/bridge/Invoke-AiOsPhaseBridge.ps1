param(
    [ValidateSet('DRY_RUN')]
    [string]$Mode = 'DRY_RUN',
    [string]$RepoRoot = '.'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Write-Host "AI_OS Phase Bridge"
Write-Host "Mode: $Mode"
Write-Host "Repo root: $RepoRoot"
python automation/bridge/aios_phase_bridge.py --mode $Mode --repo-root $RepoRoot
