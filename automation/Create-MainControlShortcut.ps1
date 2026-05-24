# ============================================================
#  Create-MainControlShortcut.ps1
#  PURPOSE : Deploy AI_OS_MAIN_CONTROL.ps1 to user root and
#            rebuild the desktop shortcut cleanly.
#  RUN ONCE after pulling a new version of the launcher.
#  MODE     : APPLY (makes real changes — review before running)
# ============================================================

$ErrorActionPreference = "Stop"

$sourceScript  = "C:\Dev\Ai.Os\AI_OS_MAIN_CONTROL.ps1"
$targetScript  = "C:\Users\mylab\AI_OS_MAIN_CONTROL.ps1"
$desktopPath   = [Environment]::GetFolderPath("Desktop")
$shortcutPath  = "$desktopPath\AI_OS_MAIN_CONTROL.lnk"
$pwshExe       = "C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"

Write-Host ""
Write-Host "  AI_OS MAIN CONTROL -- SHORTCUT INSTALLER" -ForegroundColor Cyan
Write-Host "  $("=" * 50)" -ForegroundColor Cyan
Write-Host ""

# --- Step 1: Verify source exists ---
if (-not (Test-Path $sourceScript)) {
    Write-Host "  [BLOCKED] Source script not found:" -ForegroundColor Red
    Write-Host "  $sourceScript" -ForegroundColor Yellow
    Write-Host "  Cannot proceed." -ForegroundColor Red
    exit 1
}
Write-Host "  [OK] Source script found." -ForegroundColor Green

# --- Step 2: Copy to user root ---
Copy-Item -Path $sourceScript -Destination $targetScript -Force
Write-Host "  [OK] Deployed to : $targetScript" -ForegroundColor Green

# --- Step 3: Remove stale shortcut if present ---
if (Test-Path $shortcutPath) {
    Remove-Item $shortcutPath -Force
    Write-Host "  [OK] Removed stale shortcut." -ForegroundColor Yellow
}

# --- Step 4: Create fresh shortcut ---
$shell   = New-Object -ComObject WScript.Shell
$lnk     = $shell.CreateShortcut($shortcutPath)

$lnk.TargetPath       = $pwshExe
$lnk.Arguments        = "-ExecutionPolicy Bypass -NoExit -File `"$targetScript`""
$lnk.WorkingDirectory = "C:\Dev\Ai.Os"
$lnk.WindowStyle      = 1   # 1 = Normal window
$lnk.Description      = "AI_OS MAIN CONTROL - ORCHESTRATOR"
$lnk.Save()

Write-Host "  [OK] Shortcut created : $shortcutPath" -ForegroundColor Green
Write-Host ""
Write-Host "  DONE. Open AI_OS_MAIN_CONTROL.lnk from your Desktop." -ForegroundColor Cyan
Write-Host "  $("=" * 50)" -ForegroundColor Cyan
Write-Host ""
