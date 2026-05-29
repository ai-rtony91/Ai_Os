[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$GoalText,

    [string]$PacketId,
    [string]$WorkerHint,
    [string[]]$ChangedPaths = @(),

    [ValidateSet("LOW", "MEDIUM", "HIGH", "CRITICAL")]
    [string]$RiskTier = "MEDIUM",

    [string]$OutputDirectory = "telemetry/auto_loop/reports",
    [string]$StateDirectory = "automation/orchestration/auto_loop/state",
    [switch]$WriteSandboxState,
    [switch]$NoWrite
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

function Test-AiOsPathInside {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$AllowedRoot
    )

    $fullPath = Get-AiOsFullPath -Path $Path
    $fullRoot = Get-AiOsFullPath -Path $AllowedRoot
    return $fullPath.StartsWith($fullRoot, [System.StringComparison]::OrdinalIgnoreCase)
}

function Normalize-AiOsPath {
    param([string]$Path)

    if (-not $Path) { return "" }
    return (($Path -replace "\\", "/").Trim()).TrimStart("/")
}

function Test-AiOsPathOverlap {
    param(
        [Parameter(Mandatory = $true)][string]$Left,
        [Parameter(Mandatory = $true)][string]$Right
    )

    $a = (Normalize-AiOsPath -Path $Left).TrimEnd("/")
    $b = (Normalize-AiOsPath -Path $Right).TrimEnd("/")
    if (-not $a -or -not $b) { return $false }
    return ($a -eq $b -or $a.StartsWith("$b/", [System.StringComparison]::OrdinalIgnoreCase) -or $b.StartsWith("$a/", [System.StringComparison]::OrdinalIgnoreCase))
}

function ConvertTo-AiOsArray {
    param([string[]]$Values)

    $items = [System.Collections.Generic.List[string]]::new()
    foreach ($value in $Values) {
        if (-not $value) { continue }
        foreach ($part in ($value -split ",")) {
            $clean = $part.Trim().Trim('"').Trim("'")
            if ($clean) {
                $items.Add((Normalize-AiOsPath -Path $clean))
            }
        }
    }

    return @($items | Where-Object { $_ } | Select-Object -Unique)
}

function Write-AiOsJsonRecord {
    param(
        [Parameter(Mandatory = $true)][object]$Record,
        [Parameter(Mandatory = $true)][string]$Path
    )

    $parent = Split-Path -Parent $Path
    if (-not (Test-AiOsPathInside -Path $parent -AllowedRoot "automation/orchestration/auto_loop/state") -and
        -not (Test-AiOsPathInside -Path $parent -AllowedRoot "telemetry/auto_loop/reports")) {
        throw "Refusing to write outside auto-loop sandbox: $Path"
    }

    New-Item -ItemType Directory -Force -Path $parent | Out-Null
    $json = $Record | ConvertTo-Json -Depth 20
    Set-Content -LiteralPath $Path -Value ($json + [Environment]::NewLine) -Encoding UTF8
}

function Invoke-AiOsCommand {
    param([Parameter(Mandatory = $true)][string]$Command)

    $output = & powershell -NoProfile -Command $Command 2>&1
    [ordered]@{
        command = $Command
        exit_code = $LASTEXITCODE
        output = @($output | ForEach-Object { $_.ToString() })
    }
}

function Get-AiOsWorkerAssignmentRecord {
    param(
        [string]$PacketId,
        [string]$GoalText,
        [string]$WorkerHint,
        [string[]]$ChangedPaths,
        [string]$CreatedAt
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
        assignment_id = "ASSIGNMENT_$PacketId"
        packet_id = $PacketId
        created_at = $CreatedAt
        worker_hint = if ($WorkerHint) { $WorkerHint } else { $null }
        recommended_worker_id = $workerId
        recommended_worker_type = $workerType
        recommended_lane = $lane
        assigned_paths = @($ChangedPaths)
        assignment_reason = $reason
        assignment_state = "RECOMMENDATION_ONLY"
        worker_registry_checked = Test-Path -LiteralPath "automation/orchestration/workers/AIOS_WORKER_REGISTRY.json"
        worker_profiles_checked = Test-Path -LiteralPath "automation/orchestration/workers/AIOS_WORKER_PROFILES.json"
        worker_inbox_checked = Test-Path -LiteralPath "automation/orchestration/workers/inbox/AIOS_WORKER_INBOX.json"
        active_registry_mutation_performed = $false
        human_approval_required = $true
        next_safe_action = "Human Owner reviews worker recommendation before any active assignment or inbox write."
    }
}

function Get-AiOsLockRecord {
    param(
        [string]$PacketId,
        [string]$WorkerId,
        [string[]]$ChangedPaths,
        [string]$CreatedAt,
        [datetime]$Now,
        [string]$StateDirectory
    )

    $lockSources = [System.Collections.Generic.List[string]]::new()
    foreach ($root in @("automation/orchestration/locks", "automation/orchestration/validators", (Join-Path $StateDirectory "locks"))) {
        if (Test-Path -LiteralPath $root) {
            Get-ChildItem -Path $root -Recurse -File -ErrorAction SilentlyContinue |
                Where-Object { $_.FullName -notmatch "__pycache__" -and $_.Name -match "lock|LOCK" } |
                ForEach-Object { $lockSources.Add($_.FullName) }
        }
    }

    $existingPaths = [System.Collections.Generic.List[string]]::new()
    foreach ($source in $lockSources) {
        try {
            $text = Get-Content -Raw -LiteralPath $source -ErrorAction Stop
            if ($source.EndsWith(".json", [System.StringComparison]::OrdinalIgnoreCase)) {
                $json = $text | ConvertFrom-Json
                foreach ($name in @("paths_requested", "locked_paths", "claimed_paths", "assigned_paths")) {
                    if ($json.PSObject.Properties.Name -contains $name) {
                        foreach ($path in @($json.$name)) {
                            if ($path) { $existingPaths.Add((Normalize-AiOsPath -Path ([string]$path))) }
                        }
                    }
                }
            } else {
                foreach ($path in $ChangedPaths) {
                    if ($text.IndexOf($path, [System.StringComparison]::OrdinalIgnoreCase) -ge 0) {
                        $existingPaths.Add((Normalize-AiOsPath -Path $path))
                    }
                }
            }
        } catch {
            continue
        }
    }

    $overlaps = [System.Collections.Generic.List[string]]::new()
    foreach ($requested in $ChangedPaths) {
        foreach ($existing in @($existingPaths | Select-Object -Unique)) {
            if (Test-AiOsPathOverlap -Left $requested -Right $existing) {
                $overlaps.Add("$requested overlaps $existing")
            }
        }
    }

    $conflict = $overlaps.Count -gt 0
    $state = if ($conflict) { "BLOCKED" } elseif ($lockSources.Count -eq 0) { "WARN_MANUAL_REVIEW" } else { "LOCK_RECORD_READY" }
    $reason = if ($conflict) { "Requested path overlaps existing lock-related evidence." } elseif ($lockSources.Count -eq 0) { "No existing active lock files found; manual review required before promotion." } else { $null }
    $next = if ($conflict) { "Resolve path ownership conflict before any active lock write." } else { "Human Owner reviews lock record before promotion to active lock registry." }

    [ordered]@{
        lock_id = "LOCK_$PacketId"
        packet_id = $PacketId
        worker_id = $WorkerId
        created_at = $CreatedAt
        expires_at_preview = $Now.AddHours(8).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
        paths_requested = @($ChangedPaths)
        lock_scope = "auto_loop_sandbox_path_record"
        existing_lock_sources_checked = @($lockSources)
        overlapping_paths = @($overlaps)
        conflict_detected = $conflict
        conflict_reason = $reason
        lock_state = $state
        active_lock_mutation_performed = $false
        human_approval_required = $true
        next_safe_action = $next
    }
}

function Get-AiOsValidatorRunRecord {
    param(
        [string]$PacketId,
        [string[]]$ChangedPaths,
        [string]$CreatedAt
    )

    $required = [System.Collections.Generic.List[string]]::new()
    $optional = [System.Collections.Generic.List[string]]::new()
    $skipped = [System.Collections.Generic.List[string]]::new()
    $commandsRun = [System.Collections.Generic.List[object]]::new()
    $commandsRecommended = [System.Collections.Generic.List[string]]::new()
    $blocked = [System.Collections.Generic.List[string]]::new()
    $routes = [System.Collections.Generic.List[object]]::new()

    $autoLoopTouched = $false
    foreach ($path in $ChangedPaths) {
        $normalized = Normalize-AiOsPath -Path $path
        if ($normalized -match "^automation/orchestration/auto_loop") {
            $autoLoopTouched = $true
            $required.Add("PowerShell parse: automation/orchestration/auto_loop/scripts/*.ps1")
            $required.Add("JSON parse: automation/orchestration/auto_loop/templates/*.json")
            $required.Add("git diff --check")
            $routes.Add([ordered]@{ path = $normalized; category = "auto_loop"; state = "SAFE_LOCAL_VALIDATION_ALLOWED" })
        } elseif ($normalized -match "^(docs/governance|docs/workflows)") {
            $required.Add("git diff --check")
            $required.Add("manual governance/workflow review")
            $routes.Add([ordered]@{ path = $normalized; category = "governance_docs"; state = "PLAN_ONLY" })
        } elseif ($normalized -match "^apps/dashboard") {
            $required.Add("dashboard lint/build plan if package scripts exist")
            $commandsRecommended.Add("npm --prefix apps/dashboard run build")
            $routes.Add([ordered]@{ path = $normalized; category = "dashboard"; state = "PLAN_ONLY" })
        } elseif ($normalized -match "trading_lab|trading") {
            $required.Add("paper-only Trading Lab safety validation")
            $commandsRecommended.Add("paper-only safety tests and manual review")
            $routes.Add([ordered]@{ path = $normalized; category = "paper_only_trading_lab"; state = "PLAN_ONLY_PAPER_ONLY" })
        } else {
            $required.Add("manual validator review")
            $blocked.Add("unknown path requires manual validator review")
            $routes.Add([ordered]@{ path = $normalized; category = "unknown"; state = "MANUAL_REVIEW_REQUIRED" })
        }
    }

    if ($autoLoopTouched) {
        $commandsRun.Add((Invoke-AiOsCommand -Command "Get-ChildItem automation/orchestration/auto_loop/scripts -Filter *.ps1 | ForEach-Object { `$tokens = `$null; `$errors = `$null; `$null = [System.Management.Automation.Language.Parser]::ParseFile(`$_.FullName, [ref]`$tokens, [ref]`$errors); if (`$errors -and `$errors.Count -gt 0) { exit 1 } }"))
        $commandsRun.Add((Invoke-AiOsCommand -Command "Get-ChildItem automation/orchestration/auto_loop/templates -Filter *.json | ForEach-Object { Get-Content -Raw `$_.FullName | ConvertFrom-Json | Out-Null }"))
        $commandsRun.Add((Invoke-AiOsCommand -Command "git diff --check"))
    } else {
        $skipped.Add("Safe local auto-loop validators skipped because ChangedPaths do not target automation/orchestration/auto_loop.")
    }

    $failedCommands = @($commandsRun | Where-Object { $_.exit_code -ne 0 })
    $validationState = if ($failedCommands.Count -gt 0) { "FAILED" } elseif ($blocked.Count -gt 0) { "MANUAL_REVIEW_REQUIRED" } elseif ($autoLoopTouched) { "PASSED_SAFE_LOCAL_CHECKS" } else { "PLAN_ONLY" }
    $validationResult = if ($validationState -eq "FAILED") { "BLOCK" } elseif ($validationState -eq "MANUAL_REVIEW_REQUIRED") { "WARN" } else { "PASS" }

    [ordered]@{
        validator_run_id = "VALIDATOR_RUN_$PacketId"
        packet_id = $PacketId
        created_at = $CreatedAt
        changed_paths = @($ChangedPaths)
        validator_plan = @($routes)
        validators_required = @($required | Select-Object -Unique)
        validators_optional = @($optional | Select-Object -Unique)
        validators_run = @($commandsRun)
        validators_skipped = @($skipped)
        validation_state = $validationState
        validation_result = $validationResult
        blocked_reason = if ($failedCommands.Count -gt 0) { "One or more safe local validators failed." } elseif ($blocked.Count -gt 0) { ($blocked -join "; ") } else { $null }
        commands_run = @($commandsRun | ForEach-Object { $_.command })
        commands_recommended = @($commandsRecommended | Select-Object -Unique)
        next_safe_action = "Human Owner reviews validator run record before approving APPLY, commit, push, merge, or protected action."
    }
}

function Get-AiOsApprovalRecord {
    param(
        [string]$PacketId,
        [string]$RiskTier,
        [string]$ValidatorResult,
        [string]$CreatedAt,
        [string]$ApprovalRecordPath
    )

    $state = "APPROVAL_REQUIRED"
    $blockedReason = $null
    $next = "Human Owner approval required before APPLY, commit, push, merge, runtime mutation, worker dispatch, or protected action."

    if ($RiskTier -eq "LOW") {
        $next = "Human Owner may fast-review this low-risk sandbox record before any APPLY or commit lane."
    } elseif ($RiskTier -eq "HIGH") {
        $next = "Human Owner approval plus validator proof required before any APPLY or commit lane."
    } elseif ($RiskTier -eq "CRITICAL") {
        $state = "BLOCKED"
        $blockedReason = "CRITICAL risk requires a separate explicit approval packet."
        $next = "Create a separate critical-risk approval packet before continuing."
    }

    [ordered]@{
        approval_id = "APPROVAL_$PacketId"
        packet_id = $PacketId
        created_at = $CreatedAt
        requested_action = "Review gated-write sandbox records and decide whether to promote through a future approved lane."
        risk_tier = $RiskTier
        validator_result = $ValidatorResult
        approval_state = $state
        approval_required = $true
        required_approver = "Human Owner"
        active_inbox_mutation_performed = $false
        active_inbox_path = "automation/orchestration/approval_inbox/APPROVAL_INBOX_001.json"
        sandbox_approval_record_path = $ApprovalRecordPath
        blocked_reason = $blockedReason
        next_safe_action = $next
    }
}

function Get-AiOsCommitPackageRecommendation {
    param(
        [string]$PacketId,
        [string[]]$ChangedPaths
    )

    $safe = [System.Collections.Generic.List[string]]::new()
    $risky = [System.Collections.Generic.List[string]]::new()
    $forbidden = [System.Collections.Generic.List[string]]::new()
    foreach ($path in $ChangedPaths) {
        $normalized = Normalize-AiOsPath -Path $path
        if ($normalized -match "^automation/orchestration/auto_loop/") {
            $safe.Add($normalized)
        } elseif ($normalized -match "^(telemetry/auto_loop/reports|telemetry/backup_reports|telemetry/night_supervisor)") {
            $risky.Add($normalized)
        } elseif ($normalized -match "^(automation/orchestration/work_packets|automation/orchestration/approval_inbox|automation/orchestration/workers|automation/orchestration/command_queue|telemetry/runtime|services/|apps/trading_lab/trading_lab/execution|broker|OANDA|secrets|credentials)") {
            $forbidden.Add($normalized)
        } else {
            $risky.Add($normalized)
        }
    }

    [ordered]@{
        packet_id = $PacketId
        safe_files_to_stage = @($safe | Select-Object -Unique)
        files_to_exclude = @("telemetry/auto_loop/reports/", "telemetry/backup_reports/", "telemetry/night_supervisor/")
        risky_files_to_review = @($risky | Select-Object -Unique)
        generated_files_to_exclude = @("telemetry/auto_loop/reports/")
        forbidden_files = @($forbidden | Select-Object -Unique)
        suggested_commit_message = "Add repo-loop gated-write sandbox"
        recommended_git_add_commands = @($safe | Select-Object -Unique | ForEach-Object { "git add -- `"$($_)`"" })
        git_add_dot_allowed = $false
        commit_allowed = $false
        push_allowed = $false
        human_approval_required = $true
        next_safe_action = "Human Owner reviews explicit commit package recommendation in a separate commit packet."
    }
}

if (-not (Test-AiOsPathInside -Path $OutputDirectory -AllowedRoot "telemetry/auto_loop/reports")) {
    throw "OutputDirectory must stay under telemetry/auto_loop/reports."
}
if (-not (Test-AiOsPathInside -Path $StateDirectory -AllowedRoot "automation/orchestration/auto_loop/state")) {
    throw "StateDirectory must stay under automation/orchestration/auto_loop/state."
}

$repoRoot = (Get-Location).Path
$branch = (& git branch --show-current).Trim()
$remoteText = (& git remote -v) -join "`n"
if ($repoRoot -ne "C:\Dev\Ai.Os") { throw "Wrong worktree: $repoRoot" }
if ($branch -ne "main") { throw "Wrong branch: $branch" }
if ($remoteText -notmatch "ai-rtony91/Ai_Os") { throw "Wrong repository remote." }

$now = Get-Date
$createdAt = $now.ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
$stamp = $now.ToUniversalTime().ToString("yyyyMMddTHHmmssZ")
if (-not $PacketId) {
    $PacketId = "AIOS-AUTO-LOOP-GATED-$stamp"
}

$changed = ConvertTo-AiOsArray -Values $ChangedPaths
if ($changed.Count -eq 0) {
    $changed = @("automation/orchestration/auto_loop/")
}

$shouldWrite = -not $NoWrite
$packetDir = Join-Path $StateDirectory "packets"
$lockDir = Join-Path $StateDirectory "locks"
$approvalDir = Join-Path $StateDirectory "approvals"
$validatorDir = Join-Path $StateDirectory "validator_runs"
$runtimeDir = Join-Path $StateDirectory "runtime_snapshots"
$resumeDir = Join-Path $StateDirectory "resume"

$packetRecordPath = Join-Path $packetDir "PACKET_$PacketId.json"
$lockRecordPath = Join-Path $lockDir "LOCK_$PacketId.json"
$approvalRecordPath = Join-Path $approvalDir "APPROVAL_$PacketId.json"
$validatorRecordPath = Join-Path $validatorDir "VALIDATOR_RUN_$PacketId.json"
$runtimeSnapshotPath = Join-Path $runtimeDir "RUNTIME_SNAPSHOT_$PacketId.json"
$resumeRecordPath = Join-Path $resumeDir "RESUME_$PacketId.json"
$reportPath = Join-Path $OutputDirectory "AUTO_LOOP_GATED_WRITE_REPORT_$stamp.json"

$workerAssignment = Get-AiOsWorkerAssignmentRecord -PacketId $PacketId -GoalText $GoalText -WorkerHint $WorkerHint -ChangedPaths $changed -CreatedAt $createdAt
$lockRecord = Get-AiOsLockRecord -PacketId $PacketId -WorkerId $workerAssignment.recommended_worker_id -ChangedPaths $changed -CreatedAt $createdAt -Now $now -StateDirectory $StateDirectory
$validatorRecord = Get-AiOsValidatorRunRecord -PacketId $PacketId -ChangedPaths $changed -CreatedAt $createdAt
$approvalRecord = Get-AiOsApprovalRecord -PacketId $PacketId -RiskTier $RiskTier -ValidatorResult $validatorRecord.validation_result -CreatedAt $createdAt -ApprovalRecordPath $approvalRecordPath
$commitPackage = Get-AiOsCommitPackageRecommendation -PacketId $PacketId -ChangedPaths $changed

$packetState = if ($approvalRecord.approval_state -eq "BLOCKED" -or $lockRecord.lock_state -eq "BLOCKED") { "BLOCKED" } else { "APPROVAL_REQUIRED" }
$packetRecord = [ordered]@{
    packet_id = $PacketId
    created_at = $createdAt
    updated_at = $createdAt
    goal_text = $GoalText
    packet_state = $packetState
    branch = $branch
    worktree = $repoRoot
    repo = "ai-rtony91/Ai_Os"
    worker_recommendation = $workerAssignment
    changed_paths = @($changed)
    allowed_paths = @("automation/orchestration/auto_loop/", "telemetry/auto_loop/")
    forbidden_paths = @("automation/orchestration/work_packets/", "automation/orchestration/approval_inbox/", "automation/orchestration/workers/", "automation/orchestration/command_queue/", "telemetry/runtime/", "telemetry/work_ledger.jsonl", "broker/", "OANDA/", "secrets/", "credentials/")
    protected_paths = @("AGENTS.md", "README.md", "docs/governance/", "docs/workflows/", "docs/security/", "apps/trading_lab/trading_lab/execution/")
    risk_tier = $RiskTier
    validator_status = $validatorRecord.validation_result
    approval_status = $approvalRecord.approval_state
    lock_status = $lockRecord.lock_state
    commit_package_status = "RECOMMENDATION_ONLY"
    runtime_state_status = "SANDBOX_SNAPSHOT_READY"
    resume_status = "RESUME_RECORD_READY"
    human_approval_required = $true
    blocked_actions = @("commit", "push", "merge", "live_trading", "broker_execution", "secret_access", "active_queue_mutation", "active_inbox_mutation", "runtime_mutation")
    next_safe_action = "Human Owner reviews sandbox packet, approval, validator, runtime, resume, and commit package records."
}

$runtimeSnapshot = [ordered]@{
    snapshot_id = "RUNTIME_SNAPSHOT_$PacketId"
    packet_id = $PacketId
    created_at = $createdAt
    active_goal = $GoalText
    active_worker = $workerAssignment.recommended_worker_id
    active_branch = $branch
    active_step = "GATED_WRITE_SANDBOX_RECORDS_CREATED"
    active_stop_point = "HUMAN_APPROVAL_REQUIRED"
    next_safe_action = "Human Owner reviews sandbox records before any active system promotion."
    last_validator_result = $validatorRecord.validation_result
    approval_status = $approvalRecord.approval_state
    commit_package_status = "RECOMMENDATION_ONLY"
    resume_record_path = $resumeRecordPath
    source_report_path = $reportPath
    active_runtime_mutation_performed = $false
    active_runtime_target_path = "telemetry/runtime/"
    safe_to_promote_later = $false
}

$resumePrompt = "Resume from packet_id $PacketId using automation/orchestration/auto_loop/state/resume/RESUME_$PacketId.json. Do not guess missing state."
$resumeRecord = [ordered]@{
    resume_id = "RESUME_$PacketId"
    packet_id = $PacketId
    created_at = $createdAt
    current_step = "HUMAN_APPROVAL_REQUIRED"
    last_completed_step = "SANDBOX_GATED_WRITE_RECORDS_CREATED"
    next_required_step = "Human Owner reviews and approves or rejects promotion packet."
    stop_reason = "Supervised auto-loop stopped at human gate."
    packet_record_path = $packetRecordPath
    approval_record_path = $approvalRecordPath
    validator_record_path = $validatorRecordPath
    runtime_snapshot_path = $runtimeSnapshotPath
    report_path = $reportPath
    human_resume_instruction = "Review the gated-write report and decide whether to promote sandbox records into active gated systems."
    codex_resume_prompt = $resumePrompt
    resume_state = "READY_FOR_HUMAN_REVIEW"
}

$report = [ordered]@{
    report_id = "AUTO_LOOP_GATED_WRITE_REPORT_$stamp"
    created_at = $createdAt
    packet_id = $PacketId
    goal_text = $GoalText
    repo = "ai-rtony91/Ai_Os"
    branch = $branch
    worktree = $repoRoot
    packet_record_path = $packetRecordPath
    lock_record_path = $lockRecordPath
    approval_record_path = $approvalRecordPath
    validator_run_record_path = $validatorRecordPath
    runtime_snapshot_path = $runtimeSnapshotPath
    resume_record_path = $resumeRecordPath
    commit_package_recommendation = $commitPackage
    safety_status = [ordered]@{
        live_trading_enabled = $false
        broker_execution_added = $false
        active_approval_inbox_mutated = $false
        active_worker_registry_mutated = $false
        active_command_queue_mutated = $false
        active_packet_queue_mutated = $false
        runtime_state_mutated = $false
        telemetry_runtime_mutated = $false
        staging_performed = $false
        commit_performed = $false
        push_performed = $false
    }
    blocked_actions = @("commit", "push", "merge", "live_trading", "broker_execution", "secret_access", "active_queue_mutation", "active_approval_inbox_mutation", "active_worker_registry_mutation", "runtime_mutation")
    active_state_mutation_summary = "No active production queue, inbox, registry, runtime, telemetry/runtime, or work ledger mutation performed. Sandbox records only."
    next_human_action = "Review gated-write sandbox records and approve a future promotion packet if acceptable."
    records = [ordered]@{
        packet_record = $packetRecord
        lock_record = $lockRecord
        approval_record = $approvalRecord
        validator_run_record = $validatorRecord
        runtime_snapshot = $runtimeSnapshot
        resume_record = $resumeRecord
    }
}

if ($shouldWrite) {
    foreach ($dir in @($packetDir, $lockDir, $approvalDir, $validatorDir, $runtimeDir, $resumeDir, $OutputDirectory)) {
        New-Item -ItemType Directory -Force -Path $dir | Out-Null
    }
    Write-AiOsJsonRecord -Record $packetRecord -Path $packetRecordPath
    Write-AiOsJsonRecord -Record $lockRecord -Path $lockRecordPath
    Write-AiOsJsonRecord -Record $approvalRecord -Path $approvalRecordPath
    Write-AiOsJsonRecord -Record $validatorRecord -Path $validatorRecordPath
    Write-AiOsJsonRecord -Record $runtimeSnapshot -Path $runtimeSnapshotPath
    Write-AiOsJsonRecord -Record $resumeRecord -Path $resumeRecordPath
    Write-AiOsJsonRecord -Record $report -Path $reportPath
}

$summary = [ordered]@{
    packet_id = $PacketId
    packet_record = if ($shouldWrite) { $packetRecordPath } else { "NO_WRITE" }
    lock_record = if ($shouldWrite) { $lockRecordPath } else { "NO_WRITE" }
    approval_record = if ($shouldWrite) { $approvalRecordPath } else { "NO_WRITE" }
    validator_run_record = if ($shouldWrite) { $validatorRecordPath } else { "NO_WRITE" }
    runtime_snapshot = if ($shouldWrite) { $runtimeSnapshotPath } else { "NO_WRITE" }
    resume_record = if ($shouldWrite) { $resumeRecordPath } else { "NO_WRITE" }
    report_path = if ($shouldWrite) { $reportPath } else { "NO_WRITE" }
    packet_state = $packetRecord.packet_state
    lock_state = $lockRecord.lock_state
    approval_state = $approvalRecord.approval_state
    validation_result = $validatorRecord.validation_result
    commit_allowed = $false
    push_allowed = $false
    next_human_action = $report.next_human_action
    did = @("Created local gated-write sandbox records and a consolidated report when writing was enabled.")
    did_not = @("Did not mutate active queues, approval inbox, worker registry, command queue, runtime state, telemetry/runtime, work ledger, broker paths, stage, commit, push, merge, or rebase.")
}

Write-Output ($summary | ConvertTo-Json -Depth 12)
