$QueuePath = ".\automation\orchestration\queue\DISPATCHER_QUEUE.json"

$Assignments = @(
    @{ packet_id = "worker-registry-sync"; worker_id = "WORKER-1" },
    @{ packet_id = "queue-auto-assignment"; worker_id = "WORKER-2" },
    @{ packet_id = "stale-worker-cleanup"; worker_id = "WORKER-3" },
    @{ packet_id = "morning-layout-bootstrap"; worker_id = "WORKER-4" }
)

$Queue = Get-Content $QueuePath | ConvertFrom-Json

foreach ($Assignment in $Assignments) {
    $Item = $Queue.items | Where-Object { $_.packet_id -eq $Assignment.packet_id } | Select-Object -First 1

    if ($null -ne $Item -and $Item.status -eq "READY") {
        $Item.status = "ASSIGNED"
        $Item.assigned_worker = $Assignment.worker_id
        $Item.assigned_at = (Get-Date).ToString("s")

        Write-Host "ASSIGNED $($Assignment.packet_id) -> $($Assignment.worker_id)" -ForegroundColor Green
    }
    elseif ($null -ne $Item) {
        Write-Host "SKIPPED $($Assignment.packet_id): status $($Item.status)" -ForegroundColor Yellow
    }
}

$Queue | ConvertTo-Json -Depth 10 |
Set-Content -Path $QueuePath -Encoding UTF8
