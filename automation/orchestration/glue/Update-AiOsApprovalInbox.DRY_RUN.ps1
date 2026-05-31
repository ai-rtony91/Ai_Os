[CmdletBinding()]
param(
    [string]$WorkerPacketDir = "control/operation_glue/worker_packets",
    [string]$WorkerResultDir = "telemetry/operation_glue/worker_results",
    [switch]$Apply,
    [switch]$OutputJson
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-AiOsUtcTimestamp {
    return (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
}

function Read-AiOsJsonFiles {
    param([string]$Directory)
    if (-not (Test-Path -LiteralPath $Directory -PathType Container)) {
        return @()
    }

    return @(Get-ChildItem -LiteralPath $Directory -Filter "*.json" -File -ErrorAction SilentlyContinue | Sort-Object LastWriteTime | ForEach-Object {
        try {
            [pscustomobject]@{
                path = $_.FullName
                relative_path = $_.FullName.Substring((Resolve-Path ".").Path.Length + 1)
                last_write_time = $_.LastWriteTimeUtc.ToString("o")
                json = Get-Content -LiteralPath $_.FullName -Raw | ConvertFrom-Json
            }
        }
        catch {
            [pscustomobject]@{
                path = $_.FullName
                relative_path = $_.FullName.Substring((Resolve-Path ".").Path.Length + 1)
                last_write_time = $_.LastWriteTimeUtc.ToString("o")
                json = $null
                error = $_.Exception.Message
            }
        }
    })
}

function New-AiOsInboxEntry {
    param(
        [object]$PacketRecord,
        [object]$ResultRecord
    )

    $packet = $PacketRecord.json
    $result = if ($ResultRecord) { $ResultRecord.json } else { $null }
    $protected = if ($packet) { [bool]$packet.protected_action_gate_required } else { $false }
    $approvalMarker = if ($packet) { [string]$packet.approval_marker_required } else { "UNKNOWN" }
    $resultStatus = if ($result) { [string]$result.status } else { "MISSING" }

    $status = "WAITING_FOR_WORKER"
    $approvalRequired = $false
    $reason = "Worker packet exists but no imported worker result was found."
    $next = "Import the worker result before approval review."

    if ($result) {
        if ($resultStatus -eq "FAILED") {
            $status = "BLOCKED"
            $reason = "Worker result failed."
            $next = "Review failure evidence before assigning follow-up."
        }
        elseif ($resultStatus -eq "BLOCKED") {
            $status = "BLOCKED"
            $reason = "Worker result reported a blocker."
            $next = "Resolve blocker before continuing."
        }
        elseif ($resultStatus -eq "NEEDS_APPROVAL" -or $protected -or $approvalMarker -notin @("NOT_REQUIRED", "HUMAN_REVIEW_REQUIRED")) {
            $status = "NEEDS_APPROVAL"
            $approvalRequired = $true
            $reason = "Result or packet requires Human Owner approval."
            $next = "Review approval marker and Protected Action Gate requirements before execution."
        }
        elseif ($resultStatus -eq "WARN") {
            $status = "NEEDS_REVIEW"
            $reason = "Worker result contains review warning."
            $next = "Review warning and decide whether to hold or continue."
        }
        elseif ($resultStatus -eq "PASS") {
            $status = "READY_FOR_NEXT_SAFE_ACTION"
            $reason = "Worker result passed and no protected action is required."
            $next = "Review summary and assign the next safe packet."
        }
    }

    [ordered]@{
        item_id                        = "APPROVAL_ITEM_{0}" -f ([string]$packet.packet_id)
        source_packet                  = $PacketRecord.relative_path
        source_result                  = if ($ResultRecord) { $ResultRecord.relative_path } else { $null }
        action_type                    = if ($protected) { "PROTECTED_ACTION_REVIEW" } else { "WORKER_RESULT_REVIEW" }
        status                         = $status
        approval_required              = $approvalRequired
        approval_marker_required       = $approvalMarker
        protected_action_gate_required = $protected
        reason                         = $reason
        next_safe_action               = $next
    }
}

$packetRecords = @(Read-AiOsJsonFiles -Directory $WorkerPacketDir)
$resultRecords = @(Read-AiOsJsonFiles -Directory $WorkerResultDir)
$latestResult = @($resultRecords | Sort-Object last_write_time -Descending | Select-Object -First 1)
$entries = @()

foreach ($packetRecord in $packetRecords) {
    if ($null -eq $packetRecord.json) { continue }
    $resultRecord = if ($latestResult.Count -gt 0) { $latestResult[0] } else { $null }
    $entries += New-AiOsInboxEntry -PacketRecord $packetRecord -ResultRecord $resultRecord
}

if ($entries.Count -eq 0 -and $resultRecords.Count -gt 0) {
    $resultRecord = @($resultRecords | Sort-Object last_write_time -Descending | Select-Object -First 1)[0]
    $entries += [ordered]@{
        item_id                        = "APPROVAL_ITEM_UNMATCHED_RESULT"
        source_packet                  = $null
        source_result                  = $resultRecord.relative_path
        action_type                    = "UNMATCHED_WORKER_RESULT"
        status                         = "NEEDS_REVIEW"
        approval_required              = $false
        approval_marker_required       = "UNKNOWN"
        protected_action_gate_required = $false
        reason                         = "Worker result exists without a matching Operation Glue worker packet."
        next_safe_action               = "Review result and generate or attach a worker packet."
    }
}

$blockedCount = @($entries | Where-Object { $_.status -eq "BLOCKED" }).Count
$approvalCount = @($entries | Where-Object { $_.approval_required -eq $true }).Count
$pendingCount = @($entries | Where-Object { $_.status -in @("WAITING_FOR_WORKER", "NEEDS_REVIEW", "NEEDS_APPROVAL") }).Count

$inbox = [ordered]@{
    schema                  = "AIOS_OPERATION_GLUE_APPROVAL_INBOX.v0_1"
    generated_at            = Get-AiOsUtcTimestamp
    packet_count            = $packetRecords.Count
    result_count            = $resultRecords.Count
    item_count              = $entries.Count
    pending_count           = $pendingCount
    approval_required_count = $approvalCount
    blocked_count           = $blockedCount
    entries                 = $entries
    next_safe_action        = if ($approvalCount -gt 0) {
        "Review approval-required items before execution."
    } elseif ($blockedCount -gt 0) {
        "Resolve blocked items before continuing."
    } elseif ($entries.Count -gt 0) {
        "Review ready items and assign the next safe packet."
    } else {
        "Generate a worker packet from a goal intake file."
    }
}

$outputPath = "DRY_RUN_NO_FILE_WRITTEN"
if ($Apply) {
    $outDir = "control/operation_glue"
    New-Item -ItemType Directory -Force -Path $outDir | Out-Null
    $outputPath = Join-Path $outDir "APPROVAL_INBOX.json"
    $inbox | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $outputPath -Encoding UTF8
}

$report = [ordered]@{
    schema           = "AIOS_OPERATION_GLUE_APPROVAL_INBOX_UPDATE_REPORT.v0_1"
    mode             = if ($Apply) { "APPLY" } else { "DRY_RUN" }
    output_path      = $outputPath
    wrote_file       = [bool]$Apply
    approval_inbox   = $inbox
}

if ($OutputJson) {
    $report | ConvertTo-Json -Depth 12
    exit 0
}

Write-Host "AI_OS Operation Glue - Approval Inbox Builder"
Write-Host ("Mode: {0}" -f $report.mode)
Write-Host ("Packets: {0}" -f $inbox.packet_count)
Write-Host ("Results: {0}" -f $inbox.result_count)
Write-Host ("Approval items: {0}" -f $inbox.item_count)
Write-Host ("Pending: {0}" -f $inbox.pending_count)
Write-Host ("Blocked: {0}" -f $inbox.blocked_count)
Write-Host ("Output: {0}" -f $outputPath)
Write-Host ("Next safe action: {0}" -f $inbox.next_safe_action)
Write-Host "No commit, push, merge, reset, clean, branch deletion, or protected action performed."
Write-Host ""
$report | ConvertTo-Json -Depth 12
