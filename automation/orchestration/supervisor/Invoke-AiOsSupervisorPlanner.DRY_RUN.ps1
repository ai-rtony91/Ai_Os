param(
    [string]$WorkGoal = "Create the supervisor layer that turns a work goal into assigned workers, packets, lanes, validators, and next actions."
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..\..")
$laneRegistryPath = Join-Path $repoRoot "automation\orchestration\terminal_workstations\AIOS_WORKTREE_LANE_REGISTRY.json"
$validatorConfigPath = Join-Path $repoRoot "automation\orchestration\validators\VALIDATOR_CHAIN_CONFIG_001.json"

function Read-JsonFile {
    param([string]$Path)

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return $null
    }

    return Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json
}

function New-WorkerAssignment {
    param(
        [string]$WorkerId,
        [string]$Role,
        [string]$Lane,
        [string]$Task,
        [string[]]$FilesInScope,
        [string[]]$Validators,
        [string]$ApprovalRequired,
        [string]$NextAction
    )

    [pscustomobject]@{
        worker_id = $WorkerId
        role = $Role
        lane = $Lane
        mode = "DRY_RUN_ONLY"
        task = $Task
        files_in_scope = $FilesInScope
        validators = $Validators
        approval_required = $ApprovalRequired
        next_action = $NextAction
        blocked_actions = @(
            "Codex auto-launch",
            "commit",
            "push",
            "scheduled task",
            "startup task",
            "broker connection",
            "API key use",
            "webhook execution",
            "real order",
            "live trading"
        )
    }
}

$laneRegistry = Read-JsonFile -Path $laneRegistryPath
$validatorConfig = Read-JsonFile -Path $validatorConfigPath

$availableLanes = @()
if ($laneRegistry -and $laneRegistry.lanes) {
    $availableLanes = @($laneRegistry.lanes | ForEach-Object { $_.lane_id })
}

$validatorNames = @()
if ($validatorConfig -and $validatorConfig.validators) {
    $validatorNames = @($validatorConfig.validators | Sort-Object order | ForEach-Object { $_.name })
}

$workerAssignments = @(
    New-WorkerAssignment `
        -WorkerId "SUPERVISOR-PLANNER" `
        -Role "Break the work goal into packets, lanes, validators, approval gates, and next safe actions." `
        -Lane "main_control" `
        -Task "Create the assignment plan and stop for operator review." `
        -FilesInScope @(
            "automation/orchestration/supervisor",
            "work_packets",
            "docs/AI_OS/orchestration"
        ) `
        -Validators @(
            "git diff --check",
            "git status --short"
        ) `
        -ApprovalRequired "Human review before APPLY, commit, push, PR creation, or worker launch." `
        -NextAction "Review the plan output and approve only the exact next action."
    New-WorkerAssignment `
        -WorkerId "PACKET-AUTHOR" `
        -Role "Draft work-packet previews from the supervisor plan." `
        -Lane "dispatch_queue" `
        -Task "Prepare packet metadata, files in scope, risks, validators, and stop conditions." `
        -FilesInScope @(
            "work_packets/examples",
            "work_packets/queues",
            "automation/orchestration/queue"
        ) `
        -Validators @(
            "Validate changed JSON parses",
            "git diff --check"
        ) `
        -ApprovalRequired "Approval required before any packet moves from preview to active queue." `
        -NextAction "Keep generated packets in preview status until operator approval."
    New-WorkerAssignment `
        -WorkerId "LANE-ROUTER" `
        -Role "Detect the lane required by each packet and flag lane conflicts." `
        -Lane "state_monitor" `
        -Task "Map scope to available lanes and report missing or ambiguous lanes." `
        -FilesInScope @(
            "automation/orchestration/terminal_workstations/AIOS_WORKTREE_LANE_REGISTRY.json",
            "automation/orchestration/bootstrap",
            "docs/AI_OS/orchestration/AIOS_WORKTREE_LANES.md"
        ) `
        -Validators @(
            "Validate lane registry JSON parses",
            "git diff --check"
        ) `
        -ApprovalRequired "Approval required before opening lane shells or assigning humans to lanes." `
        -NextAction "Confirm lane exists and matches the intended worktree before any worker starts."
    New-WorkerAssignment `
        -WorkerId "VALIDATOR-ROUTER" `
        -Role "Route packet scopes to required read-only validators." `
        -Lane "validation_audit" `
        -Task "Select validator chain entries and identify required syntax, JSON, and safety checks." `
        -FilesInScope @(
            "automation/orchestration/validators",
            "scripts/validation",
            "work_packets/schema.json"
        ) `
        -Validators @(
            "powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/validators/Invoke-OrchestrationValidatorChain.DRY_RUN.ps1",
            "git diff --check"
        ) `
        -ApprovalRequired "Validator PASS does not approve APPLY, commit, push, or PR creation." `
        -NextAction "Run read-only validators and report PASS, WARN, or FAIL."
    New-WorkerAssignment `
        -WorkerId "GATEKEEPER" `
        -Role "Route approval gates and commit or PR packaging previews." `
        -Lane "main_control" `
        -Task "Confirm approval state, exact files, validator status, and commit package readiness." `
        -FilesInScope @(
            "automation/orchestration/approval_inbox",
            "automation/orchestration/commit_packages",
            "Reports/dispatcher/runtime/commit_packages"
        ) `
        -Validators @(
            "powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/validators/Test-ApplyApprovalGate.DRY_RUN.ps1",
            "powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/validators/Test-CommitPackageManifest.DRY_RUN.ps1",
            "git status --short"
        ) `
        -ApprovalRequired "Separate human approval required for APPLY, git add exact files, commit, push, and PR creation." `
        -NextAction "Produce preview only; wait for explicit operator instruction."
)

$plan = [pscustomobject]@{
    schema = "AIOS_SUPERVISOR_ASSIGNMENT_PLAN.v1"
    mode = "DRY_RUN_ONLY"
    work_goal = $WorkGoal
    generated_at = (Get-Date).ToString("s")
    available_lanes_detected = $availableLanes
    validator_chain_detected = $validatorNames
    workers_needed = $workerAssignments
    packet_creation_preview = [pscustomobject]@{
        packet_status = "PREVIEW_ONLY"
        target_folder = "work_packets/examples"
        active_queue_update = "BLOCKED_UNTIL_APPROVED"
        required_fields = @(
            "id",
            "title",
            "lane",
            "mode",
            "status",
            "objective",
            "files_in_scope",
            "validators",
            "approval_required",
            "stop_condition"
        )
    }
    approval_gate_routing = [pscustomobject]@{
        dry_run = "allowed"
        apply = "requires exact human approval"
        commit_package = "preview only until exact-file staging is approved"
        pull_request = "preview only until push and PR creation are approved"
    }
    commit_pr_packaging_preview = [pscustomobject]@{
        git_add = "BLOCKED: exact files required; never use git add ."
        commit = "BLOCKED: requires explicit commit approval"
        push = "BLOCKED: requires explicit push approval"
        pull_request = "BLOCKED: requires explicit PR creation approval"
    }
    stop_condition = "Stop after reporting workers, lanes, packet previews, validators, approvals, git status, and next safe action."
    next_safe_action = "Review this DRY_RUN plan, then approve one exact packet or validator action."
}

$plan | ConvertTo-Json -Depth 10
