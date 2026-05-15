param(
    [int]$Workers = 2,
    [ValidateSet("Shell", "Codex")]
    [string]$Mode = "Shell",
    [string]$Packet = ""
)

$Repo = "C:\Users\mylab\OneDrive\GitHub\ai-rtony91_Ai_Os_CLEAN"

for ($i = 1; $i -le $Workers; $i++) {

    $WorkerName = "WORKER-$i"

    if ($Packet -ne "") {
        $PacketText = "PACKET: $Packet"
    } else {
        $PacketText = "NO PACKET ASSIGNED"
    }

    if ($Mode -eq "Codex") {
        $Command = @"
cd '$Repo'
Write-Host ''
Write-Host '$WorkerName CODEX READY' -ForegroundColor Green
Write-Host '$PacketText' -ForegroundColor Cyan
git status --short --branch
codex
"@
    }
    else {
        $Command = @"
cd '$Repo'
Write-Host ''
Write-Host '$WorkerName SHELL READY' -ForegroundColor Green
Write-Host '$PacketText' -ForegroundColor Cyan
git status --short --branch
"@
    }

    Start-Process powershell.exe -ArgumentList @(
        "-NoExit",
        "-ExecutionPolicy", "Bypass",
        "-Command", $Command
    )
}
