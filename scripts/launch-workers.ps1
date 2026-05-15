param(
    [int]$Workers = 2,
    [ValidateSet("Shell", "Codex")]
    [string]$Mode = "Shell"
)

$Repo = "C:\Users\mylab\OneDrive\GitHub\ai-rtony91_Ai_Os_CLEAN"

for ($i = 1; $i -le $Workers; $i++) {
    $WorkerName = "WORKER-$i"

    if ($Mode -eq "Codex") {
        $Command = "cd `"$Repo`"; Write-Host `"$WorkerName CODEX READY`" -ForegroundColor Green; git status --short --branch; codex"
    } else {
        $Command = "cd `"$Repo`"; Write-Host `"$WorkerName SHELL READY`" -ForegroundColor Green; git status --short --branch"
    }

    Start-Process powershell.exe -ArgumentList @(
        "-NoExit",
        "-ExecutionPolicy", "Bypass",
        "-Command", $Command
    )
}
