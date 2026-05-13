Add-Type @"
using System;
using System.Runtime.InteropServices;

public class Win32Rect {
    [StructLayout(LayoutKind.Sequential)]
    public struct RECT {
        public int Left;
        public int Top;
        public int Right;
        public int Bottom;
    }

    [DllImport("user32.dll")]
    public static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect);
}
"@

$OutPath = "automation\operator\layout_profiles\CODEX_CAPTURED_CURRENT.json"

$Targets = @(
    "AIOS-01",
    "AIOS-02",
    "AIOS-03",
    "AIOS-04"
)

$Captured = foreach ($Target in $Targets) {
    $Proc = Get-Process | Where-Object {
        $_.MainWindowTitle -like "*$Target*"
    } | Select-Object -First 1

    if ($Proc -and $Proc.MainWindowHandle -ne 0) {
        $rect = New-Object Win32Rect+RECT
        [Win32Rect]::GetWindowRect($Proc.MainWindowHandle, [ref]$rect) | Out-Null

        [PSCustomObject]@{
            title = $Target
            x = $rect.Left
            y = $rect.Top
            width = $rect.Right - $rect.Left
            height = $rect.Bottom - $rect.Top
        }
    }
}

$Profile = [PSCustomObject]@{
    profile_name = "CODEX_CAPTURED_CURRENT"
    layout_type = "CAPTURED_FROM_ACTIVE_WINDOWS"
    captured_at = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    windows = $Captured
}

$Profile | ConvertTo-Json -Depth 10 | Set-Content $OutPath

python -m json.tool $OutPath > $null

Get-Content $OutPath
