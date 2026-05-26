param(
    [switch]$QuietJson
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..\..")

function Get-RelativePathSafe {
    param([string]$Path)

    $resolved = Resolve-Path -LiteralPath $Path -ErrorAction SilentlyContinue
    if (-not $resolved) {
        return $Path
    }

    return [System.IO.Path]::GetRelativePath($repoRoot.Path, $resolved.Path).Replace("\", "/")
}

function Read-JsonFile {
    param([string]$Path)

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return $null
    }

    return Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json
}

function Get-GitStatusLines {
    $statusOutput = & git -C $repoRoot.Path status --short --branch 2>&1
    return @($statusOutput | ForEach-Object { [string]$_ })
}

$statusLines = Get-GitStatusLines
$branchLine = @($statusLines | Where-Object { $_ -like "## *" } | Select-Object -First 1)
$changedFiles = @($statusLines | Where-Object { $_ -match "^\s*M\s+" } | ForEach-Object { ($_ -replace "^\s*M\s+", "").Trim() })
$untrackedItems = @($statusLines | Where-Object { $_ -match "^\?\?\s+" } | ForEach-Object { ($_ -replace "^\?\?\s+", "").Trim() })

$queueHealthPath = Join-Path $repoRoot.Path "automation\orchestration\queue_health_supervisor.v1.example.json"
$validatorConfigPath = Join-Path $repoRoot.Path "automation\orchestration\validators\VALIDATOR_CHAIN_CONFIG_001.json"
$approvalInboxPath = Join-Path $repoRoot.Path "automation\orchestration\approval_inbox.v1.example.json"
$workerRegistryPath = Join-Path $repoRoot.Path "automation\orchestration\workers\AIOS_WORKER_REGISTRY.json"

$queueHealth = Read-JsonFile -Path $queueHealthPath
$validatorConfig = Read-JsonFile -Path $validatorConfigPath
$approvalInbox = Read-JsonFile -Path $approvalInboxPath
$workerRegistry = Read-JsonFile -Path $workerRegistryPath

$stalePackets = @()
if ($queueHealth -and $queueHealth.stale_packet_visibility) {
    $stalePackets = @($queueHealth.stale_packet_visibility | ForEach-Object {
        [pscustomobject]@{
            packet_id = [string]$_.packet_id
            state = [string]$_.visibility_state
            reason = [string]$_.notes
            next_safe_action = "Review stale packet evidence; do not move packet state without separate APPLY approval."
        }
    })
}

$validatorRecommendations = @()
if ($validatorConfig -and $validatorConfig.validators) {
    $validatorRecommendations = @($validatorConfig.validators | Select-Object -First 5 | ForEach-Object {
        [pscustomobject]@{
            validator_id = [string]$_.name
            priority = "MEDIUM"
            reason = "Validator is registered in the orchestration validator chain."
            next_safe_action = "Use a separately approved validator workflow before running validators."
        }
    })
}

$escalationItems = @()
if ($changedFiles.Count -gt 0) {
    $escalationItems += [pscustomobject]@{
        severity = "REVIEW"
        trigger = "changed_files_present"
        evidence = ($changedFiles -join ", ")
        next_safe_action = "Review changed files before any commit package or protected action."
    }
}
if ($untrackedItems.Count -gt 0) {
    $escalationItems += [pscustomobject]@{
        severity = "REVIEW"
        trigger = "untracked_items_present"
        evidence = ($untrackedItems -join ", ")
        next_safe_action = "Classify untracked items before staging, cleanup, or commit."
    }
}
if (-not $queueHealth) {
    $escalationItems += [pscustomobject]@{
        severity = "WARNING"
        trigger = "queue_health_unavailable"
        evidence = (Get-RelativePathSafe -Path $queueHealthPath)
        next_safe_action = "Restore or review queue health read model before trusting stale packet summaries."
    }
}

$approvalCount = 0
if ($approvalInbox -and $approvalInbox.items) {
    $approvalCount = @($approvalInbox.items).Count
}

$workerCount = 0
if ($workerRegistry -and $workerRegistry.workers) {
    $workerCount = @($workerRegistry.workers).Count
}

$riskLevel = "SAFE"
if ($escalationItems.Count -gt 0) {
    $riskLevel = "WATCH"
}
if (@($escalationItems | Where-Object { $_.severity -eq "BLOCKED" }).Count -gt 0) {
    $riskLevel = "BLOCKED"
}

$nextSafeActions = @(
    [pscustomobject]@{
        rank = 1
        action = "Review overnight supervisor report and escalation items."
        requires_human_approval = $false
        blocked_actions = @("APPLY", "commit", "push", "merge", "worker launch", "packet movement")
    },
    [pscustomobject]@{
        rank = 2
        action = "If escalation items are clear, approve one exact DRY_RUN validator route."
        requires_human_approval = $true
        blocked_actions = @("automatic validator launch", "automatic repair", "automatic APPLY")
    }
)

$packetDrafts = @(
    [pscustomobject]@{
        title = "Review Overnight Supervisor Escalation Items"
        lane = "OVERNIGHT_SUPERVISOR_FOUNDATION"
        mode = "DRY_RUN"
        allowed_paths = @("automation/orchestration/", "docs/workflows/", "docs/architecture/", "schemas/aios/orchestration/")
        forbidden_paths = @("apps/", "services/", "telemetry/", "docs/security/", "secrets/", "credentials/", "broker logic", "live trading logic")
        stop_point = "REPORT_ONLY_NO_APPLY"
    }
)

$report = [pscustomobject]@{
    supervisor_status = $(if ($riskLevel -eq "SAFE") { "READY" } elseif ($riskLevel -eq "BLOCKED") { "BLOCKED" } else { "REVIEW" })
    repo_health = [pscustomobject]@{
        branch = [string]$branchLine
        status_summary = "Read-only git status inspected."
        changed_files = $changedFiles
        untracked_items = $untrackedItems
        risk_level = $riskLevel
    }
    stale_packets = $stalePackets
    validator_recommendations = $validatorRecommendations
    escalation_items = $escalationItems
    next_safe_actions = $nextSafeActions
    packet_drafts = $packetDrafts
    morning_brief = [pscustomobject]@{
        summary = "Overnight Supervisor DRY_RUN inspected repo status, queue health evidence, validator configuration, approval count, and worker count."
        blockers = @($escalationItems | Where-Object { $_.severity -eq "BLOCKED" } | ForEach-Object { $_.trigger })
        review_items = @(
            "changed_files=$($changedFiles.Count)",
            "untracked_items=$($untrackedItems.Count)",
            "stale_packets=$($stalePackets.Count)",
            "validator_recommendations=$($validatorRecommendations.Count)",
            "approval_items=$approvalCount",
            "workers=$workerCount"
        )
        recommended_first_action = "Review escalation summary before approving any validator, APPLY, commit, push, merge, worker launch, or packet movement."
    }
    generated_at = (Get-Date).ToString("s")
    mode = "DRY_RUN"
    authority_boundary = [pscustomobject]@{
        read_only = $true
        approval_authority = "Anthony Meza"
        blocked_capabilities = @(
            "APPLY",
            "write files",
            "move packet state",
            "launch workers",
            "start loops",
            "start daemons",
            "schedule tasks",
            "commit",
            "push",
            "merge",
            "broker execution",
            "live trading",
            "secret handling"
        )
    }
}

if ($QuietJson) {
    $report | ConvertTo-Json -Depth 10
    exit 0
}

Write-Host "AI_OS Overnight Supervisor Plan"
Write-Host "Mode: DRY_RUN"
Write-Host "Supervisor status: $($report.supervisor_status)"
Write-Host "Repo state: $($report.repo_health.branch)"
Write-Host "Changed files: $($report.repo_health.changed_files.Count)"
Write-Host "Untracked items: $($report.repo_health.untracked_items.Count)"
Write-Host "Stale packets: $($report.stale_packets.Count)"
Write-Host "Escalation items: $($report.escalation_items.Count)"
Write-Host ""
Write-Host "Next safe actions:"
foreach ($item in $report.next_safe_actions) {
    Write-Host ("{0}. {1}" -f $item.rank, $item.action)
}
Write-Host ""
Write-Host "Morning brief preview:"
Write-Host $report.morning_brief.summary
Write-Host ("Review items: {0}" -f ($report.morning_brief.review_items -join "; "))
Write-Host ("Recommended first action: {0}" -f $report.morning_brief.recommended_first_action)
Write-Host ""
Write-Host "Mutation skipped: Overnight Supervisor DRY_RUN is read-only."
