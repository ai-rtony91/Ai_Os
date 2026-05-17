param(
    [Parameter(Mandatory = $true)]
    [string]$Marker
)

try {
    [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
    $OutputEncoding = [Console]::OutputEncoding
} catch {
    # Older hosts may reject output encoding changes; the marker still works.
}

$repoPath = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$registryPath = Join-Path $PSScriptRoot 'AIOS_WORKER_REGISTRY.json'

if (-not (Test-Path -LiteralPath $registryPath)) {
    throw "Worker registry not found: $registryPath"
}

$registry = Get-Content -LiteralPath $registryPath -Raw | ConvertFrom-Json
$identity = $registry.workers | Where-Object { $_.marker -eq $Marker -and $_.enabled -eq $true } | Select-Object -First 1

if (-not $identity) {
    $enabledMarkers = @($registry.workers | Where-Object { $_.enabled -eq $true } | ForEach-Object { $_.marker })
    throw "Unknown or disabled AI_OS worker marker '$Marker'. Enabled markers: $($enabledMarkers -join ', ')"
}

$windowTitle = "$($identity.emoji) $($identity.title)"
$Host.UI.RawUI.WindowTitle = $windowTitle

$bannerWidth = 100
try {
    if ($Host.UI.RawUI.WindowSize.Width -gt 0) {
        $bannerWidth = [Math]::Max(60, [Math]::Min(160, $Host.UI.RawUI.WindowSize.Width))
    }
} catch {
    $bannerWidth = 100
}

$divider = '=' * $bannerWidth

Write-Host ''
Write-Host $divider -ForegroundColor $identity.color
Write-Host $windowTitle -ForegroundColor $identity.color
Write-Host $divider -ForegroundColor $identity.color
Write-Host "Role: $($identity.role)"
Write-Host "Repo path: $repoPath"
Write-Host ''
Write-Host 'Allowed actions:' -ForegroundColor $identity.color
foreach ($item in $identity.allowedActions) {
    Write-Host "  - $item"
}
Write-Host ''
Write-Host 'Blocked actions:' -ForegroundColor $identity.color
foreach ($item in $identity.blockedActions) {
    Write-Host "  - $item"
}
Write-Host ''
Write-Host 'Next command hint:' -ForegroundColor $identity.color
Write-Host "  $($identity.nextCommand)"
Write-Host ''
Write-Host 'Safety: repo-scoped marker only. No files, tasks, apps, brokers, keys, or trades are touched.'
Write-Host ''
