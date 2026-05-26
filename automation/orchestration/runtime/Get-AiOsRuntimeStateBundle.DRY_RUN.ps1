param(
    [switch]$QuietJson
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..\..")
$checkedAt = (Get-Date).ToString("s")

function ConvertTo-RelativePath {
    param([string]$Path)

    $resolved = Resolve-Path -LiteralPath $Path -ErrorAction SilentlyContinue
    if (-not $resolved) {
        return $Path.Replace("\", "/")
    }

    $rootPath = $repoRoot.Path.TrimEnd("\")
    $resolvedPath = $resolved.Path
    if ($resolvedPath.StartsWith($rootPath, [System.StringComparison]::OrdinalIgnoreCase)) {
        return $resolvedPath.Substring($rootPath.Length).TrimStart("\").Replace("\", "/")
    }

    return $resolvedPath.Replace("\", "/")
}

function Read-JsonSafe {
    param([string]$Path)

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return $null
    }

    try {
        return Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json
    }
    catch {
        return [pscustomobject]@{
            parse_error = $_.Exception.Message
            path = ConvertTo-RelativePath -Path $Path
        }
    }
}

function New-Freshness {
    param(
        [int]$TtlSeconds = 3600,
        [bool]$IsStale = $false
    )

    [pscustomobject]@{
        checked_at = $checkedAt
        ttl_seconds = $TtlSeconds
        is_stale = $IsStale
    }
}

function New-Section {
    param(
        [string]$Status,
        [string[]]$SourcePaths,
        [string]$Summary,
        [object[]]$Items = @(),
        [bool]$IsStale = $false,
        [string[]]$BlockedActions = @()
    )

    [pscustomobject]@{
        status = $Status
        source_paths = @($SourcePaths | ForEach-Object { ConvertTo-RelativePath -Path $_ })
        summary = $Summary
        items = @($Items)
        freshness = New-Freshness -IsStale $IsStale
        blocked_actions = @($BlockedActions)
    }
}

function Get-JsonFiles {
    param([string]$Path)

    if (-not (Test-Path -LiteralPath $Path -PathType Container)) {
        return @()
    }

    @(Get-ChildItem -LiteralPath $Path -File -Filter "*.json" -ErrorAction SilentlyContinue | Sort-Object Name)
}

$runtimeStatePath = Join-Path $repoRoot.Path "automation\runtime\state\AIOS_RUNTIME_STATE.json"
$packetActivePath = Join-Path $repoRoot.Path "automation\orchestration\work_packets\active"
$packetBlockedPath = Join-Path $repoRoot.Path "automation\orchestration\work_packets\blocked"
$packetCompletePath = Join-Path $repoRoot.Path "automation\orchestration\work_packets\complete"
$workerRegistryPath = Join-Path $repoRoot.Path "automation\orchestration\workers\AIOS_WORKER_REGISTRY.json"
$workerProfilesPath = Join-Path $repoRoot.Path "automation\orchestration\workers\AIOS_WORKER_PROFILES.json"
$workerInboxPath = Join-Path $repoRoot.Path "automation\orchestration\workers\inbox\AIOS_WORKER_INBOX.json"
$lockRegistryPath = Join-Path $repoRoot.Path "automation\orchestration\locks\FILE_LOCK_REGISTRY_001.json"
$validatorConfigPath = Join-Path $repoRoot.Path "automation\orchestration\validators\VALIDATOR_CHAIN_CONFIG_001.json"
$validatorRecommendationPath = Join-Path $repoRoot.Path "automation\orchestration\validators\VALIDATOR_RECOMMENDATION.example.json"
$validatorRunReportPath = Join-Path $repoRoot.Path "automation\orchestration\validator_chain_runner\VALIDATOR_CHAIN_RUN_REPORT.example.json"
$approvalInboxPath = Join-Path $repoRoot.Path "automation\orchestration\approval_inbox.v1.example.json"
$approvalQueuePath = Join-Path $repoRoot.Path "automation\orchestration\approval_inbox\AIOS_APPROVAL_QUEUE.example.json"
$supervisorSchemaPath = Join-Path $repoRoot.Path "schemas\aios\orchestration\overnight_supervisor.schema.json"
$supervisorRulesPath = Join-Path $repoRoot.Path "automation\orchestration\supervisor\aios_supervision_rules.example.json"

$runtimeState = Read-JsonSafe -Path $runtimeStatePath
$workerRegistry = Read-JsonSafe -Path $workerRegistryPath
$workerProfiles = Read-JsonSafe -Path $workerProfilesPath
$workerInbox = Read-JsonSafe -Path $workerInboxPath
$lockRegistry = Read-JsonSafe -Path $lockRegistryPath
$validatorConfig = Read-JsonSafe -Path $validatorConfigPath
$validatorRecommendation = Read-JsonSafe -Path $validatorRecommendationPath
$validatorRunReport = Read-JsonSafe -Path $validatorRunReportPath
$approvalInbox = Read-JsonSafe -Path $approvalInboxPath
$approvalQueue = Read-JsonSafe -Path $approvalQueuePath
$supervisorRules = Read-JsonSafe -Path $supervisorRulesPath

$gitLines = @(& git -C $repoRoot.Path status --short --branch 2>&1 | ForEach-Object { [string]$_ })
$branchLine = @($gitLines | Where-Object { $_ -like "## *" } | Select-Object -First 1)
$changedLines = @($gitLines | Where-Object { $_ -notlike "## *" })

$activePackets = Get-JsonFiles -Path $packetActivePath
$blockedPackets = Get-JsonFiles -Path $packetBlockedPath
$completePackets = Get-JsonFiles -Path $packetCompletePath
$packetItems = @()
foreach ($packetFile in @($activePackets + $blockedPackets + $completePackets)) {
    $packet = Read-JsonSafe -Path $packetFile.FullName
    $packetItems += [pscustomobject]@{
        source_path = ConvertTo-RelativePath -Path $packetFile.FullName
        packet_id = if ($packet -and $packet.packet_id) { [string]$packet.packet_id } else { "" }
        status = if ($packet -and $packet.status) { [string]$packet.status } else { "UNKNOWN" }
        title = if ($packet -and $packet.title) { [string]$packet.title } elseif ($packet -and $packet.intent) { [string]$packet.intent } else { "" }
    }
}

$workerItems = @(
    [pscustomobject]@{
        source = ConvertTo-RelativePath -Path $workerRegistryPath
        kind = "registry"
        count = if ($workerRegistry -and $workerRegistry.workers) { @($workerRegistry.workers).Count } else { 0 }
    },
    [pscustomobject]@{
        source = ConvertTo-RelativePath -Path $workerProfilesPath
        kind = "profiles"
        count = if ($workerProfiles -and $workerProfiles.workers) { @($workerProfiles.workers).Count } else { 0 }
    },
    [pscustomobject]@{
        source = ConvertTo-RelativePath -Path $workerInboxPath
        kind = "inbox"
        count = if ($workerInbox -and $workerInbox.items) { @($workerInbox.items).Count } else { 0 }
    }
)

$validatorItems = @(
    [pscustomobject]@{
        source = ConvertTo-RelativePath -Path $validatorConfigPath
        kind = "config"
        count = if ($validatorConfig -and $validatorConfig.validators) { @($validatorConfig.validators).Count } else { 0 }
    },
    [pscustomobject]@{
        source = ConvertTo-RelativePath -Path $validatorRecommendationPath
        kind = "recommendation"
        result = if ($validatorRecommendation -and $validatorRecommendation.result) { [string]$validatorRecommendation.result } else { "UNKNOWN" }
    },
    [pscustomobject]@{
        source = ConvertTo-RelativePath -Path $validatorRunReportPath
        kind = "run_report"
        result = if ($validatorRunReport -and $validatorRunReport.overall_result) { [string]$validatorRunReport.overall_result } else { "UNKNOWN" }
    }
)

$approvalItems = @(
    [pscustomobject]@{
        source = ConvertTo-RelativePath -Path $approvalInboxPath
        kind = "approval_inbox"
        count = if ($approvalInbox -and $approvalInbox.approvals) { @($approvalInbox.approvals).Count } else { 0 }
    },
    [pscustomobject]@{
        source = ConvertTo-RelativePath -Path $approvalQueuePath
        kind = "approval_queue"
        count = if ($approvalQueue -and $approvalQueue.items) { @($approvalQueue.items).Count } else { 0 }
    }
)

$staleConditions = @()
if ($null -eq $runtimeState) {
    $staleConditions += [pscustomobject]@{
        source = ConvertTo-RelativePath -Path $runtimeStatePath
        condition = "runtime_state_missing"
        severity = "REVIEW"
        next_safe_action = "Review runtime state source before trusting runtime recommendations."
    }
}
if ($changedLines.Count -gt 0) {
    $staleConditions += [pscustomobject]@{
        source = "git status"
        condition = "working_tree_has_visible_changes"
        severity = "REVIEW"
        next_safe_action = "Review changed and untracked files before protected actions."
    }
}
if ($activePackets.Count -eq 0) {
    $staleConditions += [pscustomobject]@{
        source = ConvertTo-RelativePath -Path $packetActivePath
        condition = "no_active_packet_files"
        severity = "WARNING"
        next_safe_action = "Confirm whether the active packet queue is intentionally empty."
    }
}

$confidenceScore = 80
$confidenceReasons = @("Runtime bundle is generated from read-only evidence.")
if ($staleConditions.Count -gt 0) {
    $confidenceScore = 60
    $confidenceReasons += "Review conditions are present."
}
if ($changedLines.Count -gt 0) {
    $confidenceScore -= 10
    $confidenceReasons += "Working tree is not clean."
}
if ($null -eq $runtimeState) {
    $confidenceScore -= 10
    $confidenceReasons += "Runtime state source is missing."
}
if ($confidenceScore -lt 0) {
    $confidenceScore = 0
}

$overallConfidence = "HIGH"
if ($confidenceScore -lt 75) { $overallConfidence = "MEDIUM" }
if ($confidenceScore -lt 50) { $overallConfidence = "LOW" }
if (@($staleConditions | Where-Object { $_.severity -eq "BLOCKED" }).Count -gt 0) { $overallConfidence = "BLOCKED" }

$blockedRuntimeActions = @(
    "write_runtime_state",
    "write_heartbeat",
    "move_packet_state",
    "release_lock",
    "launch_worker",
    "run_apply_path",
    "stage_files",
    "commit_changes",
    "push_changes",
    "schedule_tasks",
    "start_daemon"
)

$bundle = [pscustomobject]@{
    schema = "AIOS_RUNTIME_STATE_BUNDLE.v1"
    schema_version = "1.0"
    generated_at = $checkedAt
    mode = "DRY_RUN"
    authority_boundary = [pscustomobject]@{
        read_only = $true
        approval_authority = "ANTHONY_ONLY"
        generated_evidence_only = $true
        blocked_capabilities = $blockedRuntimeActions
    }
    packet_state = New-Section -Status "REVIEW" -SourcePaths @($packetActivePath, $packetBlockedPath, $packetCompletePath) -Summary "Packet folders inspected as read-only runtime evidence." -Items $packetItems -BlockedActions @("packet_state_change", "packet_assignment")
    worker_state = New-Section -Status "REVIEW" -SourcePaths @($workerRegistryPath, $workerProfilesPath, $workerInboxPath) -Summary "Worker registry, profiles, and inbox inspected without heartbeat writes." -Items $workerItems -BlockedActions @("worker_launch", "heartbeat_write", "worker_state_change")
    lock_state = New-Section -Status "REVIEW" -SourcePaths @($lockRegistryPath) -Summary "Lock registry evidence inspected without lock release." -Items @($lockRegistry) -BlockedActions @("lock_claim", "lock_release", "force_unlock")
    validator_state = New-Section -Status "REVIEW" -SourcePaths @($validatorConfigPath, $validatorRecommendationPath, $validatorRunReportPath) -Summary "Validator config and report evidence inspected without running mutation paths." -Items $validatorItems -BlockedActions @("apply_repair", "approval_grant")
    approval_state = New-Section -Status "REVIEW" -SourcePaths @($approvalInboxPath, $approvalQueuePath) -Summary "Approval evidence inspected without creating or resolving approvals." -Items $approvalItems -BlockedActions @("approval_create", "approval_resolve")
    escalation_state = New-Section -Status $(if ($staleConditions.Count -gt 0) { "REVIEW" } else { "READY" }) -SourcePaths @() -Summary "Escalation persistence is not enabled; review conditions are included in stale_conditions." -Items @($staleConditions) -BlockedActions @("escalation_append", "escalation_resolve")
    git_state = New-Section -Status $(if ($changedLines.Count -gt 0) { "REVIEW" } else { "READY" }) -SourcePaths @("git status --short --branch") -Summary "Git status inspected read-only." -Items @([pscustomobject]@{ branch = [string]$branchLine; changed_lines = $changedLines }) -BlockedActions @("stage_files", "commit_changes", "push_changes")
    supervisor_state = New-Section -Status "READY" -SourcePaths @($supervisorSchemaPath, $supervisorRulesPath) -Summary "Supervisor schema and rules inspected as read-only authority evidence." -Items @($supervisorRules) -BlockedActions @("start_loop", "start_daemon", "launch_worker")
    next_safe_actions = @(
        [pscustomobject]@{
            rank = 1
            action = "Review runtime bundle output before approving any routing or gate enforcement."
            requires_human_approval = $false
            reason = "This bundle is evidence only."
        },
        [pscustomobject]@{
            rank = 2
            action = "Approve a separate APPLY packet before any runtime state persistence or router enforcement."
            requires_human_approval = $true
            reason = "Runtime writes and routing gates remain outside this DRY_RUN helper."
        }
    )
    stale_conditions = $staleConditions
    confidence_state = [pscustomobject]@{
        overall_confidence = $overallConfidence
        confidence_score = $confidenceScore
        confidence_reasons = $confidenceReasons
    }
}

if ($QuietJson) {
    $bundle | ConvertTo-Json -Depth 12
    exit 0
}

Write-Host "AI_OS Runtime State Bundle"
Write-Host "Mode: DRY_RUN"
Write-Host "Schema: $($bundle.schema)"
Write-Host "Confidence: $($bundle.confidence_state.overall_confidence) $($bundle.confidence_state.confidence_score)"
Write-Host "Git: $branchLine"
Write-Host "Packets: $($packetItems.Count)"
Write-Host "Workers sources: $($workerItems.Count)"
Write-Host "Validator sources: $($validatorItems.Count)"
Write-Host "Approval sources: $($approvalItems.Count)"
Write-Host "Stale/review conditions: $($staleConditions.Count)"
Write-Host ""
Write-Host "Next safe actions:"
foreach ($action in $bundle.next_safe_actions) {
    Write-Host ("{0}. {1}" -f $action.rank, $action.action)
}
Write-Host ""
Write-Host "Runtime mutation skipped: Runtime State Bundle DRY_RUN is read-only."
Write-Host "Files changed by helper: NO"
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
