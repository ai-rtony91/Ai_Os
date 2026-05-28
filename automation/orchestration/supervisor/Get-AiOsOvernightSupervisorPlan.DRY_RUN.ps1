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

    $rootPath = $repoRoot.Path.TrimEnd("\") + "\"
    $rootUri = [System.Uri]::new($rootPath)
    $pathUri = [System.Uri]::new($resolved.Path)

    return [System.Uri]::UnescapeDataString($rootUri.MakeRelativeUri($pathUri).ToString()).Replace("\", "/")
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
$approvalInboxFolder = Join-Path $repoRoot.Path "automation\orchestration\approval_inbox"
$workPacketFolder = Join-Path $repoRoot.Path "automation\orchestration\work_packets"
$commitPackageFolder = Join-Path $repoRoot.Path "automation\orchestration\commit_packages"
$workerRegistryPath = Join-Path $repoRoot.Path "automation\orchestration\workers\AIOS_WORKER_REGISTRY.json"

$queueHealth = Read-JsonFile -Path $queueHealthPath
$validatorConfig = Read-JsonFile -Path $validatorConfigPath
$approvalInbox = Read-JsonFile -Path $approvalInboxPath
$workerRegistry = Read-JsonFile -Path $workerRegistryPath

function Get-JsonLeafFiles {
    param([string]$Path)

    if (-not (Test-Path -LiteralPath $Path -PathType Container)) {
        return @()
    }

    return @(Get-ChildItem -LiteralPath $Path -File -Filter "*.json" -ErrorAction SilentlyContinue)
}

function Get-PropertyValue {
    param(
        [object]$Object,
        [string[]]$Names,
        [string]$Default = "UNKNOWN"
    )

    if (-not $Object) {
        return $Default
    }

    foreach ($name in $Names) {
        $property = $Object.PSObject.Properties[$name]
        if ($property -and $null -ne $property.Value -and [string]$property.Value -ne "") {
            return [string]$property.Value
        }
    }

    return $Default
}

function Get-ValidatorChainNames {
    param([object]$ValidatorConfig)

    if ($ValidatorConfig -and $ValidatorConfig.validators) {
        return @($ValidatorConfig.validators | Select-Object -First 5 | ForEach-Object { [string]$_.name })
    }

    return @("UNKNOWN")
}

$validatorChainNames = Get-ValidatorChainNames -ValidatorConfig $validatorConfig

$packetJsonFiles = Get-JsonLeafFiles -Path $workPacketFolder
$packetFlow = @()
foreach ($file in $packetJsonFiles) {
    $packet = Read-JsonFile -Path $file.FullName
    $packetId = Get-PropertyValue -Object $packet -Names @("packet_id", "id", "task_id") -Default $file.BaseName
    $lane = Get-PropertyValue -Object $packet -Names @("lane", "worker_lane", "assigned_lane")
    $workerIdentity = Get-PropertyValue -Object $packet -Names @("worker_identity", "worker", "assigned_worker")
    $packetState = Get-PropertyValue -Object $packet -Names @("packet_state", "state", "status") -Default "UNKNOWN"
    $approvalRequired = $false
    $commitPackageCandidate = $false
    $escalationReason = "none"
    $stopCondition = "REPORT_ONLY_NO_MUTATION"

    if ($packetState -match "APPROVAL|APPLY|PROTECTED") {
        $approvalRequired = $true
        $packetState = "APPROVAL_REQUIRED"
        $escalationReason = "Packet state indicates approval or protected action."
    } elseif ($packetState -match "VALIDATOR|VALIDATION") {
        $packetState = "VALIDATOR_REQUIRED"
        $escalationReason = "Packet state indicates validator review is required."
    } elseif ($packetState -match "COMMIT") {
        $approvalRequired = $true
        $commitPackageCandidate = $true
        $packetState = "COMMIT_PACKAGE_CANDIDATE"
        $escalationReason = "Packet state indicates commit package review is required."
    } elseif ($packetState -match "BLOCK") {
        $approvalRequired = $true
        $packetState = "BLOCKED"
        $escalationReason = "Packet state is blocked."
    } elseif ($packetState -match "STALE") {
        $packetState = "STALE"
        $escalationReason = "Packet state is stale."
    } else {
        $packetState = "READY_FOR_REVIEW"
    }

    if ($lane -eq "UNKNOWN" -or $workerIdentity -eq "UNKNOWN") {
        $packetState = "BLOCKED"
        $approvalRequired = $true
        $escalationReason = "Packet is missing lane or worker identity evidence."
        $stopCondition = "MISSING_PACKET_IDENTITY"
    }

    $packetFlow += [pscustomobject]@{
        packet_id = $packetId
        lane = $lane
        worker_identity = $workerIdentity
        validator_chain = $validatorChainNames
        approval_required = $approvalRequired
        escalation_reason = $escalationReason
        stop_condition = $stopCondition
        packet_state = $packetState
        report_target = "morning_brief"
        commit_package_candidate = $commitPackageCandidate
        next_safe_action = "Review packet evidence; do not move packet state without separate APPLY approval."
    }
}

if ($packetFlow.Count -eq 0) {
    $packetFlow = @(
        [pscustomobject]@{
            packet_id = "NO_PACKET_FILES_FOUND"
            lane = "UNKNOWN"
            worker_identity = "UNKNOWN"
            validator_chain = $validatorChainNames
            approval_required = $false
            escalation_reason = "No work packet JSON files were available for classification."
            stop_condition = "REPORT_ONLY_NO_PACKET_MOVEMENT"
            packet_state = "UNKNOWN"
            report_target = "morning_brief"
            commit_package_candidate = $false
            next_safe_action = "Add or route a packet through the approved work packet workflow before execution."
        }
    )
}

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

$validatorResults = @()
if ($validatorConfig -and $validatorConfig.validators) {
    $validatorResults = @($validatorConfig.validators | Select-Object -First 5 | ForEach-Object {
        [pscustomobject]@{
            validator_id = [string]$_.name
            state = "NOT_RUN"
            evidence = "Validator is configured; Overnight Supervisor does not execute validators automatically."
            next_safe_action = "Run only through a separately approved DRY_RUN validator packet."
        }
    })
} else {
    $validatorResults = @(
        [pscustomobject]@{
            validator_id = "UNKNOWN"
            state = "UNKNOWN"
            evidence = "Validator chain configuration was unavailable."
            next_safe_action = "Restore validator chain evidence before APPLY, commit, push, or merge."
        }
    )
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

$approvalJsonFiles = Get-JsonLeafFiles -Path $approvalInboxFolder
$approvalRequired = @($packetFlow | Where-Object { $_.approval_required } | ForEach-Object {
    [pscustomobject]@{
        packet_id = [string]$_.packet_id
        reason = [string]$_.escalation_reason
        approval_authority = "Anthony Meza"
        next_safe_action = "Request Human Owner review before any protected action or mutation."
    }
})
if ($approvalRequired.Count -eq 0 -and ($approvalCount -gt 0 -or $approvalJsonFiles.Count -gt 0)) {
    $approvalRequired = @(
        [pscustomobject]@{
            packet_id = "APPROVAL_INBOX_REVIEW"
            reason = "Approval inbox evidence exists and should be reviewed before protected actions."
            approval_authority = "Anthony Meza"
            next_safe_action = "Inspect approval inbox through a read-only approval workflow."
        }
    )
}

$workerCount = 0
if ($workerRegistry -and $workerRegistry.workers) {
    $workerCount = @($workerRegistry.workers).Count
}

$commitPackageJsonFiles = Get-JsonLeafFiles -Path $commitPackageFolder
$commitPackageCandidates = @($packetFlow | Where-Object { $_.commit_package_candidate } | ForEach-Object {
    [pscustomobject]@{
        packet_id = [string]$_.packet_id
        lane = [string]$_.lane
        candidate_files = @()
        status = "NEEDS_APPROVAL"
        next_safe_action = "Prepare exact-file package only after validation and Human Owner approval."
    }
})
if ($commitPackageCandidates.Count -eq 0 -and $commitPackageJsonFiles.Count -gt 0) {
    $commitPackageCandidates = @($commitPackageJsonFiles | Select-Object -First 5 | ForEach-Object {
        [pscustomobject]@{
            packet_id = $_.BaseName
            lane = "UNKNOWN"
            candidate_files = @((Get-RelativePathSafe -Path $_.FullName))
            status = "READY_FOR_REVIEW"
            next_safe_action = "Review existing commit package candidate; do not stage, commit, push, or merge."
        }
    })
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

$approvalNeeded = $false
if ($escalationItems.Count -gt 0) {
    $approvalNeeded = $true
}

$safeToIgnore = @()
if (@($untrackedItems | Where-Object { $_ -eq ".codex_worktrees/" }).Count -gt 0) {
    $safeToIgnore += ".codex_worktrees/ known local backlog; do not stage."
}
if ($changedFiles.Count -eq 0) {
    $safeToIgnore += "No modified tracked files."
}
if ($safeToIgnore.Count -eq 0) {
    $safeToIgnore += "No safe-to-ignore items identified."
}

$todayFocus = "Review escalation items, then choose one safe next action."
if ($escalationItems.Count -eq 0) {
    $todayFocus = "Repo looks clear for the next approved planning or validation step."
}

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
    packet_flow = $packetFlow
    validator_recommendations = $validatorRecommendations
    validator_results = $validatorResults
    approval_required = $approvalRequired
    commit_package_candidates = $commitPackageCandidates
    escalation_items = $escalationItems
    next_safe_actions = $nextSafeActions
    packet_drafts = $packetDrafts
    morning_brief = [pscustomobject]@{
        summary = "Overnight Supervisor DRY_RUN inspected repo status, queue health evidence, validator configuration, approval count, and worker count."
        blockers = @($escalationItems | Where-Object { $_.severity -eq "BLOCKED" } | ForEach-Object { $_.trigger })
        approval_needed = $approvalNeeded
        review_items = @(
            "changed_files=$($changedFiles.Count)",
            "untracked_items=$($untrackedItems.Count)",
            "stale_packets=$($stalePackets.Count)",
            "classified_packets=$($packetFlow.Count)",
            "validator_recommendations=$($validatorRecommendations.Count)",
            "validator_results=$($validatorResults.Count)",
            "approval_required=$($approvalRequired.Count)",
            "commit_package_candidates=$($commitPackageCandidates.Count)",
            "approval_items=$approvalCount",
            "workers=$workerCount"
        )
        recommended_first_action = "Review escalation summary before approving any validator, APPLY, commit, push, merge, worker launch, or packet movement."
        safe_to_ignore = $safeToIgnore
        today_focus = $todayFocus
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
Write-Host "Classified packets: $($report.packet_flow.Count)"
Write-Host "Approval-required items: $($report.approval_required.Count)"
Write-Host "Commit package candidates: $($report.commit_package_candidates.Count)"
Write-Host "Escalation items: $($report.escalation_items.Count)"
Write-Host ""
Write-Host "Next safe actions:"
foreach ($item in $report.next_safe_actions) {
    Write-Host ("{0}. {1}" -f $item.rank, $item.action)
}
Write-Host ""
Write-Host "Morning brief preview:"
Write-Host "STATUS"
Write-Host ("{0} - risk {1}" -f $report.supervisor_status, $report.repo_health.risk_level)
Write-Host ""
Write-Host "WHAT CHANGED"
Write-Host ("Changed files: {0}" -f $report.repo_health.changed_files.Count)
Write-Host ("Untracked items: {0}" -f $report.repo_health.untracked_items.Count)
Write-Host ""
Write-Host "BLOCKED BY"
if ($report.morning_brief.blockers.Count -gt 0) {
    $report.morning_brief.blockers | ForEach-Object { Write-Host ("- {0}" -f $_) }
} else {
    Write-Host "None."
}
Write-Host ""
Write-Host "NEEDS ANTHONY APPROVAL"
Write-Host $(if ($report.morning_brief.approval_needed) { "YES - review escalation items before protected action." } else { "NO - no escalation item requires approval right now." })
Write-Host ""
Write-Host "SAFE NEXT ACTION"
Write-Host $report.next_safe_actions[0].action
Write-Host ""
Write-Host "SAFE TO IGNORE"
$report.morning_brief.safe_to_ignore | ForEach-Object { Write-Host ("- {0}" -f $_) }
Write-Host ""
Write-Host "TODAY FOCUS"
Write-Host ("⚡ {0}" -f $report.morning_brief.today_focus)
Write-Host ""
Write-Host "Mutation skipped: Overnight Supervisor DRY_RUN is read-only."
