Add-Type @"
using System;
using System.Runtime.InteropServices;

public class Win32 {
    [DllImport("user32.dll")]
    public static extern bool MoveWindow(IntPtr hWnd, int X, int Y, int nWidth, int nHeight, bool Repaint);
}
"@

$Repo = "C:\Dev\Ai.Os"
$LayoutPath = Join-Path $Repo "automation\operator\layout_profiles\CODEX_4_WORKER_LEFT_VERTICAL_STACK_3440x1440.json"

Set-Location $Repo
$Layout = Get-Content $LayoutPath -Raw | ConvertFrom-Json

function Move-WindowByTitle {
    param(
        [string]$Title,
        [int]$X,
        [int]$Y,
        [int]$Width,
        [int]$Height
    )

    $Target = $null

    for ($i = 0; $i -lt 60; $i++) {
        $Target = Get-Process | Where-Object {
            $_.MainWindowTitle -like "*$Title*"
        } | Select-Object -First 1

        if ($Target -and $Target.MainWindowHandle -ne 0) {
            break
        }

        Start-Sleep -Milliseconds 750
    }

    if ($Target -and $Target.MainWindowHandle -ne 0) {
        [Win32]::MoveWindow($Target.MainWindowHandle, $X, $Y, $Width, $Height, $true) | Out-Null
        Write-Host "MOVED: $Title -> X=$X Y=$Y W=$Width H=$Height" -ForegroundColor Green
    } else {
        Write-Host "FAILED TO FIND WINDOW: $Title" -ForegroundColor Red
    }
}

Write-Host "AI_OS TITLE-BASED CODEX LAUNCHER" -ForegroundColor Cyan
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

    Start-Process "conhost.exe" -ArgumentList @(
        "powershell.exe",
        "-NoExit",
        "-EncodedCommand",
        $Encoded
    )

    Start-Sleep -Seconds 4

    Move-WindowByTitle `
        -Title $Title `
        -X ([int]$Worker.x) `
        -Y ([int]$Worker.y) `
        -Width ([int]$Worker.width) `
        -Height ([int]$Worker.height)
}

Write-Host "AI_OS title-based Codex launch complete." -ForegroundColor Green
