param(
    [int]$StaleMinutes = 60
)

$LockDir = ".\automation\orchestration\locks"
$Now = Get-Date

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host " AI_OS STALE LOCK DETECTOR" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

Get-ChildItem $LockDir -Filter "*.lock.json" |
ForEach-Object {
    $Data = Get-Content $_.FullName | ConvertFrom-Json

    if ($Data.status -eq "CLAIMED") {
        $ClaimedAt = [datetime]$Data.claimed_at
        $AgeMinutes = [math]::Round(($Now - $ClaimedAt).TotalMinutes, 2)

        if ($AgeMinutes -gt $StaleMinutes) {
            $Data | Add-Member -NotePropertyName "status" -NotePropertyValue "STALE" -Force
            $Data | Add-Member -NotePropertyName "stale_detected_at" -NotePropertyValue $Now.ToString("s") -Force
            $Data | Add-Member -NotePropertyName "age_minutes" -NotePropertyValue $AgeMinutes -Force

            $Data | ConvertTo-Json -Depth 5 |
            Set-Content -Path $_.FullName -Encoding UTF8

            Write-Host "STALE LOCK: $($Data.packet_id) age $AgeMinutes minutes" -ForegroundColor Yellow
        }
        else {
            Write-Host "OK CLAIMED: $($Data.packet_id) age $AgeMinutes minutes" -ForegroundColor Green
        }
    }
    else {
        Write-Host "OK: $($Data.packet_id) status $($Data.status)" -ForegroundColor Green
    }
}
