param(
    [string]$Profile = "LEFT_VERTICAL"
)

$Repo = "C:\Users\mylab\OneDrive\GitHub\ai-rtony91_Ai_Os_CLEAN"

$Profiles = @{
    "LEFT_VERTICAL" = "automation\operator\layout_profiles\CODEX_4_WORKER_LEFT_VERTICAL_STACK_3440x1440.json"
    "LEFT_2X2"      = "automation\operator\layout_profiles\CODEX_4_WORKER_LEFT_2X2_3440x1440.json"
}

if (!(Test-Path $Repo)) {
    Write-Host "BLOCKED: Canonical repo missing." -ForegroundColor Red
    exit 1
}

if (!$Profiles.ContainsKey($Profile)) {
    Write-Host "BLOCKED: Unknown profile: $Profile" -ForegroundColor Red
    Write-Host "Available profiles:" -ForegroundColor Yellow
    $Profiles.Keys
    exit 1
}

Set-Location $Repo

$LayoutPath = Join-Path $Repo $Profiles[$Profile]

if (!(Test-Path $LayoutPath)) {
    Write-Host "BLOCKED: Layout file missing: $LayoutPath" -ForegroundColor Red
    exit 1
}

$Layout = Get-Content $LayoutPath -Raw | ConvertFrom-Json

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "AI_OS CODEX PROFILE LAUNCHER" -ForegroundColor Cyan
Write-Host "Profile: $Profile" -ForegroundColor Cyan
Write-Host "Layout:  $($Layout.profile_name)" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

git status --short --branch

foreach ($Worker in $Layout.workers) {
    $Title = "AIOS-$($Worker.number)-$($Worker.name)"

    $Command = @"
`$Host.UI.RawUI.WindowTitle = '$Title'
Set-Location '$Repo'
Write-Host ''
Write-Host '$Title' -ForegroundColor Cyan
Write-Host '$($Worker.prompt)' -ForegroundColor Yellow
Write-Host ''
codex --cd '$Repo'
"@

    Start-Process powershell -ArgumentList @(
        "-NoExit",
        "-Command",
        $Command
    )

    Start-Sleep -Milliseconds 700
}

Write-Host ""
Write-Host "AI_OS Codex profile launch complete." -ForegroundColor Green
Write-Host "NOTE: If windows need exact placement, use saved layout profile values as the reference." -ForegroundColor Yellow
