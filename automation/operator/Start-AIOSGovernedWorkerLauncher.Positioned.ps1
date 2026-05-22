Add-Type @"
using System;
using System.Runtime.InteropServices;

public class Win32 {
    [DllImport("user32.dll")]
    public static extern bool MoveWindow(IntPtr hWnd, int X, int Y, int nWidth, int nHeight, bool Repaint);
}
"@

$Repo = "C:\Dev\Ai.Os"

if (!(Test-Path $Repo)) {
    Write-Host "BLOCKED: Canonical repo path missing." -ForegroundColor Red
    exit 1
}

Set-Location $Repo

$Workers = @(
    @{
        Number = "01"
        Name = "DEVOPS"
        X = 0
        Y = 0
        Width = 1720
        Height = 720
        Message = "DEVOPS worker ready."
    },
    @{
        Number = "02"
        Name = "TRADING_LAB"
        X = 1720
        Y = 0
        Width = 1720
        Height = 720
        Message = "TRADING LAB worker ready. Paper-only."
    },
    @{
        Number = "03"
        Name = "VALIDATOR"
        X = 0
        Y = 720
        Width = 1720
        Height = 720
        Message = "VALIDATOR worker ready."
    },
    @{
        Number = "04"
        Name = "TELEMETRY"
        X = 1720
        Y = 720
        Width = 1720
        Height = 720
        Message = "TELEMETRY worker ready."
    }
)

foreach ($Worker in $Workers) {

    $Title = "AIOS-$($Worker.Number)-$($Worker.Name)"

    $Process = Start-Process powershell -PassThru -ArgumentList @(
        "-NoExit",
        "-Command",
        "`$Host.UI.RawUI.WindowTitle = '$Title'; Set-Location '$Repo'; Write-Host '$Title' -ForegroundColor Cyan; Write-Host '$($Worker.Message)' -ForegroundColor Yellow; git status --short --branch"
    )

    Start-Sleep -Seconds 2

    $Handle = $Process.MainWindowHandle

    if ($Handle -ne 0) {
        [Win32]::MoveWindow(
            $Handle,
            $Worker.X,
            $Worker.Y,
            $Worker.Width,
            $Worker.Height,
            $true
        ) | Out-Null
    }
}

Write-Host ""
Write-Host "AI_OS positioned worker launch complete." -ForegroundColor Green
