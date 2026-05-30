[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$GoalText,

    [string]$PacketId,
    [string]$WorkerHint,
    [string[]]$ChangedPaths = @(),

    [ValidateSet("LOW", "MEDIUM", "HIGH", "CRITICAL")]
    [string]$RiskTier = "MEDIUM",

    [string]$OutputDirectory = "telemetry/auto_loop/reports"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-AiOsFullPath {
    param([Parameter(Mandatory = $true)][string]$Path)

    if ([System.IO.Path]::IsPathRooted($Path)) {
        return [System.IO.Path]::GetFullPath($Path)
    }

    return [System.IO.Path]::GetFullPath((Join-Path (Get-Location).Path $Path))
}

function Test-AiOsOutputDirectory {
    param([Parameter(Mandatory = $true)][string]$Path)

    $allowedRoot = [System.IO.Path]::GetFullPath((Join-Path (Get-Location).Path "telemetry\auto_loop\reports"))
    $fullPath = Get-AiOsFullPath -Path $Path
    return $fullPath.StartsWith($allowedRoot, [System.StringComparison]::OrdinalIgnoreCase)
}

function Normalize-AiOsPath {
    param([string]$Path)
    return (($Path -replace "\\", "/").Trim())
}

function Test-AiOsPathOverlap {
    param(
        [Parameter(Mandatory = $true)][string]$Left,
        [Parameter(Mandatory = $true)][string]$Right
    )

    $a = (Normalize-AiOsPath -Path $Left).TrimEnd("/")
    $b = (Normalize-AiOsPath -Path $Right).TrimEnd("/")
    return ($a -eq $b -or $a.StartsWith("$b/", [System.StringComparison]::OrdinalIgnoreCase) -or $b.StartsWith("$a/", [System.StringComparison]::OrdinalIgnoreCase))
}

function Get-AiOsWorkerAssignment {
    param(
        [string]$PacketId,
        [string]$GoalText,
        [string]$WorkerHint,
        [string[]]$ChangedPaths
    )

    $joined = (($GoalText, ($ChangedPaths -join " ")) -join " ").ToLowerInvariant()
    $workerId = if ($WorkerHint) { $WorkerHint } else { "manual_review" }
    $workerType = "manual_review"
    $lane = "manual review lane"
    $reason = "No confident worker route was identified."

    if ($WorkerHint) {
        $workerType = "operator_hint"
        $lane = "operator-provided worker lane"
        $reason = "WorkerHint was provided and treated as preferred."
    } elseif ($joined -match "docs/governance|docs/workflows|governance|workflow") {
        $workerId = "governance_doc_lane"
        $workerType = "documentation_governance"
        $lane = "governance/doc lane"
        $reason = "Goal or path mentions governance or workflow docs."
    } elseif ($joined -match "automation/orchestration/auto_loop|auto_loop|auto-loop") {
        $workerId = "auto_loop_orchestration_lane"
        $workerType = "orchestration"
        $lane = "auto-loop/orchestration lane"
        $reason = "Goal or path mentions the auto-loop orchestration area."
    } elseif ($joined -match "apps/dashboard|dashboard") {
        $workerId = "dashboard_lane"
        $workerType = "dashboard"
        $lane = "dashboard lane"
        $reason = "Goal or path mentions dashboard files."
    } elseif ($joined -match "trading_lab|trading") {
        $workerId = "trading_lab_paper_only_lane"
        $workerType = "paper_only_trading_lab"
        $lane = "Trading Lab paper-only lane"
        $reason = "Goal or path mentions Trading Lab or trading and must stay paper-only."
    }

    [ordered]@{
        packet_id = $PacketId
        worker_hint = if ($WorkerHint) { $WorkerHint } else { $null }
        recommended_worker_id = $workerId
        recommended_worker_type = $workerType
        recommended_lane = $lane
        reason = $reason
        assigned_paths = @($ChangedPaths)
        worker_registry_found = Test-Path -LiteralPath "automation/orchestration/workers/AIOS_WORKER_REGISTRY.json"
        worker_profiles_found = Test-Path -LiteralPath "automation/orchestration/workers/AIOS_WORKER_PROFILES.json"
        worker_inbox_found = Test-Path -LiteralPath "automation/orchestration/workers/inbox/AIOS_WORKER_INBOX.json"
        assignment_state = "RECOMMENDATION_ONLY"
        human_approval_required = $true
        blocked_reason = $null
    }
}

function Get-AiOsOwnershipLockPreview {
    param(
        [string]$PacketId,
        [string]$WorkerId,
        [string[]]$PathsRequested,
        [datetime]$Now
    )

    $lockSources = @(Get-ChildItem -Path "automation/orchestration" -Recurse -File -ErrorAction SilentlyContinue | Where-Object { $_.Name -match "lock" } | ForEach-Object { $_.FullName })
    $overlaps = [System.Collections.Generic.List[string]]::new()

    foreach ($source in $lockSources) {
        $text = Get-Content -Raw -LiteralPath $source -ErrorAction SilentlyContinue
        foreach ($requested in $PathsRequested) {
            if ($text -and $text.IndexOf((Normalize-AiOsPath -Path $requested), [System.StringComparison]::OrdinalIgnoreCase) -ge 0) {
                $overlaps.Add("$requested in $source")
            }
        }
    }

    $lockState = "LOCK_PREVIEW_READY"
    $conflictDetected = $false
    $conflictReason = $null
    $nextSafeAction = "Review lock preview before any active lock write."

    if ($overlaps.Count -gt 0) {
        $lockState = "BLOCKED"
        $conflictDetected = $true
        $conflictReason = "Requested path appears in existing lock-related source."
        $nextSafeAction = "Resolve ownership conflict before any APPLY lane."
    } elseif ($lockSources.Count -eq 0) {
        $lockState = "WARN_NO_LOCK_DATA"
        $nextSafeAction = "No lock data source found; manual approval required before active lock write."
    }

    [ordered]@{
        lock_preview_id = "LOCK_PREVIEW_{0}" -f (Get-Date -Format "yyyyMMddHHmmss")
        packet_id = $PacketId
        worker_id = $WorkerId
        paths_requested = @($PathsRequested)
        lock_scope = "path_preview_only"
        existing_lock_sources_checked = @($lockSources)
        overlapping_paths = @($overlaps)
        conflict_detected = $conflictDetected
        conflict_reason = $conflictReason
        lock_state = $lockState
        expires_at_preview = $Now.AddHours(8).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
        human_approval_required = $true
        next_safe_action = $nextSafeAction
    }
}

function Get-AiOsValidatorExecutionPlan {
    param(
        [string]$PacketId,
        [string[]]$ChangedPaths
    )

    $routes = [System.Collections.Generic.List[object]]::new()
    $required = [System.Collections.Generic.List[string]]::new()
    $optional = [System.Collections.Generic.List[string]]::new()
    $missing = [System.Collections.Generic.List[string]]::new()
    $found = [System.Collections.Generic.List[string]]::new()
    $blocked = [System.Collections.Generic.List[string]]::new()

    foreach ($path in $ChangedPaths) {
        $normalized = Normalize-AiOsPath -Path $path
        if ($normalized -match "^automation/orchestration/auto_loop") {
            $required.Add("PowerShell parse: automation/orchestration/auto_loop/scripts/*.ps1")
            $required.Add("JSON parse: automation/orchestration/auto_loop/templates/*.json")
            $required.Add("Finish-line DRY_RUN: automation/orchestration/auto_loop/scripts/Test-AiOsAutoLoopFinishLine.DRY_RUN.ps1")
            $routes.Add([ordered]@{ path = $normalized; category = "auto_loop"; state = "STATIC_VALIDATION_READY" })
        } elseif ($normalized -match "^(docs/governance|docs/workflows)") {
            $required.Add("git diff --check")
            $required.Add("manual governance/workflow review")
            $routes.Add([ordered]@{ path = $normalized; category = "governance_docs"; state = "MANUAL_REVIEW_REQUIRED" })
        } elseif ($normalized -match "^apps/dashboard") {
            if (Test-Path -LiteralPath "apps/dashboard/package.json") {
                $required.Add("npm --prefix apps/dashboard run build")
                $found.Add("apps/dashboard/package.json")
            } else {
                $missing.Add("apps/dashboard/package.json")
            }
            $routes.Add([ordered]@{ path = $normalized; category = "dashboard"; state = "DASHBOARD_VALIDATION_PLAN_READY" })
        } elseif ($normalized -match "trading_lab|trading") {
            $required.Add("paper-only Trading Lab safety validation")
            if (Test-Path -LiteralPath "tests/trader") { $found.Add("tests/trader") } else { $missing.Add("tests/trader") }
            if (Test-Path -LiteralPath "automation/trading_lab") { $found.Add("automation/trading_lab") } else { $missing.Add("automation/trading_lab") }
            $routes.Add([ordered]@{ path = $normalized; category = "paper_only_trading_lab"; state = "PAPER_ONLY_SAFETY_PLAN_READY" })
        } else {
            $required.Add("manual validator review")
            $blocked.Add("unknown path requires manual validator review")
            $routes.Add([ordered]@{ path = $normalized; category = "unknown"; state = "MANUAL_REVIEW_REQUIRED" })
        }
    }

    if (Test-Path -LiteralPath "automation/orchestration/validators/Invoke-OrchestrationValidatorChain.DRY_RUN.ps1") {
        $optional.Add("powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/validators/Invoke-OrchestrationValidatorChain.DRY_RUN.ps1")
        $found.Add("automation/orchestration/validators/Invoke-OrchestrationValidatorChain.DRY_RUN.ps1")
    }

    [ordered]@{
        packet_id = $PacketId
        changed_paths = @($ChangedPaths)
        validator_route = @($routes)
        validators_found = @($found | Select-Object -Unique)
        validators_missing = @($missing | Select-Object -Unique)
        required_commands = @($required | Select-Object -Unique)
        optional_commands = @($optional | Select-Object -Unique)
        execution_mode = "DRY_RUN_PLAN_ONLY"
        validation_state = if ($blocked.Count -gt 0) { "MANUAL_REVIEW_REQUIRED" } else { "VALIDATOR_PLAN_READY" }
        blocked_if_missing = @($blocked | Select-Object -Unique)
        next_safe_action = "Review validator plan before executing validators in a separate approved lane."
    }
}

function Get-AiOsApprovalExecutionPlan {
    param(
        [string]$PacketId,
        [string]$RiskTier,
        [string]$ValidatorState
    )

    $state = "APPROVAL_REQUIRED"
    $blockedReason = $null
    $next = "Human Owner reviews approval preview before APPLY, commit, push, merge, or protected action."

    if ($RiskTier -eq "LOW") {
        $next = "Human Owner may fast-review this low-risk preview before any APPLY or commit lane."
    } elseif ($RiskTier -eq "HIGH") {
        $next = "Human Owner approval plus validator proof required before any APPLY or commit lane."
    } elseif ($RiskTier -eq "CRITICAL") {
        $state = "BLOCKED"
        $blockedReason = "CRITICAL risk requires a separate explicit approval packet."
        $next = "Create a separate critical-risk approval packet before continuing."
    }

    [ordered]@{
        approval_preview_id = "APPROVAL_PREVIEW_{0}" -f (Get-Date -Format "yyyyMMddHHmmss")
        packet_id = $PacketId
        requested_action = "Review DRY_RUN repo-loop spine report."
        risk_tier = $RiskTier
        validator_state = $ValidatorState
        approval_required = $true
        required_approver = "Human Owner"
        approval_state = $state
        approval_inbox_found = Test-Path -LiteralPath "automation/orchestration/approval_inbox"
        active_inbox_mutation_allowed = $false
        active_inbox_mutation_performed = $false
        blocked_reason = $blockedReason
        next_safe_action = $next
    }
}

function Get-AiOsCommitPackagePreview {
    param([string]$PacketId)

    $statusLines = @(& git status --porcelain=v1 --untracked-files=all)
    $safe = [System.Collections.Generic.List[string]]::new()
    $exclude = [System.Collections.Generic.List[string]]::new()
    $risky = [System.Collections.Generic.List[string]]::new()
    $generated = [System.Collections.Generic.List[string]]::new()
    $forbidden = [System.Collections.Generic.List[string]]::new()

    foreach ($line in $statusLines) {
        if (-not $line) { continue }
        $path = $line.Substring(3)
        if ($path -match " -> ") { $path = ($path -split " -> ")[-1] }
        $normalized = Normalize-AiOsPath -Path $path

        if ($normalized -match "^telemetry/auto_loop/reports/|^telemetry/backup_reports/|^telemetry/night_supervisor/") {
            $generated.Add($normalized)
            $exclude.Add($normalized)
        } elseif ($normalized -match "^automation/orchestration/auto_loop/|^telemetry/auto_loop/README.md$|^telemetry/auto_loop/examples/") {
            $safe.Add($normalized)
        } elseif ($normalized -match "^automation/orchestration/work_packets/|^automation/orchestration/approval_inbox/|^automation/orchestration/workers/|^automation/orchestration/command_queue/|^telemetry/runtime/|^telemetry/work_ledger.jsonl") {
            $forbidden.Add($normalized)
        } else {
            $risky.Add($normalized)
        }
    }

    [ordered]@{
        packet_id = $PacketId
        safe_files_to_stage = @($safe | Select-Object -Unique)
        files_to_exclude = @($exclude | Select-Object -Unique)
        risky_files_to_review = @($risky | Select-Object -Unique)
        generated_files_to_exclude = @($generated | Select-Object -Unique)
        forbidden_files = @($forbidden | Select-Object -Unique)
        suggested_commit_message = "Add repo-loop spine DRY_RUN preview"
        git_add_dot_allowed = $false
        commit_allowed = $false
        push_allowed = $false
        human_approval_required = $true
        next_safe_action = "Review explicit path recommendations in a separate commit packet. No staging was performed."
    }
}

if (-not (Test-AiOsOutputDirectory -Path $OutputDirectory)) {
    throw "OutputDirectory must be under telemetry/auto_loop/reports."
}

$now = Get-Date
$createdAt = $now.ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
$packetIdValue = if ($PacketId) { $PacketId } else { "AUTO_LOOP_PACKET_{0}" -f (Get-Date -Format "yyyyMMddHHmmss") }
if ($ChangedPaths.Count -eq 0) {
    $ChangedPaths = @("automation/orchestration/auto_loop/")
}

$expandedChangedPaths = [System.Collections.Generic.List[string]]::new()
foreach ($changedPath in $ChangedPaths) {
    foreach ($pathPart in ($changedPath -split ",")) {
        $cleanPath = $pathPart.Trim().Trim('"')
        if ($cleanPath) {
            $expandedChangedPaths.Add($cleanPath)
        }
    }
}
$ChangedPaths = @($expandedChangedPaths)

$branch = (& git branch --show-current 2>$null)
$worktree = (Get-Location).Path
$repo = "ai-rtony91/Ai_Os"

$worker = Get-AiOsWorkerAssignment -PacketId $packetIdValue -GoalText $GoalText -WorkerHint $WorkerHint -ChangedPaths $ChangedPaths
$lock = Get-AiOsOwnershipLockPreview -PacketId $packetIdValue -WorkerId $worker.recommended_worker_id -PathsRequested $ChangedPaths -Now $now
$validator = Get-AiOsValidatorExecutionPlan -PacketId $packetIdValue -ChangedPaths $ChangedPaths
$approval = Get-AiOsApprovalExecutionPlan -PacketId $packetIdValue -RiskTier $RiskTier -ValidatorState $validator.validation_state
$commitPackage = Get-AiOsCommitPackagePreview -PacketId $packetIdValue

$blockedReason = $null
$transitionAllowed = $true
if ($lock.conflict_detected) {
    $transitionAllowed = $false
    $blockedReason = $lock.conflict_reason
}
if ($approval.approval_state -eq "BLOCKED") {
    $transitionAllowed = $false
    $blockedReason = $approval.blocked_reason
}

$movementState = if ($transitionAllowed) { "RESUME_READY" } else { "BLOCKED" }
$movement = [ordered]@{
    packet_id = $packetIdValue
    goal_text = $GoalText
    current_state = $movementState
    previous_state = "DRAFT"
    next_allowed_states = @("READY_FOR_ASSIGNMENT", "ASSIGNED", "LOCK_PREVIEWED", "VALIDATOR_ROUTE_READY", "APPROVAL_REQUIRED", "COMMIT_PACKAGE_READY", "RUNTIME_STATE_PREVIEW_READY", "RESUME_READY", "BLOCKED")
    requested_transition = "RESUME_READY"
    transition_allowed = $transitionAllowed
    transition_blocked_reason = $blockedReason
    required_worker_status = $worker.assignment_state
    required_lock_status = $lock.lock_state
    required_validator_status = $validator.validation_state
    required_approval_status = $approval.approval_state
    required_commit_package_status = "COMMIT_PACKAGE_READY"
    human_approval_required = $true
    blocked_actions = @("active_packet_queue_mutation", "worker_dispatch", "approval_execution", "commit", "push", "merge", "runtime_state_mutation")
    next_safe_action = if ($transitionAllowed) { "Human Owner reviews report and approves the next gated packet." } else { "Resolve blocked preview before continuing." }
}

$reportId = "AUTO_LOOP_REPO_SPINE_REPORT_{0}" -f (Get-Date -Format "yyyyMMddTHHmmssZ")
$reportPath = Join-Path (Get-AiOsFullPath -Path $OutputDirectory) ("$reportId.json")

$resume = [ordered]@{
    packet_id = $packetIdValue
    resume_id = "RESUME_{0}" -f (Get-Date -Format "yyyyMMddHHmmss")
    current_step = $movement.current_state
    last_completed_step = "runtime_state_preview"
    next_required_step = "human_review"
    stop_reason = "DRY_RUN complete; no active state mutation authorized."
    report_path = ($reportPath.Substring((Get-Location).Path.Length + 1) -replace "\\", "/")
    human_prompt_to_resume = "Review the report and approve the next gated packet."
    codex_prompt_to_resume = "Resume from telemetry auto-loop report path $($reportPath.Substring((Get-Location).Path.Length + 1) -replace "\\", "/"). Do not guess missing state."
    created_at = $createdAt
}

$runtimePreview = [ordered]@{
    packet_id = $packetIdValue
    active_goal_preview = $GoalText
    active_worker_preview = $worker.recommended_worker_id
    active_branch = $branch
    active_stop_point = "DRY_RUN report only"
    next_safe_action = "Review runtime preview before any runtime state write."
    last_validator_result_preview = $validator.validation_state
    last_commit_package_preview = "COMMIT_PACKAGE_READY"
    approval_status_preview = $approval.approval_state
    resume_pointer_preview = $resume.resume_id
    active_runtime_mutation_allowed = $false
    active_runtime_mutation_performed = $false
}

$safetyStatus = if ($movement.current_state -eq "BLOCKED") { "BLOCK" } elseif ($lock.lock_state -eq "WARN_NO_LOCK_DATA" -or $validator.validation_state -eq "MANUAL_REVIEW_REQUIRED") { "WARN" } else { "PASS" }

$report = [ordered]@{
    report_id = $reportId
    created_at = $createdAt
    packet_id = $packetIdValue
    goal_text = $GoalText
    repo = $repo
    branch = $branch
    worktree = $worktree
    movement_result = $movement
    worker_assignment_result = $worker
    ownership_lock_result = $lock
    validator_execution_plan = $validator
    approval_execution_plan = $approval
    commit_package_result = $commitPackage
    runtime_state_preview = $runtimePreview
    resume_pointer = $resume
    safety_status = $safetyStatus
    blocked_actions = @("active_queue_mutation", "active_approval_inbox_mutation", "active_worker_registry_mutation", "active_runtime_state_mutation", "worker_dispatch", "staging", "commit", "push", "merge", "rebase", "broker_execution", "secret_access")
    next_human_action = if ($safetyStatus -eq "BLOCK") { "Resolve blocked preview before any APPLY lane." } else { "Review report and approve the next gated packet if the preview is acceptable." }
}

$outputRoot = Split-Path -Parent $reportPath
if (-not (Test-Path -LiteralPath $outputRoot)) {
    New-Item -ItemType Directory -Path $outputRoot -Force | Out-Null
}

$reportJson = $report | ConvertTo-Json -Depth 30
Set-Content -LiteralPath $reportPath -Value ($reportJson + [Environment]::NewLine) -Encoding UTF8

Write-Host "AI_OS Repo-Loop Spine DRY_RUN"
Write-Host "Packet: $packetIdValue"
Write-Host "Safety: $safetyStatus"
Write-Host "Worker lane: $($worker.recommended_lane)"
Write-Host "Lock state: $($lock.lock_state)"
Write-Host "Validator state: $($validator.validation_state)"
Write-Host "Approval state: $($approval.approval_state)"
Write-Host "Commit allowed: False"
Write-Host "Push allowed: False"
Write-Host "Runtime mutation performed: False"
Write-Host "Report: $($resume.report_path)"
Write-Host "Next: $($report.next_human_action)"
