param(
    [int]$Workers = 1,
    [ValidateSet("Shell", "Codex")]
    [string]$Mode = "Shell",
    [string]$Packet = ""
)

$Repo = "C:\Users\mylab\OneDrive\GitHub\ai-rtony91_Ai_Os_CLEAN"
$TempDir = Join-Path $env:TEMP "AIOS-worker-launcher"
New-Item -ItemType Directory -Force -Path $TempDir | Out-Null

for ($i = 1; $i -le $Workers; $i++) {
    $WorkerName = "WORKER-$i"

    if ([string]::IsNullOrWhiteSpace($Packet)) {
        $PacketText = "NO PACKET ASSIGNED"
    } else {
        $PacketText = "PACKET: $Packet"
    }

    $WorkerFile = Join-Path $TempDir "$WorkerName.ps1"

    $Lines = @(
        "Set-Location `"$Repo`"",
        "Clear-Host",
        "Write-Host '====================================================' -ForegroundColor Cyan",
        "Write-Host ' AI_OS $Mode WORKER: $WorkerName' -ForegroundColor Cyan",
        "Write-Host '====================================================' -ForegroundColor Cyan",
        "Write-Host ''",
        "Write-Host 'WINDOW ROLE:' -ForegroundColor Yellow",
        "Write-Host 'This is a worker window, not the main control window.'",
        "Write-Host ''",
        "Write-Host 'SAFE RULE:' -ForegroundColor Yellow",
        "Write-Host 'Only paste commands here if ChatGPT specifically says to use this worker.'",
        "Write-Host ''",
        "Write-Host '$PacketText' -ForegroundColor Green",
        "Write-Host ''",
        "git status --short --branch"
    )

    if ($Mode -eq "Codex") {
        $Lines += "codex"
    }

    Set-Content -Path $WorkerFile -Value $Lines -Encoding UTF8

    Start-Process powershell.exe -ArgumentList @(
        "-NoExit",
        "-ExecutionPolicy", "Bypass",
        "-File", $WorkerFile
    )
}
