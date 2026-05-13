# MorningLaunch.ps1 - AlgoTradez Morning Setup
# Monitor: 3440x1440 Ultrawide


Add-Type -AssemblyName System.Windows.Forms
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class WinAPI {
    [DllImport("user32.dll")] public static extern bool MoveWindow(IntPtr hWnd, int X, int Y, int W, int H, bool repaint);
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int cmd);
}
"@

function WaitForWindow($processName, $timeoutSec = 12) {
    $elapsed = 0
    while ($elapsed -lt $timeoutSec) {
        $proc = Get-Process $processName -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowHandle -ne 0 } | Select-Object -First 1
        if ($proc) { return $proc }
        Start-Sleep -Milliseconds 500
        $elapsed += 0.5
    }
    return $null
}

function PositionWindow($proc, $x, $y, $w, $h) {
    if ($proc -and $proc.MainWindowHandle -ne 0) {
        [WinAPI]::ShowWindow($proc.MainWindowHandle, 1) | Out-Null
        [WinAPI]::MoveWindow($proc.MainWindowHandle, $x, $y, $w, $h, $true) | Out-Null
    }
}

$chrome = "C:\Program Files\Google\Chrome\Application\chrome.exe"

# TOP-RIGHT: TradingView + OANDA
Start-Process $chrome -ArgumentList "--profile-directory=Default --new-window https://www.tradingview.com https://trade.oanda.com"
Start-Sleep -Seconds 3
$chromeProc = WaitForWindow "chrome"
PositionWindow $chromeProc 1720 0 1720 720

# BOTTOM-RIGHT: AI-OS + Azure (Edge)
Start-Process "msedge" -ArgumentList "--new-window https://algotradez-aios.azurewebsites.net https://portal.azure.com"
Start-Sleep -Seconds 3
$edgeProc = WaitForWindow "msedge"
PositionWindow $edgeProc 2293 720 1147 720

# TOP-LEFT: VS Code
Start-Process "code" -ArgumentList "C:\Users\mylab\OneDrive\Desktop\ai_Os"
Start-Sleep -Seconds 4
$codeProc = WaitForWindow "Code"
PositionWindow $codeProc 0 0 1720 720

# BOTTOM-MIDDLE: Claude Desktop
$claudeExe = "$env:LOCALAPPDATA\AnthropicClaude\claude.exe"
Start-Process $claudeExe
Start-Sleep -Seconds 4
$claudeProc = WaitForWindow "claude"
PositionWindow $claudeProc 1147 720 1157 720

# BOTTOM-LEFT: GitHub
Start-Process $chrome -ArgumentList "--profile-directory=Default --new-window https://github.com/ai-rtony91"
Start-Sleep -Seconds 3
$ghProc = Get-Process chrome -ErrorAction SilentlyContinue | Sort-Object StartTime -Descending | Where-Object { $_.MainWindowHandle -ne 0 } | Select-Object -First 1
PositionWindow $ghProc 0 720 1161 720

# MINIMIZED: YouTube Music
Start-Process $chrome -ArgumentList "--profile-directory=Default --new-window https://music.youtube.com/watch?v=Lwd7WQ8L5dQ&si=r9aAEg2c7DqgeV8D"
Start-Sleep -Seconds 8
$ytProc = Get-Process chrome -ErrorAction SilentlyContinue | Sort-Object StartTime -Descending | Where-Object { $_.MainWindowHandle -ne 0 } | Select-Object -First 1
if ($ytProc -and $ytProc.MainWindowHandle -ne 0) {
    [WinAPI]::ShowWindow($ytProc.MainWindowHandle, 6) | Out-Null
}

# Log
Add-Content "C:\Scripts\log.txt" "MorningLaunch RUN: $(Get-Date)"
Write-Host "AlgoTradez is LIVE. Let's get it. $`$`$" -ForegroundColor Green



