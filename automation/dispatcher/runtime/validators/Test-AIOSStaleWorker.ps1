[CmdletBinding()]
param(
    [string]$WorkerTablePath = "Reports/dispatcher/runtime/active_worker_table.example.json",
    [int]$StaleMinutes = 30
)

$ErrorActionPreference = "Stop"

function Test-AIOSStaleWorker {
    [CmdletBinding()]
    param(
        [string]$WorkerTablePath = "Reports/dispatcher/runtime/active_worker_table.example.json",
        [int]$StaleMinutes = 30
    )

    $findings = New-Object System.Collections.Generic.List[object]
    $status = "PASS"

    if (-not (Test-Path -LiteralPath $WorkerTablePath)) {
        return [pscustomobject]@{
            schema = "AIOS_VALIDATOR_RESULT.v1"
            validator = "stale_worker"
            stage = "recovery_review"
            status = "REVIEW_REQUIRED"
            findings = @([pscustomobject]@{ status = "REVIEW_REQUIRED"; message = "Worker table is missing: $WorkerTablePath" })
            checked_paths = @($WorkerTablePath)
            blocked_actions = @("reassign_worker", "resume_apply", "commit", "push")
            next_safe_action = "Review worker state before reassignment or recovery."
        }
    }

    try {
        $data = Get-Content -LiteralPath $WorkerTablePath -Raw | ConvertFrom-Json
    }
    catch {
        return [pscustomobject]@{
            schema = "AIOS_VALIDATOR_RESULT.v1"
            validator = "stale_worker"
            stage = "recovery_review"
            status = "FAIL"
            findings = @([pscustomobject]@{ status = "FAIL"; message = "Worker table JSON could not parse."; detail = $_.Exception.Message })
            checked_paths = @($WorkerTablePath)
            blocked_actions = @("reassign_worker", "resume_apply", "commit", "push")
            next_safe_action = "Fix worker runtime JSON before recovery review."
        }
    }

    $workers = @($data.workers)
    if ($workers.Count -eq 0) {
        $status = "REVIEW_REQUIRED"
        $findings.Add([pscustomobject]@{ status = "REVIEW_REQUIRED"; message = "No workers found in worker table." }) | Out-Null
    }

    foreach ($worker in $workers) {
        $heartbeatValue = $worker.last_heartbeat
        if (-not $heartbeatValue) {
            $status = "REVIEW_REQUIRED"
            $findings.Add([pscustomobject]@{ status = "REVIEW_REQUIRED"; message = "Worker has no heartbeat timestamp: $($worker.worker_id)" }) | Out-Null
            continue
        }

        try {
            $heartbeat = [datetime]::Parse($heartbeatValue).ToUniversalTime()
            $ageMinutes = ([datetime]::UtcNow - $heartbeat).TotalMinutes
            if ($ageMinutes -gt $StaleMinutes) {
                $status = "REVIEW_REQUIRED"
                $findings.Add([pscustomobject]@{ status = "REVIEW_REQUIRED"; message = "Worker heartbeat is stale: $($worker.worker_id)" }) | Out-Null
            }
            else {
                $findings.Add([pscustomobject]@{ status = "PASS"; message = "Worker heartbeat is current: $($worker.worker_id)" }) | Out-Null
            }
        }
        catch {
            $status = "FAIL"
            $findings.Add([pscustomobject]@{ status = "FAIL"; message = "Worker heartbeat timestamp is invalid: $($worker.worker_id)" }) | Out-Null
        }
    }

    [pscustomobject]@{
        schema = "AIOS_VALIDATOR_RESULT.v1"
        validator = "stale_worker"
        stage = "recovery_review"
        status = $status
        findings = $findings.ToArray()
        checked_paths = @($WorkerTablePath)
        blocked_actions = @("reassign_worker", "resume_apply", "commit", "push")
        next_safe_action = "Review stale worker ownership before reassignment or resume."
    }
}

if ($MyInvocation.InvocationName -ne ".") {
    Test-AIOSStaleWorker -WorkerTablePath $WorkerTablePath -StaleMinutes $StaleMinutes | ConvertTo-Json -Depth 8
}
