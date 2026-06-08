param(
    [ValidateSet('DRY_RUN')]
    [string]$Mode = 'DRY_RUN',
    [string]$RepoRoot = '.'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Write-Host "AI_OS Self-Build Inspector"
Write-Host "Mode: $Mode"
python automation/self_build/aios_self_build_inspector.py --mode $Mode --repo-root $RepoRoot
