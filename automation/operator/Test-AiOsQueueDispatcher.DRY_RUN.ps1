param(
    [string]$RepoRoot = ".",
    [string]$QueuePath = "work_packets/queues/aios_phase2_queue.example.json",
    [string]$PacketRoot = "."
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$failures = New-Object System.Collections.Generic.List[string]
$validLanes = @("main_control", "build_engine", "validation", "docs", "dashboard", "operator_review")
$validStatuses = @("pending", "approved", "dispatched", "validating", "blocked", "complete")
$validApprovalStates = @("not_requested", "requested", "approved", "rejected")
$validValidatorStates = @("not_run", "pass", "fail", "warning")
$blockedTerms = @("broker", "OANDA", "api_key", "webhook", "live_order", "real_order", "scheduled_task", "startup_task")

function Add-Failure {
    param([string]$Message)
    $script:failures.Add($Message) | Out-Null
    Write-Host "FAIL: $Message" -ForegroundColor Red
}

function Read-JsonFile {
    param([string]$FullPath)
    if (-not (Test-Path -LiteralPath $FullPath -PathType Leaf)) {
        Add-Failure "Missing JSON file: $FullPath"
        return $null
    }
    try {
        return Get-Content -LiteralPath $FullPath -Raw | ConvertFrom-Json
    } catch {
        Add-Failure "JSON parse failed: $FullPath :: $($_.Exception.Message)"
        return $null
    }
}

function Test-RequiredField {
    param(
        [object]$Object,
        [string]$Label,
        [string]$FieldName
    )

    if (-not ($Object.PSObject.Properties.Name -contains $FieldName)) {
        Add-Failure "$Label missing required field: $FieldName"
        return $false
    }

    return $true
}

function Test-PowerShellParse {
    param([string]$FullPath)
    if (-not (Test-Path -LiteralPath $FullPath -PathType Leaf)) {
        Add-Failure "Missing PowerShell file: $FullPath"
        return
    }

    $tokens = $null
    $parseErrors = $null
    [System.Management.Automation.Language.Parser]::ParseFile($FullPath, [ref]$tokens, [ref]$parseErrors) | Out-Null
    foreach ($parseError in @($parseErrors)) {
        Add-Failure "PowerShell parse failed: $FullPath :: $($parseError.Message)"
    }
}

function Resolve-AiOsPath {
    param(
        [string]$Path,
        [string]$BasePath
    )

    if ([System.IO.Path]::IsPathRooted($Path)) {
        return $Path
    }

    return Join-Path $BasePath $Path
}

$resolvedRepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path
$resolvedPacketRoot = (Resolve-Path -LiteralPath (Resolve-AiOsPath -Path $PacketRoot -BasePath $resolvedRepoRoot)).Path
$queueFullPath = Resolve-AiOsPath -Path $QueuePath -BasePath $resolvedRepoRoot
$schemaFullPath = Join-Path $resolvedRepoRoot "work_packets/queue.schema.json"
$dispatcherFullPath = Join-Path $resolvedRepoRoot "automation/operator/Invoke-AiOsPacketDispatcher.ps1"

Write-Host "AI_OS Queue Dispatcher DRY_RUN Validator" -ForegroundColor Cyan
Write-Host "Repo: $resolvedRepoRoot"
Write-Host "Queue: $queueFullPath"
Write-Host "Packet root: $resolvedPacketRoot"
Write-Host "Safety: read-only validator. No files are created, edited, moved, deleted, staged, committed, pushed, launched, credential-accessed, or traded."

$schema = Read-JsonFile -FullPath $schemaFullPath
if ($schema) {
    if ($schema.'$id' -ne "AIOS_WORK_QUEUE.v1") {
        Add-Failure "work_packets/queue.schema.json must declare `$id AIOS_WORK_QUEUE.v1."
    }

    foreach ($field in @("queue_id", "version", "created_at", "updated_at", "mode", "queue_status", "packets", "lanes", "approvals", "validators", "next_action", "stop_condition")) {
        if (@($schema.required) -notcontains $field) {
            Add-Failure "Queue schema required list missing: $field"
        }
    }
}

$queueText = ""
if (Test-Path -LiteralPath $queueFullPath -PathType Leaf) {
    $queueText = Get-Content -LiteralPath $queueFullPath -Raw
    foreach ($term in $blockedTerms) {
        if ($queueText.Contains($term)) {
            Add-Failure "Queue file contains blocked term: $term"
        }
    }
}

$queue = Read-JsonFile -FullPath $queueFullPath
if ($queue) {
    Write-Host "Queue JSON parse: PASS" -ForegroundColor Green

    foreach ($field in @("queue_id", "version", "created_at", "updated_at", "mode", "queue_status", "packets", "lanes", "approvals", "validators", "next_action", "stop_condition")) {
        Test-RequiredField -Object $queue -Label "queue" -FieldName $field | Out-Null
    }

    if ($queue.mode -ne "DRY_RUN") {
        Add-Failure "Queue mode must be DRY_RUN."
    }

    $packetIds = @{}
    foreach ($packet in @($queue.packets)) {
        foreach ($field in @("packet_id", "source_file", "title", "lane", "status", "priority", "approval_state", "validator_state", "assigned_worker", "blocked_reason", "next_action")) {
            Test-RequiredField -Object $packet -Label "packet" -FieldName $field | Out-Null
        }

        if ($packetIds.ContainsKey($packet.packet_id)) {
            Add-Failure "Duplicate packet_id: $($packet.packet_id)"
        } else {
            $packetIds[$packet.packet_id] = $true
        }

        if ($validLanes -notcontains $packet.lane) {
            Add-Failure "$($packet.packet_id) invalid lane: $($packet.lane)"
        }
        if ($validStatuses -notcontains $packet.status) {
            Add-Failure "$($packet.packet_id) invalid status: $($packet.status)"
        }
        if ($validApprovalStates -notcontains $packet.approval_state) {
            Add-Failure "$($packet.packet_id) invalid approval_state: $($packet.approval_state)"
        }
        if ($validValidatorStates -notcontains $packet.validator_state) {
            Add-Failure "$($packet.packet_id) invalid validator_state: $($packet.validator_state)"
        }

        $sourceFullPath = Resolve-AiOsPath -Path $packet.source_file -BasePath $resolvedPacketRoot
        if (-not (Test-Path -LiteralPath $sourceFullPath -PathType Leaf)) {
            Add-Failure "$($packet.packet_id) source_file not found: $($packet.source_file)"
        }
    }

    foreach ($lane in @($queue.lanes)) {
        if ((Test-RequiredField -Object $lane -Label "lane" -FieldName "lane") -and $validLanes -notcontains $lane.lane) {
            Add-Failure "Invalid lane registry entry: $($lane.lane)"
        }
    }
}

Test-PowerShellParse -FullPath $dispatcherFullPath
Test-PowerShellParse -FullPath (Join-Path $resolvedRepoRoot "automation/operator/Test-AiOsQueueDispatcher.DRY_RUN.ps1")

try {
    $dispatcherOutput = & powershell -NoProfile -ExecutionPolicy Bypass -File $dispatcherFullPath -RepoRoot $resolvedRepoRoot -QueuePath $QueuePath -PacketRoot $PacketRoot -Explain 2>&1
    if ($LASTEXITCODE -ne 0) {
        Add-Failure "Dispatcher DRY_RUN failed with exit code $LASTEXITCODE"
        $dispatcherOutput | ForEach-Object { Write-Host $_ }
    } else {
        Write-Host "Dispatcher DRY_RUN: PASS" -ForegroundColor Green
    }
} catch {
    Add-Failure "Dispatcher DRY_RUN error: $($_.Exception.Message)"
}

if ($failures.Count -gt 0) {
    Write-Host ""
    Write-Host "AI_OS QUEUE DISPATCHER VALIDATION: FAIL" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "AI_OS QUEUE DISPATCHER VALIDATION: PASS" -ForegroundColor Green
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
exit 0
