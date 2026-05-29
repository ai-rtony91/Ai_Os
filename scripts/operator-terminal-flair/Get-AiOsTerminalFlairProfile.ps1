param(
    [Parameter(Mandatory = $true)]
    [string]$ProfileId
)

# Reads the repo-contained terminal flair registry and returns one profile object.
# This script does not write files and does not edit Windows Terminal or PowerShell profiles.

$ErrorActionPreference = "Stop"

$scriptDirectory = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Resolve-Path (Join-Path $scriptDirectory "..\..")
$registryPath = Join-Path $repoRoot "docs\AI_OS\design\terminal-flair\WORKER_PROFILE_THEME_REGISTRY_001.json"

if (-not (Test-Path -LiteralPath $registryPath)) {
    Write-Error "Terminal flair registry not found: $registryPath"
    exit 1
}

$registry = Get-Content -LiteralPath $registryPath -Raw | ConvertFrom-Json
$normalizedProfileId = $ProfileId.Trim().ToUpperInvariant()
$profile = @($registry.profiles) | Where-Object { $_.profile_id -eq $normalizedProfileId } | Select-Object -First 1

if (-not $profile) {
    Write-Host "Profile not found: $ProfileId" -ForegroundColor Yellow
    Write-Host "Available profiles:" -ForegroundColor Cyan
    @($registry.profiles) | ForEach-Object {
        Write-Host ("- {0}" -f $_.profile_id)
    }
    exit 1
}

$profile
