# AI-OS quick launcher
$Root = "C:\Dev\Ai.Os"

Start-Process explorer.exe $Root
Start-Process explorer.exe "$Root\scripts"
Start-Process explorer.exe "$Root\logs"
Start-Process explorer.exe "$Root\Tasks"

# Open PowerShell at project root
Start-Process powershell.exe -ArgumentList "-NoExit", "-Command", "cd `"$Root`""

# Open VS Code if installed
Start-Process powershell.exe -ArgumentList "-NoExit", "-Command", "cd `"$Root`"; code ."

# Open focused terminals

Start-Process powershell.exe -ArgumentList "-NoExit", "-Command", "cd `"$Root\scripts`"; title SCRIPTS"

Start-Process powershell.exe -ArgumentList "-NoExit", "-Command", "cd `"$Root\logs`"; title LOGS"

Start-Process powershell.exe -ArgumentList "-NoExit", "-Command", "cd `"$Root\src`"; title SOURCE"
