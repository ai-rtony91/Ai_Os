# AI_OS Governed Worker Launcher v1
# Purpose: launch named PowerShell worker windows inside canonical AI_OS repo.
# Safety: no commits, no pushes, no deploys, no broker, no live trading.

$Repo = "C:\Dev\Ai.Os"

if (!(Test-Path $Repo)) {
    Write-Host "BLOCKED: Canonical repo path not found." -ForegroundColor Red
    exit 1
}

Set-Location $Repo

Write-Host "AI_OS WORKER LAUNCHER v1" -ForegroundColor Cyan
Write-Host "Repo: $Repo" -ForegroundColor Gray
git status --short --branch

$Workers = @(
    @{ Number = "01"; Name = "DEVOPS"; Message = "DevOps worker ready. DRY_RUN first. No auto commit or push." },
    @{ Number = "02"; Name = "TRADING_LAB"; Message = "Trading Lab worker ready. Paper-only. No broker. No live execution." },
    @{ Number = "03"; Name = "VALIDATOR"; Message = "Validator worker ready. Run checks before APPLY." },
    @{ Number = "04"; Name = "TELEMETRY"; Message = "Telemetry worker ready. Track startup and session status." }
)

foreach ($Worker in $Workers) {
    $Title = "AIOS-$($Worker.Number)-$($Worker.Name)"

    Start-Process powershell -ArgumentList @(
        "-NoExit",
        "-Command",
        "`$Host.UI.RawUI.WindowTitle = '$Title'; Set-Location '$Repo'; Write-Host '$Title' -ForegroundColor Cyan; Write-Host '$($Worker.Message)' -ForegroundColor Yellow; git status --short --branch"
    )

    Start-Sleep -Milliseconds 600
}

$ReportDir = "automation\operator\startup_reports"
New-Item -ItemType Directory -Force $ReportDir | Out-Null

$Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$ReportPath = Join-Path $ReportDir "WORKER_LAUNCH_REPORT_001.md"

@"
# AI_OS Worker Launch Report 001

Timestamp:
$Timestamp

Launcher:
Start-AIOSGovernedWorkerLauncher.ps1

Workers Launched:
- AIOS-01-DEVOPS
- AIOS-02-TRADING_LAB
- AIOS-03-VALIDATOR
- AIOS-04-TELEMETRY

Safety:
- No commits executed.
- No pushes executed.
- No deploys executed.
- No broker execution.
- No live trading.
- Repo validation performed before launch.

Canonical Repo:
$Repo
"@ | Set-Content $ReportPath

Write-Host "Worker launch complete." -ForegroundColor Green
Write-Host "Report written: $ReportPath" -ForegroundColor Green
