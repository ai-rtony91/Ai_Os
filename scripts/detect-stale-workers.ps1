param(
    [int]$StaleMinutes = 30
)

$WorkerDir = ".\automation\orchestration\workers"
$Now = Get-Date

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host " AI_OS STALE WORKER DETECTOR" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

Get-ChildItem $WorkerDir -Filter "*heartbeat.json" |
ForEach-Object {
    $Data = Get-Content $_.FullName | ConvertFrom-Json
    $Last = [datetime]$Data.last_heartbeat
    $AgeMinutes = [math]::Round(($Now - $Last).TotalMinutes, 2)

    if ($AgeMinutes -gt $StaleMinutes -and $Data.status -eq "ACTIVE") {
        $Data.status = "STALE"
        $Data.stale_detected_at = $Now.ToString("s")
        $Data.age_minutes = $AgeMinutes

        $Data | ConvertTo-Json -Depth 5 |
        Set-Content -Path $_.FullName -Encoding UTF8

        Write-Host "STALE: $($Data.worker_id) age $AgeMinutes minutes" -ForegroundColor Yellow
    }
    else {
        Write-Host "OK: $($Data.worker_id) status $($Data.status) age $AgeMinutes minutes" -ForegroundColor Green
    }
}
