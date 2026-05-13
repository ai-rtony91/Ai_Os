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

Set-Location $Repo
$Layout = Get-Content $LayoutPath -Raw | ConvertFrom-Json

Write-Host "AI_OS CONHOST CODEX LAUNCHER" -ForegroundColor Cyan
Write-Host "Layout: $($Layout.profile_name)" -ForegroundColor Cyan

foreach ($Worker in $Layout.workers) {
    $Title = "AIOS-$($Worker.number)-$($Worker.name)"

    $InnerCommand = @"
`$Host.UI.RawUI.WindowTitle = '$Title'
Set-Location '$Repo'
Write-Host '$Title' -ForegroundColor Cyan
Write-Host '$($Worker.prompt)' -ForegroundColor Yellow
codex --cd '$Repo'
"@

    $Encoded = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($InnerCommand))

    $Process = Start-Process "conhost.exe" -PassThru -ArgumentList @(
        "powershell.exe",
        "-NoExit",
        "-EncodedCommand",
        $Encoded
    )

    Start-Sleep -Seconds 2

    if ($Process.MainWindowHandle -ne 0) {
        [Win32]::MoveWindow(
            $Process.MainWindowHandle,
            [int]$Worker.x,
            [int]$Worker.y,
            [int]$Worker.width,
            [int]$Worker.height,
            $true
        ) | Out-Null
    }
}

Write-Host "AI_OS conhost Codex launch complete." -ForegroundColor Green
