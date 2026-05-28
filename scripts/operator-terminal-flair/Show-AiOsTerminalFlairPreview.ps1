param(
    [string]$ProfileId,

    [ValidateSet("CLEAN", "HYPE", "BOSS")]
    [string]$Mode = "HYPE",

    [switch]$All,

    [switch]$NoEmoji
)

# Shows one or all AI_OS terminal flair profile banners.
# This script calls the banner renderer only. It does not write files or edit config.

$ErrorActionPreference = "Stop"

$scriptDirectory = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Resolve-Path (Join-Path $scriptDirectory "..\..")
$registryPath = Join-Path $repoRoot "docs\AI_OS\design\terminal-flair\WORKER_PROFILE_THEME_REGISTRY_001.json"
$bannerScript = Join-Path $scriptDirectory "New-AiOsTerminalSessionBanner.ps1"

if (-not (Test-Path -LiteralPath $registryPath)) {
    Write-Error "Terminal flair registry not found: $registryPath"
    exit 1
}

if (-not (Test-Path -LiteralPath $bannerScript)) {
    Write-Error "Banner script not found: $bannerScript"
    exit 1
}

$registry = Get-Content -LiteralPath $registryPath -Raw | ConvertFrom-Json

if ($All) {
    foreach ($profile in @($registry.profiles)) {
        & $bannerScript -ProfileId $profile.profile_id -Mode $Mode -NoEmoji:$NoEmoji
        Write-Host ""
    }
    return
}

if ($ProfileId) {
    & $bannerScript -ProfileId $ProfileId -Mode $Mode -NoEmoji:$NoEmoji
    return
}

Write-Host "Choose a profile with -ProfileId or preview every profile with -All." -ForegroundColor Yellow
Write-Host "Available profiles:" -ForegroundColor Cyan
@($registry.profiles) | ForEach-Object {
    Write-Host ("- {0}" -f $_.profile_id)
}
exit 1
