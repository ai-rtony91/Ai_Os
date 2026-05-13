param(
    [Parameter(Mandatory = $true)]
    [string]$WorkerId
)

if ($WorkerId -notmatch '^AIOS-\d{2}$') {
    Write-Host "BLOCKED: WorkerId must use AIOS-## format. Example: AIOS-01" -ForegroundColor Red
    exit 1
}

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Repo = Split-Path -Parent (Split-Path -Parent $ScriptDir)
$ActiveQueue = Join-Path $ScriptDir "worker_queue\active"

Write-Host "AI_OS WORKER JOB CARD" -ForegroundColor Cyan
Write-Host "Worker: $WorkerId" -ForegroundColor Cyan

if (!(Test-Path $ActiveQueue)) {
    Write-Host "WARN: Job card folder not found: $ActiveQueue" -ForegroundColor Yellow
    Write-Host "Next step: check that automation/operator/worker_queue/active exists." -ForegroundColor Yellow
    Write-Host "STOP RULES" -ForegroundColor Magenta
    Write-Host "- Read this job card first." -ForegroundColor Magenta
    Write-Host "- Work in DRY_RUN unless the operator approves APPLY." -ForegroundColor Magenta
    Write-Host "- Do not commit." -ForegroundColor Magenta
    Write-Host "- Do not push." -ForegroundColor Magenta
    Write-Host "- Do not use secrets, API keys, brokers, OANDA, or live trading." -ForegroundColor Magenta
    Write-Host "- Report what you found before changing anything." -ForegroundColor Magenta
    exit 0
}

$Matches = Get-ChildItem -LiteralPath $ActiveQueue -Filter "$WorkerId-*.md" -File | Sort-Object Name

if ($Matches.Count -eq 0) {
    Write-Host "WARN: No job card found for $WorkerId." -ForegroundColor Yellow
    Write-Host "Next step: create one job card named $WorkerId-SHORT-NAME.md." -ForegroundColor Yellow
    Write-Host "STOP RULES" -ForegroundColor Magenta
    Write-Host "- Read this job card first." -ForegroundColor Magenta
    Write-Host "- Work in DRY_RUN unless the operator approves APPLY." -ForegroundColor Magenta
    Write-Host "- Do not commit." -ForegroundColor Magenta
    Write-Host "- Do not push." -ForegroundColor Magenta
    Write-Host "- Do not use secrets, API keys, brokers, OANDA, or live trading." -ForegroundColor Magenta
    Write-Host "- Report what you found before changing anything." -ForegroundColor Magenta
    exit 0
}

if ($Matches.Count -gt 1) {
    Write-Host "WARN: More than one job card found for $WorkerId." -ForegroundColor Yellow
    foreach ($Match in $Matches) {
        Write-Host "- $($Match.FullName)" -ForegroundColor Yellow
    }
    Write-Host "Next step: keep only one active job card for this worker." -ForegroundColor Yellow
    Write-Host "STOP RULES" -ForegroundColor Magenta
    Write-Host "- Read this job card first." -ForegroundColor Magenta
    Write-Host "- Work in DRY_RUN unless the operator approves APPLY." -ForegroundColor Magenta
    Write-Host "- Do not commit." -ForegroundColor Magenta
    Write-Host "- Do not push." -ForegroundColor Magenta
    Write-Host "- Do not use secrets, API keys, brokers, OANDA, or live trading." -ForegroundColor Magenta
    Write-Host "- Report what you found before changing anything." -ForegroundColor Magenta
    exit 0
}

$JobCard = $Matches[0]
$RelativeJobCard = Resolve-Path -LiteralPath $JobCard.FullName -Relative

Write-Host "File: $RelativeJobCard" -ForegroundColor Green
Write-Host ""
Write-Host "YOUR JOB" -ForegroundColor Cyan
Get-Content -LiteralPath $JobCard.FullName
Write-Host ""
Write-Host "STOP RULES" -ForegroundColor Magenta
Write-Host "- Read this job card first." -ForegroundColor Magenta
Write-Host "- Work in DRY_RUN unless the operator approves APPLY." -ForegroundColor Magenta
Write-Host "- Do not commit." -ForegroundColor Magenta
Write-Host "- Do not push." -ForegroundColor Magenta
Write-Host "- Do not use secrets, API keys, brokers, OANDA, or live trading." -ForegroundColor Magenta
Write-Host "- Report what you found before changing anything." -ForegroundColor Magenta
