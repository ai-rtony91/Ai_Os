$repo = "C:\Users\mylab\OneDrive\GitHub\ai-rtony91_Ai_Os_CLEAN"

Write-Host ""
Write-Host "======================================="
Write-Host "      AI_OS MORNING BOOT START"
Write-Host "======================================="
Write-Host ""

# ----------------------------------------
# OPEN AI_OS DASHBOARD
# ----------------------------------------

Start-Process "http://localhost:8080/AIOS_STATIC_PREVIEW.html"

Start-Sleep -Seconds 2

# ----------------------------------------
# START LOCAL SERVER
# ----------------------------------------

Start-Process powershell -ArgumentList @(
'-NoExit',
'-Command',
"Set-Location '$repo'; python -m http.server 8080"
)

Start-Sleep -Seconds 3

# ----------------------------------------
# CODEX WINDOW 1
# ----------------------------------------

Start-Process powershell -ArgumentList @(
'-NoExit',
'-Command',
"`$Host.UI.RawUI.WindowTitle = 'AIOS-CODEX-1';
Set-Location '$repo';
codex"
)

Start-Sleep -Seconds 2

# ----------------------------------------
# CODEX WINDOW 2
# ----------------------------------------

Start-Process powershell -ArgumentList @(
'-NoExit',
'-Command',
"`$Host.UI.RawUI.WindowTitle = 'AIOS-CODEX-2';
Set-Location '$repo';
codex"
)

Start-Sleep -Seconds 2

# ----------------------------------------
# DEVOPS WINDOW
# ----------------------------------------

Start-Process powershell -ArgumentList @(
'-NoExit',
'-Command',
"`$Host.UI.RawUI.WindowTitle = 'AIOS-DEVOPS';
Set-Location '$repo';
git status --short --branch"
)

Start-Sleep -Seconds 2

# ----------------------------------------
# TRADING LAB WINDOW
# ----------------------------------------

Start-Process powershell -ArgumentList @(
'-NoExit',
'-Command',
"`$Host.UI.RawUI.WindowTitle = 'AIOS-TRADING-LAB';
Set-Location '$repo';
Write-Host 'Trading Lab Ready'"
)

Start-Sleep -Seconds 2

# ----------------------------------------
# OPEN IMPORTANT URLS
# ----------------------------------------

Start-Process "https://chatgpt.com"
Start-Process "https://tradingview.com"

Write-Host ""
Write-Host "======================================="
Write-Host " AI_OS MORNING BOOT COMPLETE"
Write-Host "======================================="
Write-Host ""