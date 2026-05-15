param(
    [int]$Workers = 2
)

$Repo = "C:\Users\mylab\OneDrive\GitHub\ai-rtony91_Ai_Os_CLEAN"

for ($i = 1; $i -le $Workers; $i++) {
    $WorkerName = "WORKER-$i"
    $Command = "cd `"$Repo`"; Write-Host `"$WorkerName READY`" -ForegroundColor Green; git status --short --branch"

    Start-Process powershell.exe -ArgumentList @(
        "-NoExit",
        "-ExecutionPolicy", "Bypass",
        "-Command", $Command
    )
}
