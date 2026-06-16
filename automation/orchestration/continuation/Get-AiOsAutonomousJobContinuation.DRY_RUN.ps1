param(
    [string]$RepoRoot = "",
    [string]$PreviousStateJson = "",
    [string]$PreviousStatePath = "",
    [switch]$OutputJson
)

$ErrorActionPreference = "Stop"

function Resolve-AiOsRepoRoot {
    param([string]$CandidateRoot)
    if (-not [string]::IsNullOrWhiteSpace($CandidateRoot)) {
        return (Resolve-Path -LiteralPath $CandidateRoot).Path
    }
    $gitRoot = (git -C $PSScriptRoot rev-parse --show-toplevel 2>$null)
    if (-not [string]::IsNullOrWhiteSpace($gitRoot)) {
        return (Resolve-Path -LiteralPath $gitRoot.Trim()).Path
    }
    return (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..\..")).Path
}

try {
    $repoRootPath = Resolve-AiOsRepoRoot -CandidateRoot $RepoRoot
    $scriptPath = Join-Path $PSScriptRoot "aios_autonomous_job_continuation.py"
    if (-not (Test-Path -LiteralPath $scriptPath -PathType Leaf)) {
        throw "Missing autonomous job continuation engine: $scriptPath"
    }

    $previousPayload = $PreviousStateJson
    if ([string]::IsNullOrWhiteSpace($previousPayload) -and -not [string]::IsNullOrWhiteSpace($PreviousStatePath)) {
        $previousPayload = Get-Content -LiteralPath $PreviousStatePath -Raw
    }

    $argsList = @($scriptPath, "--repo-root", $repoRootPath)
    if (-not [string]::IsNullOrWhiteSpace($previousPayload)) {
        $argsList += @("--previous-state-json", $previousPayload)
    }

    $json = & python @argsList
    if ($LASTEXITCODE -ne 0) {
        throw "Autonomous job continuation engine exited with code $LASTEXITCODE"
    }

    if ($OutputJson) {
        $json
    }
    else {
        $state = $json | ConvertFrom-Json
        [ordered]@{
            schema = $state.schema
            cycle_id = $state.cycle_id
            state = $state.state
            selected_task_id = $state.selected_task.task_id
            selected_task_mode = $state.selected_task.mode
            repair_count = $state.repair_count
            security_state = $state.security_snapshot.overall_state
            safe_to_continue_without_human = $state.safe_to_continue_without_human
            stop_reason = $state.stop_reason
            next_safe_action = $state.next_safe_action
        } | ConvertTo-Json -Depth 8
    }
    exit 0
}
catch {
    $failure = [ordered]@{
        schema = "AIOS_AUTONOMOUS_JOB_CONTINUATION_STATE.v1"
        generated_at_utc = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
        cycle_id = "AIOS-AJC-FAIL-CLOSED"
        component = "autonomous_job_continuation"
        mode = "DRY_RUN_READ_ONLY"
        repo_root = $RepoRoot
        branch = "unknown"
        state = "STOP"
        state_history = @("BOOT", "RECON", "STOP")
        selected_task = [ordered]@{
            task_id = "none"
            title = "Autonomous job continuation engine failed closed."
            mode = "BLOCKED"
            lane = "BLOCKED"
            blocked = $true
            blocked_reason = "engine_failure"
            validators = @("Manual evidence review")
            allowed_paths = @()
            forbidden_paths = @()
        }
        validators = @("Manual evidence review")
        validator_status = "unknown"
        repair_count = 0
        security_snapshot = [ordered]@{
            overall_state = "UNKNOWN"
            safe_for_dry_run = $false
            safe_for_apply = $false
            sos_required = $false
            stop_required = $true
            review_required = $true
        }
        dirty_signature = "unknown"
        security_signature = "unknown"
        task_signature = "unknown"
        approval_snapshot = [ordered]@{
            approval_required = $true
            explicit_approval_present = $false
            approval_gate_status = "unknown"
            approval_inbox_status = "unknown"
            approval_mutated = $false
        }
        resume = [ordered]@{
            requested = $false
            can_resume = $false
            reason = "Engine failed closed."
        }
        evidence = $null
        execution = [ordered]@{
            executed_commands = @()
            allowlisted_action = ""
            mutation_performed = $false
            apply_performed = $false
            protected_action_performed = $false
            worker_launch_performed = $false
            scheduler_performed = $false
            daemon_performed = $false
        }
        safe_to_continue_without_human = $false
        stop_reason = "engine_failure"
        next_safe_action = "Stop and inspect autonomous job continuation engine failure."
        safety = [ordered]@{
            read_only = $true
            dry_run_only = $true
            apply_allowed = $false
            git_add_allowed = $false
            git_commit_allowed = $false
            git_push_allowed = $false
            pr_allowed = $false
            merge_allowed = $false
            worker_launch_allowed = $false
            scheduler_allowed = $false
            daemon_allowed = $false
            broker_allowed = $false
            live_trading_allowed = $false
            production_allowed = $false
            dashboard_mutation_allowed = $false
        }
    }
    $failure | ConvertTo-Json -Depth 20
    exit 1
}
