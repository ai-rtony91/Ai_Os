param(
    [ValidateSet('DRY_RUN', 'APPLY')]
    [string]$Mode = 'DRY_RUN'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$RepoRoot = (git rev-parse --show-toplevel).Trim()
$Source = Join-Path $RepoRoot '.githooks/pre-commit'
$TargetDir = Join-Path $RepoRoot '.git/hooks'
$Target = Join-Path $TargetDir 'pre-commit'

Write-Host "AI_OS hook installer"
Write-Host "Mode: $Mode"
Write-Host "Source: $Source"
Write-Host "Target: $Target"

if (!(Test-Path $Source)) {
    throw "Hook template missing: $Source"
}

if ($Mode -eq 'DRY_RUN') {
    Write-Host "DRY_RUN only. No hook installed."
    if (Test-Path $Target) {
        Write-Host "Existing pre-commit hook detected. APPLY would require review before overwrite."
    }
    exit 0
}

if (Test-Path $Target) {
    throw "Existing pre-commit hook detected. Back it up manually after review before APPLY."
}

Copy-Item -LiteralPath $Source -Destination $Target
Write-Host "Installed AI_OS pre-commit hook."
