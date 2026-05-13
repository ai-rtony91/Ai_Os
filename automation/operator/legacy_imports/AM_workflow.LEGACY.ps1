# ============================================
# MorningLaunch.ps1 — AlgoTradez Morning Setup
# Monitor: 3440x1440 Ultrawide
# Chrome  = top-right | Edge = bottom-right
# ============================================

Add-Type -AssemblyName System.Windows.Forms

# Win32 API for window positioning
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class WinAPI {
    [DllImport("user32.dll")] public static extern bool MoveWindow(IntPtr hWnd, int X, int Y, int W, int H, bool repaint);
    [DllImport("user32.dll")] public static extern IntPtr FindWindow(string cls, string title);
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int cmd);
}
"@

# Kill Firefox
Get-Process firefox -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Milliseconds 500

# --- CHROME: TradersPost + TradingView (top-right) ---
$chrome = "C:\Program Files\Google\Chrome\Application\chrome.exe"
Start-Process $chrome -ArgumentList "--new-window https://traderspost.io https://www.tradingview.com"
Start-Sleep -Seconds 3

$chromeProc = Get-Process chrome | Sort-Object StartTime -Descending | Select-Object -First 1
if ($chromeProc) {
    [WinAPI]::ShowWindow($chromeProc.MainWindowHandle, 1) | Out-Null
    [WinAPI]::MoveWindow($chromeProc.MainWindowHandle, 1720, 0, 1720, 720, $true) | Out-Null
}

# --- EDGE: Azure Portal (bottom-right) ---
Start-Process "msedge" -ArgumentList "--new-window https://portal.azure.com"
Start-Sleep -Seconds 3

$edgeProc = Get-Process msedge | Sort-Object StartTime -Descending | Select-Object -First 1
if ($edgeProc) {
    [WinAPI]::ShowWindow($edgeProc.MainWindowHandle, 1) | Out-Null
    [WinAPI]::MoveWindow($edgeProc.MainWindowHandle, 1720, 720, 1720, 720, $true) | Out-Null
}

# Log run
Add-Content "C:\Scripts\log.txt" "MorningLaunch RUN: $(Get-Date)"
