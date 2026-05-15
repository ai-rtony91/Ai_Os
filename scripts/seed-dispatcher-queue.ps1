$QueuePath = ".\automation\orchestration\queue\DISPATCHER_QUEUE.json"

$Queue = Get-Content $QueuePath | ConvertFrom-Json

$NewItems = @(
    @{
        packet_id = "worker-registry-sync"
        title = "Sync worker heartbeats into worker registry"
        priority = "high"
        status = "READY"
        assigned_worker = ""
        lane = "orchestration"
    },
    @{
        packet_id = "queue-auto-assignment"
        title = "Auto-assign READY queue items to available workers"
        priority = "high"
        status = "READY"
        assigned_worker = ""
        lane = "orchestration"
    },
    @{
        packet_id = "stale-worker-cleanup"
        title = "Detect stale workers and mark them for cleanup"
        priority = "medium"
        status = "READY"
        assigned_worker = ""
        lane = "recovery"
    },
    @{
        packet_id = "morning-layout-bootstrap"
        title = "Connect AI_OS startup shortcut, workers, and layout routine"
        priority = "medium"
        status = "READY"
        assigned_worker = ""
        lane = "startup"
    }
)

foreach ($NewItem in $NewItems) {
    $Exists = $Queue.items | Where-Object { $_.packet_id -eq $NewItem.packet_id }
    if ($null -eq $Exists) {
        $Queue.items += $NewItem
    }
}

$Queue | ConvertTo-Json -Depth 10 |
Set-Content -Path $QueuePath -Encoding UTF8

Write-Host "Queue seeded with next automation tasks." -ForegroundColor Green
