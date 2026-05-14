param(
    [string]$Profile = "CODEX_08"
)

$Repo = "C:\Users\mylab\OneDrive\GitHub\ai-rtony91_Ai_Os_CLEAN"

$Profiles = @{
    "CODEX_06" = "automation\operator\layout_profiles\CODEX_06_GRID_3440x1440.json"
    "CODEX_08" = "automation\operator\layout_profiles\CODEX_08_GRID_3440x1440.json"
    "CODEX_10" = "automation\operator\layout_profiles\CODEX_10_SIDE_RAILS_3440x1440.json"
}

if (!(Test-Path $Repo)) { Write-Host "BLOCKED: repo missing." -ForegroundColor Red; exit 1 }
if (!$Profiles.ContainsKey($Profile)) { Write-Host "BLOCKED: bad profile. Use CODEX_06, CODEX_08, or CODEX_10." -ForegroundColor Red; exit 1 }

Set-Location $Repo
$LayoutPath = Join-Path $Repo $Profiles[$Profile]
$Layout = Get-Content $LayoutPath -Raw | ConvertFrom-Json

Write-Host "AI_OS WORKER LAUNCHER" -ForegroundColor Cyan
Write-Host "Worker set: $Profile" -ForegroundColor Cyan
Write-Host "Window plan: $($Layout.profile_name)" -ForegroundColor Cyan

foreach ($Worker in $Layout.workers) {
    $Title = "AIOS-$($Worker.number)"

    $InnerCommand = @"
`$Host.UI.RawUI.WindowTitle = '$Title'
Set-Location '$Repo'
Write-Host '$Title - $($Worker.role)' -ForegroundColor Cyan
Write-Host '$($Worker.prompt)' -ForegroundColor Yellow
powershell -ExecutionPolicy Bypass -File 'automation\operator\Start-AIOSWorkerQueueRunner.ps1' -WorkerId '$Title'
Start-Sleep -Seconds 5
codex --cd '$Repo'
"@

    $Encoded = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($InnerCommand))

    $Process = Start-Process "conhost.exe" -PassThru -ArgumentList @(
        "powershell.exe",
        "-NoExit",
        "-EncodedCommand",
        $Encoded
    )

    Write-Host "Opened $Title" -ForegroundColor Green

    Start-Sleep -Milliseconds 700
}

Write-Host "AI_OS worker launch complete." -ForegroundColor Green
