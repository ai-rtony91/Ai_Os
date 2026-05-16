$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$registryPath = Join-Path $scriptDir 'AIOS_PATH_REGISTRY.json'
$repoRoot = (Resolve-Path -LiteralPath (Join-Path $scriptDir '..\..\..')).Path

Write-Host 'AI_OS Path Registry Validator'
Write-Host 'Mode: DRY_RUN'
Write-Host "Repo root: $repoRoot"
Write-Host "Registry: $registryPath"
Write-Host 'Safety: read-only. No files, startup tasks, scheduled tasks, dashboard files, Trading Lab files, commits, or pushes are changed.'
Write-Host ''

if (-not (Test-Path -LiteralPath $registryPath -PathType Leaf)) {
    Write-Host "FAIL registry_file $registryPath"
    exit 1
}

$registry = Get-Content -LiteralPath $registryPath -Raw | ConvertFrom-Json
$failures = @()

foreach ($entry in @($registry.required_paths)) {
    $key = [string]$entry.key
    $relativePath = [string]$entry.path
    $expectedType = [string]$entry.type
    $resolvedPath = Join-Path $repoRoot $relativePath

    $exists = switch ($expectedType) {
        'file' { Test-Path -LiteralPath $resolvedPath -PathType Leaf }
        'directory' { Test-Path -LiteralPath $resolvedPath -PathType Container }
        default { Test-Path -LiteralPath $resolvedPath }
    }

    if ($exists) {
        Write-Host "PASS $key -> $relativePath"
    } else {
        Write-Host "FAIL $key -> $relativePath"
        $failures += $key
    }
}

Write-Host ''

if ($failures.Count -gt 0) {
    Write-Host 'SUMMARY: FAIL'
    foreach ($failure in $failures) {
        Write-Host "- missing: $failure"
    }
    exit 1
}

Write-Host 'SUMMARY: PASS'
Write-Host 'Commit performed: NO'
Write-Host 'Push performed: NO'
