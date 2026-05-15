param(
    [int]$Workers = 1,
    [int]$StartIndex = 1,
    [ValidateSet("Shell", "Codex")]
    [string]$Mode = "Shell",
    [string]$Packet = "",
    [string]$RolePrefix = ""
)

$Repo = "C:\Users\mylab\OneDrive\GitHub\ai-rtony91_Ai_Os_CLEAN"
$TempDir = Join-Path $env:TEMP "AIOS-worker-launcher"

New-Item -ItemType Directory -Force -Path $TempDir | Out-Null

$ShellRoles = @(
    "Validator",
    "Git Status",
    "Heartbeat",
    "Stale Detector",
    "Logs",
    "Search",
    "Standby",
    "Docs"
)

$CodexRoles = @(
    "Build Lane",
    "Architecture Lane",
    "Recovery Lane"
)

for ($offset = 0; $offset -lt $Workers; $offset++) {
    $WorkerNumber = $StartIndex + $offset

    if ($Mode -eq "Codex") {
        $Role = $CodexRoles[$offset]
        if ([string]::IsNullOrWhiteSpace($Role)) { $Role = "Codex Lane" }
        $WorkerName = "CODEX-$($offset + 1)"
    }
    else {
        $Role = $ShellRoles[$offset]
        if ([string]::IsNullOrWhiteSpace($Role)) { $Role = "Shell Lane" }
        $WorkerName = "WORKER-$WorkerNumber"
    }

    if (-not [string]::IsNullOrWhiteSpace($RolePrefix)) {
        $Role = $RolePrefix
    }

    if ([string]::IsNullOrWhiteSpace($Packet)) {
        $PacketText = "NO PACKET ASSIGNED"
    }
    else {
        $PacketText = "PACKET: $Packet"
    }

    $WorkerFile = Join-Path $TempDir "$WorkerName.ps1"

    $Lines = @(
        "Set-Location `"$Repo`"",
        "`$host.UI.RawUI.WindowTitle = '$WorkerName | $Role'",
        "Clear-Host",
        "Write-Host '====================================================' -ForegroundColor Cyan",
        "Write-Host ' AI_OS $Mode : $WorkerName' -ForegroundColor Cyan",
        "Write-Host ' ROLE: $Role' -ForegroundColor Yellow",
        "Write-Host '====================================================' -ForegroundColor Cyan",
        "Write-Host ''",
        "Write-Host '$PacketText' -ForegroundColor Green",
        "Write-Host ''",
        "powershell -ExecutionPolicy Bypass -File .\scripts\write-worker-heartbeat.ps1 -WorkerId '$WorkerName' -Role '$Role' -Packet '$Packet'",
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
