param(
    [string]$Profile = "CODEX_08"
)

Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Win32 {
    [DllImport("user32.dll")]
    public static extern bool MoveWindow(IntPtr hWnd, int X, int Y, int nWidth, int nHeight, bool Repaint);
}
"@

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

Write-Host "AI_OS MULTI-CODEX LAUNCHER v2" -ForegroundColor Cyan
Write-Host "Profile: $Profile" -ForegroundColor Cyan
Write-Host "Layout: $($Layout.profile_name)" -ForegroundColor Cyan

foreach ($Worker in $Layout.workers) {
    $Title = "AIOS-$($Worker.number)"

    $InnerCommand = @"
`$Host.UI.RawUI.WindowTitle = '$Title'
Set-Location '$Repo'
Write-Host '$Title - $($Worker.role)' -ForegroundColor Cyan
Write-Host '$($Worker.prompt)' -ForegroundColor Yellow
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

    for ($i = 0; $i -lt 30; $i++) {
        if ($Process.MainWindowHandle -ne 0) { break }
        Start-Sleep -Milliseconds 250
    }

    if ($Process.MainWindowHandle -ne 0) {
        [Win32]::MoveWindow(
            $Process.MainWindowHandle,
            [int]$Worker.x,
            [int]$Worker.y,
            [int]$Worker.width,
            [int]$Worker.height,
            $true
        ) | Out-Null
        Write-Host "MOVED $Title to X=$($Worker.x) Y=$($Worker.y)" -ForegroundColor Green
    } else {
        Write-Host "WARN: could not move $Title" -ForegroundColor Yellow
    }

    Start-Sleep -Milliseconds 700
}

Write-Host "AI_OS multi-Codex launch complete." -ForegroundColor Green
