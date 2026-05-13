Add-Type @"
using System;
using System.Runtime.InteropServices;

public class Win32 {
    [DllImport("user32.dll")]
    public static extern bool MoveWindow(IntPtr hWnd, int X, int Y, int nWidth, int nHeight, bool Repaint);
}
"@

$Repo = "C:\Users\mylab\OneDrive\GitHub\ai-rtony91_Ai_Os_CLEAN"
$LayoutPath = Join-Path $Repo "automation\operator\layout_profiles\CODEX_4_WORKER_LEFT_VERTICAL_STACK_3440x1440.json"

if (!(Test-Path $Repo)) {
    Write-Host "BLOCKED: Canonical repo missing." -ForegroundColor Red
    exit 1
}

if (!(Test-Path $LayoutPath)) {
    Write-Host "BLOCKED: Layout profile missing." -ForegroundColor Red
    exit 1
}

Set-Location $Repo

$Layout = Get-Content $LayoutPath -Raw | ConvertFrom-Json

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "AI_OS CODEX WORKER LAUNCHER v1" -ForegroundColor Cyan
Write-Host "Layout: $($Layout.profile_name)" -ForegroundColor Cyan
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

    $Process = Start-Process powershell -PassThru -ArgumentList @(
        "-NoExit",
        "-Command",
        $Command
    )

    Start-Sleep -Seconds 3

    $Handle = $Process.MainWindowHandle

    if ($Handle -ne 0) {
        [Win32]::MoveWindow(
            $Handle,
            [int]$Worker.x,
            [int]$Worker.y,
            [int]$Worker.width,
            [int]$Worker.height,
            $true
        ) | Out-Null
    }
}

Write-Host ""
Write-Host "AI_OS Codex worker launch complete." -ForegroundColor Green
