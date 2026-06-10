param(
    [ValidateSet("help","daily","morning","swarm","status","resume","workers","runtime","supervisor","mission","runner","queue","telemetry","packet","layout","control","finish-pr","hud","autonomy-status","autonomy-next","approval-status","self-build-status")]
    [Parameter(Position=0)]
    [string]$Mode = "help",
    [string]$Goal = "Build next AIOS runtime loop step",
    [string]$MissionName = "",
    [int]$WorkerCount = 4,
    [ValidateSet("auto","compact","wide","dual-monitor")]
    [string]$Preset = "auto",
    [switch]$ApplyMission,
    [string]$MissionPath = "",
    [string]$TaskId = "",
    [int]$Pr = 0,
    [switch]$ShowPrompt,

    # packet command params — used with: .\aios.ps1 packet <worker> <preset>
    [Parameter(Position=1)]
    [string]$Worker = "",
    [Parameter(Position=2)]
    [string]$PacketPreset = "",
    [ValidateSet("DRY_RUN","APPLY")]
    [string]$ExecutionMode = "DRY_RUN"
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

Write-Host "AIOS SHORTCUT START" -ForegroundColor Cyan
Write-Host "Mode: $Mode"

function Show-AiOsCrewRecommendation {
    $crewHelper = "automation/orchestration/crew/Get-AiOsCrewIntegrationRecommendation.DRY_RUN.ps1"

    Write-Host ""
    Write-Host "== Crew Recommendation ==" -ForegroundColor Yellow
    Write-Host "Mode: DRY_RUN_READ_ONLY"
    Write-Host "Authority: evidence only; Human Owner approval is required before APPLY, commit, push, merge, lock, or approval changes."

    if (-not (Test-Path -LiteralPath $crewHelper -PathType Leaf)) {
        Write-Host "Crew helper: unavailable" -ForegroundColor Yellow
        Write-Host "Next safe action: continue with existing status checks; do not infer Crew readiness."
        return
    }

    try {
        $rawOutput = powershell -NoProfile -File $crewHelper -OutputJson 2>&1
        $crew = ($rawOutput | Out-String) | ConvertFrom-Json

        Write-Host "overall_readiness: $($crew.overall_readiness)"
        Write-Host "next_safe_action: $($crew.next_safe_action)"
        Write-Host "recommended_worker: $($crew.recommended_worker)"
        Write-Host "recommended_lane: $($crew.recommended_lane)"
        Write-Host "recommended_validators:"
        if (@($crew.recommended_validators).Count -eq 0) {
            Write-Host "  NONE"
        } else {
            @($crew.recommended_validators) | ForEach-Object { Write-Host "  $_" }
        }
        Write-Host "approval_summary: pending=$($crew.approval_state_summary.pending_approvals); approved=$($crew.approval_state_summary.approved_actions); blocked=$($crew.approval_state_summary.blocked_actions)"
        Write-Host "collision_warning: $($crew.collision_warning)"
        Write-Host "commit_package_preview: status=$($crew.commit_package_preview.status); git_status=$($crew.commit_package_preview.git_status); recommended_files=$($crew.commit_package_preview.recommended_file_count); risks=$($crew.commit_package_preview.risk_count)"
    }
    catch {
        Write-Host "Crew helper: failed" -ForegroundColor Yellow
        Write-Host "Reason: $($_.Exception.Message)"
        Write-Host "Next safe action: continue with existing status checks; do not infer Crew readiness."
    }
}

function Invoke-AiOsReadOnlyPowerShellScript {
    param(
        [Parameter(Mandatory = $true)][string]$RelativePath,
        [string[]]$Arguments = @()
    )

    $scriptPath = Join-Path $PSScriptRoot $RelativePath
    if (-not (Test-Path -LiteralPath $scriptPath -PathType Leaf)) {
        Write-Host "Read-only command unavailable: $RelativePath" -ForegroundColor Yellow
        Write-Host "No state was changed."
        return
    }

    powershell -NoProfile -ExecutionPolicy Bypass -File $scriptPath @Arguments
}

function Invoke-AiOsReadOnlyPythonScript {
    param(
        [Parameter(Mandatory = $true)][string]$RelativePath,
        [string[]]$Arguments = @()
    )

    $scriptPath = Join-Path $PSScriptRoot $RelativePath
    if (-not (Test-Path -LiteralPath $scriptPath -PathType Leaf)) {
        Write-Host "Read-only command unavailable: $RelativePath" -ForegroundColor Yellow
        Write-Host "No state was changed."
        return
    }

    & python $scriptPath @Arguments
}

function Invoke-AiOsQuietJsonCommand {
    param(
        [Parameter(Mandatory = $true)][string]$RelativePath,
        [string[]]$Arguments = @()
    )

    $scriptPath = Join-Path $PSScriptRoot $RelativePath
    if (-not (Test-Path -LiteralPath $scriptPath -PathType Leaf)) {
        return [ordered]@{
            available = $false
            source = $RelativePath
            error = "missing script"
            raw_output = $null
            data = $null
        }
    }

    try {
        $rawOutput = & powershell -NoProfile -ExecutionPolicy Bypass -File $scriptPath @Arguments 2>$null
        $jsonText = ($rawOutput | Out-String).Trim()
        if ([string]::IsNullOrWhiteSpace($jsonText)) {
            throw "script returned no JSON output"
        }

        return [ordered]@{
            available = $true
            source = $RelativePath
            error = $null
            raw_output = $jsonText
            data = ($jsonText | ConvertFrom-Json)
        }
    }
    catch {
        return [ordered]@{
            available = $false
            source = $RelativePath
            error = $_.Exception.Message
            raw_output = $null
            data = $null
        }
    }
}

function Get-AiOsGitSummary {
    $statusLines = @(git status --short --branch 2>$null)
    $branchLine = if ($statusLines.Count -gt 0) { [string]$statusLines[0] } else { "## UNKNOWN" }
    $branch = "UNKNOWN"
    $ahead = $null
    $behind = $null

    if ($branchLine.StartsWith("## ")) {
        $descriptor = $branchLine.Substring(3).Trim()
        $tracking = ""

        if ($descriptor -match '^(?<branch>.+?)(?:\s+\[(?<tracking>[^\]]+)\])?$') {
            $branchDescriptor = [string]$Matches.branch
            $tracking = [string]$Matches.tracking
            if ($branchDescriptor -match '^(?<local>.+?)\.\.\.(?<remote>.+)$') {
                $branch = [string]$Matches.local
            } else {
                $branch = $branchDescriptor.Trim()
            }
        }

        if (-not [string]::IsNullOrWhiteSpace($tracking)) {
            foreach ($part in ($tracking -split ',')) {
                $token = $part.Trim()
                if ($token -match '^ahead\s+(?<count>\d+)$') {
                    $ahead = [int]$Matches.count
                } elseif ($token -match '^behind\s+(?<count>\d+)$') {
                    $behind = [int]$Matches.count
                }
            }
        }
    }

    return [pscustomobject]@{
        branch = $branch
        clean = ($statusLines.Count -le 1)
        changed_count = [Math]::Max($statusLines.Count - 1, 0)
        ahead = $ahead
        behind = $behind
        commit_performed = "NO"
        push_performed = "NO"
    }
}

function Get-AiOsSelfBuildSummary {
    $consumerPath = "automation/orchestration/autonomy_control_plane/aios_self_build_decision_consumer.py"
    $evidencePath = "Reports/self_build_cycle/latest_self_build_cycle.evidence.json"
    $scriptPath = Join-Path $PSScriptRoot $consumerPath

    $summary = [ordered]@{
        available = $false
        source = $consumerPath
        normalized_status = "REVIEW_REQUIRED"
        operator_route = "APPROVAL_REVIEW_REQUIRED"
        approval_required = $true
        report_only = $true
        safe_next_action = "Review self-build decision consumer failure before relying on autonomy status."
        source_evidence_path = $evidencePath
        source_cycle_id = $null
    }

    if (-not (Test-Path -LiteralPath $scriptPath -PathType Leaf)) {
        $summary.safe_next_action = "Self-build decision consumer is unavailable; continue with existing control readout only."
        return [pscustomobject]$summary
    }

    try {
        $rawOutput = & python $scriptPath --evidence (Join-Path $PSScriptRoot $evidencePath) 2>$null
        $jsonText = ($rawOutput | Out-String).Trim()
        if ([string]::IsNullOrWhiteSpace($jsonText)) {
            throw "consumer produced no JSON output"
        }
        $readout = $jsonText | ConvertFrom-Json
        return [pscustomobject]@{
            available = $true
            source = $consumerPath
            normalized_status = [string]$readout.normalized_status
            operator_route = [string]$readout.operator_route
            approval_required = [bool]$readout.approval_required
            report_only = [bool]$readout.report_only
            safe_next_action = [string]$readout.safe_next_action
            source_evidence_path = [string]$readout.source_evidence_path
            source_cycle_id = $readout.source_cycle_id
        }
    }
    catch {
        $summary.safe_next_action = "Review self-build decision consumer failure before relying on autonomy status."
        return [pscustomobject]$summary
    }
}

function Get-AiOsApprovalSummary {
    $summaryPath = "automation/orchestration/approval_inbox/Get-AiOsApprovalInboxSummary.DRY_RUN.ps1"
    $inboxPath = "automation/orchestration/approval_inbox"
    $result = Invoke-AiOsQuietJsonCommand -RelativePath $summaryPath -Arguments @("-InboxPath", $inboxPath, "-QuietJson")

    if (-not $result.available) {
        return [pscustomobject]@{
            available = $false
            source = $summaryPath
            approval_summary_available = $false
            approval_pending_count = 0
            approval_blocked_count = 0
            approval_completed_count = 0
            approval_safe_state = "REVIEW_REQUIRED"
            approval_next_review_action = "Review approval summary failure before relying on approval state visibility."
            approvals_performed = "NO"
            approval_inbox_mutated = "NO"
            apply_gate_mutated = "NO"
            protected_action_allowed = "NO"
            commit_performed = "NO"
            push_performed = "NO"
        }
    }

    $data = $result.data
    $pendingCount = @($data.pending_approvals).Count
    $blockedCount = @($data.blocked_actions).Count
    $completedCount = @($data.approved_actions).Count
    $safeState = if ($blockedCount -gt 0) { "BLOCKED" } elseif (($pendingCount + $completedCount) -gt 0) { "REVIEW" } else { "PASS" }

    return [pscustomobject]@{
        available = $true
        source = $summaryPath
        approval_summary_available = $true
        approval_pending_count = $pendingCount
        approval_blocked_count = $blockedCount
        approval_completed_count = $completedCount
        approval_safe_state = $safeState
        approval_next_review_action = [string]$data.next_safe_command
        approvals_performed = "NO"
        approval_inbox_mutated = "NO"
        apply_gate_mutated = "NO"
        protected_action_allowed = "NO"
        commit_performed = "NO"
        push_performed = "NO"
    }
}

function Get-AiOsNextCommandSummary {
    $result = Invoke-AiOsQuietJsonCommand -RelativePath "automation/runtime/recommendation/Get-AiOsNextCommand.ps1" -Arguments @("-QuietJson")
    $summary = [ordered]@{
        available = $false
        source = "automation/runtime/recommendation/Get-AiOsNextCommand.ps1"
        next_best_step = "Review next-command summary failure before choosing a command."
        why = "Next-command summary unavailable."
        safe_to_run = "UNKNOWN"
        approval_required = "UNKNOWN"
        runtime_health = "UNKNOWN"
        self_build_decision_status = "UNKNOWN"
        self_build_operator_route = "UNKNOWN"
        self_build_approval_required = $false
        self_build_report_only = $true
        self_build_safe_next_action = "Review self-build decision consumer failure before relying on autonomy status."
        self_build_source = "automation/orchestration/autonomy_control_plane/aios_self_build_decision_consumer.py"
        approval_summary_available = $false
        approval_pending_count = 0
        approval_blocked_count = 0
        approval_completed_count = 0
        approval_safe_state = "REVIEW_REQUIRED"
        approval_next_review_action = "Review approval summary failure before relying on approval state visibility."
        approvals_performed = "NO"
        approval_inbox_mutated = "NO"
        apply_gate_mutated = "NO"
        protected_action_allowed = "NO"
        commit_performed = "NO"
        push_performed = "NO"
    }

    if (-not $result.available) {
        $selfBuildSummary = Get-AiOsSelfBuildSummary
        $approvalSummary = Get-AiOsApprovalSummary
        $summary.self_build_decision_status = $selfBuildSummary.normalized_status
        $summary.self_build_operator_route = $selfBuildSummary.operator_route
        $summary.self_build_approval_required = [bool]$selfBuildSummary.approval_required
        $summary.self_build_report_only = [bool]$selfBuildSummary.report_only
        $summary.self_build_safe_next_action = [string]$selfBuildSummary.safe_next_action
        $summary.self_build_source = [string]$selfBuildSummary.source
        $summary.approval_summary_available = [bool]$approvalSummary.approval_summary_available
        $summary.approval_pending_count = [int]$approvalSummary.approval_pending_count
        $summary.approval_blocked_count = [int]$approvalSummary.approval_blocked_count
        $summary.approval_completed_count = [int]$approvalSummary.approval_completed_count
        $summary.approval_safe_state = [string]$approvalSummary.approval_safe_state
        $summary.approval_next_review_action = [string]$approvalSummary.approval_next_review_action
        $summary.approvals_performed = [string]$approvalSummary.approvals_performed
        $summary.approval_inbox_mutated = [string]$approvalSummary.approval_inbox_mutated
        $summary.apply_gate_mutated = [string]$approvalSummary.apply_gate_mutated
        $summary.protected_action_allowed = [string]$approvalSummary.protected_action_allowed
        $summary.commit_performed = [string]$approvalSummary.commit_performed
        $summary.push_performed = [string]$approvalSummary.push_performed
        return [pscustomobject]$summary
    }

    $data = $result.data
    $summary.available = $true
    $summary.next_best_step = [string]$data.next_best_step
    $summary.why = [string]$data.why
    $summary.safe_to_run = [string]$data.safe_to_run
    $summary.approval_required = [string]$data.approval_required
    $summary.runtime_health = [string]$data.runtime_health
    $summary.self_build_decision_status = [string]$data.self_build_decision_status
    $summary.self_build_operator_route = [string]$data.self_build_operator_route
    $summary.self_build_approval_required = [bool]$data.self_build_approval_required
    $summary.self_build_report_only = [bool]$data.self_build_report_only
    $summary.self_build_safe_next_action = [string]$data.self_build_safe_next_action
    $summary.self_build_source = $summary.source
    $summary.approval_summary_available = [bool]$data.approval_summary_available
    $summary.approval_pending_count = [int]$data.approval_pending_count
    $summary.approval_blocked_count = [int]$data.approval_blocked_count
    $summary.approval_completed_count = [int]$data.approval_completed_count
    $summary.approval_safe_state = [string]$data.approval_safe_state
    $summary.approval_next_review_action = [string]$data.approval_next_review_action
    $summary.approvals_performed = [string]$data.approvals_performed
    $summary.approval_inbox_mutated = [string]$data.approval_inbox_mutated
    $summary.apply_gate_mutated = [string]$data.apply_gate_mutated
    $summary.protected_action_allowed = [string]$data.protected_action_allowed
    $summary.commit_performed = [string]$data.commit_performed
    $summary.push_performed = [string]$data.push_performed

    if ([string]::IsNullOrWhiteSpace($summary.self_build_decision_status) -or $summary.self_build_decision_status -eq "UNKNOWN") {
        $selfBuildSummary = Get-AiOsSelfBuildSummary
        $summary.self_build_decision_status = [string]$selfBuildSummary.normalized_status
        $summary.self_build_operator_route = [string]$selfBuildSummary.operator_route
        $summary.self_build_approval_required = [bool]$selfBuildSummary.approval_required
        $summary.self_build_report_only = [bool]$selfBuildSummary.report_only
        $summary.self_build_safe_next_action = [string]$selfBuildSummary.safe_next_action
        $summary.self_build_source = [string]$selfBuildSummary.source
    }

    if (-not $summary.approval_summary_available) {
        $approvalSummary = Get-AiOsApprovalSummary
        $summary.approval_summary_available = [bool]$approvalSummary.approval_summary_available
        $summary.approval_pending_count = [int]$approvalSummary.approval_pending_count
        $summary.approval_blocked_count = [int]$approvalSummary.approval_blocked_count
        $summary.approval_completed_count = [int]$approvalSummary.approval_completed_count
        $summary.approval_safe_state = [string]$approvalSummary.approval_safe_state
        $summary.approval_next_review_action = [string]$approvalSummary.approval_next_review_action
        $summary.approvals_performed = [string]$approvalSummary.approvals_performed
        $summary.approval_inbox_mutated = [string]$approvalSummary.approval_inbox_mutated
        $summary.apply_gate_mutated = [string]$approvalSummary.apply_gate_mutated
        $summary.protected_action_allowed = [string]$approvalSummary.protected_action_allowed
        $summary.commit_performed = [string]$approvalSummary.commit_performed
        $summary.push_performed = [string]$approvalSummary.push_performed
    }

    return [pscustomobject]$summary
}

function Write-AiOsControlReadout {
    param(
        [Parameter(Mandatory = $true)][pscustomobject]$GitSummary,
        [Parameter(Mandatory = $true)][pscustomobject]$NextSummary
    )

    $cleanText = if ($GitSummary.clean) { "true" } else { "false" }

    Write-Host ""
    Write-Host "AI_OS CONTROL READOUT" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "REPO"
    Write-Host "branch: $($GitSummary.branch)"
    Write-Host "clean: $cleanText"
    Write-Host "changed_count: $($GitSummary.changed_count)"
    if ($null -ne $GitSummary.ahead) {
        Write-Host "ahead: $($GitSummary.ahead)"
    }
    if ($null -ne $GitSummary.behind) {
        Write-Host "behind: $($GitSummary.behind)"
    }
    Write-Host "commit_performed: $($GitSummary.commit_performed)"
    Write-Host "push_performed: $($GitSummary.push_performed)"

    Write-Host ""
    Write-Host "RUNTIME / NEXT"
    Write-Host "next_best_step: $($NextSummary.next_best_step)"
    Write-Host "why: $($NextSummary.why)"
    Write-Host "safe_to_run: $($NextSummary.safe_to_run)"
    Write-Host "approval_required: $($NextSummary.approval_required)"
    Write-Host "source: Get-AiOsNextCommand.ps1"

    Write-Host ""
    Write-Host "SELF-BUILD"
    Write-Host "normalized_status: $($NextSummary.self_build_decision_status)"
    Write-Host "operator_route: $($NextSummary.self_build_operator_route)"
    Write-Host "approval_required: $($NextSummary.self_build_approval_required)"
    Write-Host "report_only: $($NextSummary.self_build_report_only)"
    Write-Host "safe_next_action: $($NextSummary.self_build_safe_next_action)"
    Write-Host "source: $($NextSummary.self_build_source)"

    Write-Host ""
    Write-Host "APPROVAL"
    Write-Host "approval_summary_available: $($NextSummary.approval_summary_available)"
    Write-Host "approval_pending_count: $($NextSummary.approval_pending_count)"
    Write-Host "approval_blocked_count: $($NextSummary.approval_blocked_count)"
    Write-Host "approval_completed_count: $($NextSummary.approval_completed_count)"
    Write-Host "approval_safe_state: $($NextSummary.approval_safe_state)"
    Write-Host "approval_next_review_action: $($NextSummary.approval_next_review_action)"
    Write-Host "approvals_performed: $($NextSummary.approvals_performed)"
    Write-Host "approval_inbox_mutated: $($NextSummary.approval_inbox_mutated)"
    Write-Host "apply_gate_mutated: $($NextSummary.apply_gate_mutated)"
    Write-Host "protected_action_allowed: $($NextSummary.protected_action_allowed)"

    Write-Host ""
    Write-Host "SAFETY FLAGS"
    Write-Host "approvals_performed: $($NextSummary.approvals_performed)"
    Write-Host "approval_inbox_mutated: $($NextSummary.approval_inbox_mutated)"
    Write-Host "apply_gate_mutated: $($NextSummary.apply_gate_mutated)"
    Write-Host "work_packets_mutated: NO"
    Write-Host "protected_action_allowed: $($NextSummary.protected_action_allowed)"
    Write-Host "apply_performed: NO"
    Write-Host "commit_performed: $($NextSummary.commit_performed)"
    Write-Host "push_performed: $($NextSummary.push_performed)"
    Write-Host "merge_performed: NO"
    Write-Host "dispatch_performed: NO"
    Write-Host "live_trading_performed: NO"
    Write-Host "broker_connection_performed: NO"
    Write-Host "scheduler_created: NO"
    Write-Host "service_created: NO"

    Write-Host ""
    Write-Host "FINAL OPERATOR NEXT STEP"
    Write-Host $NextSummary.next_best_step
    Write-Host ""
}

switch ($Mode) {
    "help" {
        Write-Host ""
        Write-Host "Available commands:"
        Write-Host ".\aios.ps1 -Mode daily    # run normal daily flow"
        Write-Host ".\aios.ps1 -Mode morning  # run morning operations intelligence"
        Write-Host ".\aios.ps1 -Mode status   # show health, next action, inbox"
        Write-Host ".\aios.ps1 -Mode resume   # resume last session"
        Write-Host ".\aios.ps1 -Mode workers  # show worker list and inbox"
        Write-Host ".\aios.ps1 -Mode swarm    # launch worker swarm"
        Write-Host ".\aios.ps1 -Mode runtime  # run goal intake + recommendation + health"
        Write-Host ".\aios.ps1 -Mode supervisor # preview supervised scheduler/runtime events"
        Write-Host ".\aios.ps1 -Mode mission -Goal ""Improve AIOS runtime automation"" # create Mission Control plan DRY_RUN"
        Write-Host ".\aios.ps1 -Mode runner # preview allowlisted command runner"
        Write-Host ".\aios.ps1 -Mode runner -MissionPath automation/mission_control/missions/improve-aios-runtime-automation # show next safe mission action"
        Write-Host ".\aios.ps1 -Mode runner -MissionPath automation/mission_control/missions/improve-aios-runtime-automation -TaskId MC-01 -ShowPrompt # show task prompt"
        Write-Host ".\aios.ps1 -Mode queue # show command queue read-only"
        Write-Host ".\aios.ps1 -Mode telemetry # show telemetry viewer read-only"
        Write-Host ".\aios.ps1 -Mode layout  # show 5-worker terminal layout plan and banner commands"
        Write-Host ".\aios.ps1 -Mode control # one-command operator control readout"
        Write-Host ".\aios.ps1 -Mode finish-pr -Pr 273 # preview PR finish steps"
        Write-Host ".\aios.ps1 -Mode hud -Worker CLAUDE # preview worker HUD"
        Write-Host ".\aios.ps1 -Mode autonomy-status # autonomy/control-plane status report"
        Write-Host ".\aios.ps1 -Mode autonomy-next # next safe operator command only"
        Write-Host ".\aios.ps1 -Mode approval-status # approval inbox/readiness summary"
        Write-Host ".\aios.ps1 -Mode self-build-status # latest self-build decision readout"
    }

    "daily" {
        powershell -ExecutionPolicy Bypass -File automation/session/Start-AiOsDailyFlow.ps1 -RunWorkerPreview
    }
    "morning" {
    powershell -ExecutionPolicy Bypass -File automation/operator/Start-AiOsMorningOperations.ps1
    }

    "swarm" {
        powershell -ExecutionPolicy Bypass -File automation/session/Start-AiOsDailyFlow.ps1 -LaunchSwarm -RunWorkerPreview
    }

    "status" {
        powershell -ExecutionPolicy Bypass -File automation/orchestration/health/Test-AiOsRuntimeHealth.DRY_RUN.ps1
        powershell -ExecutionPolicy Bypass -File automation/orchestration/recommendations/Get-AiOsActionRecommendation.DRY_RUN.ps1
        powershell -ExecutionPolicy Bypass -File automation/orchestration/workers/inbox/Get-AiOsWorkerInbox.DRY_RUN.ps1
        Show-AiOsCrewRecommendation
    }

    "resume" {
        powershell -ExecutionPolicy Bypass -File automation/session/Resume-AiOsSession.ps1
    }

    "workers" {
        powershell -ExecutionPolicy Bypass -File automation/orchestration/workers/Get-AiOsWorkerAddressBook.ps1
        powershell -ExecutionPolicy Bypass -File automation/orchestration/workers/inbox/Get-AiOsWorkerInbox.DRY_RUN.ps1
    }

    "control" {
        $gitSummary = Get-AiOsGitSummary
        $nextSummary = Get-AiOsNextCommandSummary
        Write-AiOsControlReadout -GitSummary $gitSummary -NextSummary $nextSummary
    }

    "finish-pr" {
        if ($Pr -le 0) {
            Write-Host "BLOCKED: -Pr must be a positive PR number." -ForegroundColor Red
            exit 1
        }

        powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/pr_gates/Invoke-AiOsPrFinisher.DRY_RUN.ps1 -Pr $Pr
    }

    "hud" {
        powershell -NoProfile -ExecutionPolicy Bypass -File automation/window_identity/Show-AiOsWorkerHud.DRY_RUN.ps1 -Worker $Worker
    }

    "autonomy-status" {
        Invoke-AiOsReadOnlyPowerShellScript -RelativePath "automation/orchestration/autonomy_reports/New-AiOsAutonomyStatusReport.DRY_RUN.ps1"
    }

    "autonomy-next" {
        Invoke-AiOsReadOnlyPowerShellScript -RelativePath "automation/runtime/recommendation/Get-AiOsNextCommand.ps1"
    }

    "approval-status" {
        Invoke-AiOsReadOnlyPowerShellScript -RelativePath "automation/orchestration/approval_inbox/Get-AiOsApprovalInboxSummary.DRY_RUN.ps1"
    }

    "self-build-status" {
        Invoke-AiOsReadOnlyPythonScript -RelativePath "automation/orchestration/autonomy_control_plane/aios_self_build_decision_consumer.py" -Arguments @(
            "--evidence",
            (Join-Path $PSScriptRoot "Reports/self_build_cycle/latest_self_build_cycle.evidence.json")
        )
    }

    "runtime" {

    powershell -ExecutionPolicy Bypass -File checkpoints/verify_success.ps1

    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "BLOCKED: proof verification failed" -ForegroundColor Red
        exit 1
    }

    powershell -ExecutionPolicy Bypass -File automation/intake/Start-AiOsRuntimeLoop.ps1 -Goal $Goal -Apply
}

   "supervisor" {
    powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/scheduler/Invoke-AiOsSchedulerPreview.DRY_RUN.ps1
}

   "mission" {
    $missionArgs = @(
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        "automation/mission_control/New-AiOsMissionPlan.ps1",
        "-Goal",
        $Goal,
        "-WorkerCount",
        $WorkerCount,
        "-Preset",
        $Preset
    )

    if (-not [string]::IsNullOrWhiteSpace($MissionName)) {
        $missionArgs += @("-MissionName", $MissionName)
    }

    if ($ApplyMission) {
        $missionArgs += "-Apply"
    }

    powershell @missionArgs
}

   "runner" {
    if ([string]::IsNullOrWhiteSpace($MissionPath)) {
        powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/command_runner/Invoke-AiOsCommandRunner.DRY_RUN.ps1
        break
    }

    $runnerArgs = @(
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        "automation/mission_control/Get-AiOsMissionNextAction.ps1",
        "-MissionPath",
        $MissionPath
    )

    if (-not [string]::IsNullOrWhiteSpace($TaskId)) {
        $runnerArgs += @("-TaskId", $TaskId)
    }

    if ($ShowPrompt) {
        $runnerArgs += "-ShowPrompt"
    }

    powershell @runnerArgs
}

   "queue" {
        powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/command_queue/Get-AiOsCommandQueue.DRY_RUN.ps1
}

   "telemetry" {
        powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/telemetry_viewer/Show-AiOsTelemetryViewer.DRY_RUN.ps1
}

   "layout" {
        $sep = "-" * 79
        Write-Host ""
        Write-Host "  AI_OS 5-WORKER TERMINAL LAYOUT" -ForegroundColor Cyan
        Write-Host "  $sep"
        Write-Host ""
        Write-Host "  ZONE MAP (1920x1080 reference)" -ForegroundColor White
        Write-Host "  +-----------------------+---------------------------+"
        Write-Host "  |                       |  2. CODEX BUILD LANE      |"
        Write-Host "  |  1. AI_OS MAIN        +-------------+-------------+"
        Write-Host "  |     CONTROL           | 3. CLAUDE   | 4. VALIDATOR|"
        Write-Host "  |  left, full height    +-------------+-------------+"
        Write-Host "  |  [0,0  960x1080]      |  5. APPROVAL INBOX        |"
        Write-Host "  +-----------------------+---------------------------+"
        Write-Host ""
        Write-Host "  WORKER IDENTITIES" -ForegroundColor White
        Write-Host "  $sep"
        Write-Host "  #  Worker                 Color    Role" -ForegroundColor DarkGray
        Write-Host "  1  AI_OS MAIN CONTROL   " -NoNewline; Write-Host "Cyan   " -NoNewline -ForegroundColor Cyan;    Write-Host "  orchestrator -- NEXT ACTION owner"
        Write-Host "  2  CODEX BUILD LANE     " -NoNewline; Write-Host "Blue   " -NoNewline -ForegroundColor Blue;    Write-Host "  executor     -- file edits, build tasks"
        Write-Host "  3  CLAUDE REVIEWER      " -NoNewline; Write-Host "Magenta" -NoNewline -ForegroundColor Magenta; Write-Host "  reviewer     -- DRY_RUN inspection"
        Write-Host "  4  VALIDATOR WORKER     " -NoNewline; Write-Host "Yellow " -NoNewline -ForegroundColor Yellow;  Write-Host "  validator    -- CI checks, git diff/status"
        Write-Host "  5  APPROVAL INBOX       " -NoNewline; Write-Host "Green  " -NoNewline -ForegroundColor Green;   Write-Host "  approval gate -- operator decisions only"
        Write-Host ""
        Write-Host "  BANNER COMMANDS (run in each worker terminal)" -ForegroundColor White
        Write-Host "  $sep"
        Write-Host '  powershell -File automation/operator/Show-AiOsWorkerBanner.ps1 -Worker "AI_OS MAIN CONTROL" -Mode DRY_RUN'
        Write-Host '  powershell -File automation/operator/Show-AiOsWorkerBanner.ps1 -Worker "CODEX BUILD LANE"   -Mode DRY_RUN'
        Write-Host '  powershell -File automation/operator/Show-AiOsWorkerBanner.ps1 -Worker "CLAUDE REVIEWER"    -Mode DRY_RUN'
        Write-Host '  powershell -File automation/operator/Show-AiOsWorkerBanner.ps1 -Worker "VALIDATOR WORKER"   -Mode DRY_RUN'
        Write-Host '  powershell -File automation/operator/Show-AiOsWorkerBanner.ps1 -Worker "APPROVAL INBOX"     -Mode DRY_RUN'
        Write-Host ""
        Write-Host "  WINDOWS TERMINAL PROFILE DRAFT" -ForegroundColor White
        Write-Host "  $sep"
        Write-Host "  docs/AI_OS/interface/WINDOWS_TERMINAL_PROFILES_DRAFT.md"
        Write-Host "  Copy profile entries manually to settings.json -- do not auto-edit."
        Write-Host ""
        Write-Host "  WINDOW SNAPPING" -ForegroundColor White
        Write-Host "  $sep"
        Write-Host "  Manual snap recommended until zones are validated."
        Write-Host "  FancyZones scripting deferred to next implementation step."
        Write-Host ""
        Write-Host "  STOP POINT" -ForegroundColor Yellow
        Write-Host "  $sep"
        Write-Host "  DRY_RUN display only. No windows launched. No files changed." -ForegroundColor Yellow
        Write-Host "  Open each worker manually in a new Windows Terminal tab." -ForegroundColor Yellow
        Write-Host ""
    }

   "packet" {
    # Validate worker
    $supportedWorkers = @("claude")
    if ([string]::IsNullOrWhiteSpace($Worker) -or $supportedWorkers -notcontains $Worker) {
        Write-Host ""
        Write-Host "BLOCKED: unknown or missing worker." -ForegroundColor Red
        Write-Host "  Supported workers : $($supportedWorkers -join ', ')"
        Write-Host "  Usage             : .\aios.ps1 packet <worker> <preset>"
        Write-Host "  Example           : .\aios.ps1 packet claude audit-docs"
        Write-Host ""
        exit 1
    }

    # Validate preset
    $supportedPresets = @("audit-docs")
    if ([string]::IsNullOrWhiteSpace($PacketPreset) -or $supportedPresets -notcontains $PacketPreset) {
        Write-Host ""
        Write-Host "BLOCKED: unknown or missing preset." -ForegroundColor Red
        Write-Host "  Supported presets for '$Worker' : $($supportedPresets -join ', ')"
        Write-Host "  Usage                          : .\aios.ps1 packet <worker> <preset>"
        Write-Host "  Example                        : .\aios.ps1 packet claude audit-docs"
        Write-Host ""
        exit 1
    }

    # APPLY mode — not yet supported
    if ($ExecutionMode -eq "APPLY") {
        Write-Host ""
        Write-Host "╔══════════════════════════════════════════════════════════════════╗" -ForegroundColor Red
        Write-Host "║  [ APPLY PACKET — NOT SUPPORTED YET ]                           ║" -ForegroundColor Red
        Write-Host "║  APPLY mode is not implemented in packet generation yet.        ║" -ForegroundColor Red
        Write-Host "║  All packets are DRY_RUN only at this stage.                   ║" -ForegroundColor Red
        Write-Host "╚══════════════════════════════════════════════════════════════════╝" -ForegroundColor Red
        Write-Host ""
        Write-Host "Rerun without -ExecutionMode APPLY to generate a DRY_RUN packet." -ForegroundColor Yellow
        Write-Host ""
        exit 1
    }

    $ts  = Get-Date -Format "yyyy-MM-dd HH:mm"
    $sep = "=" * 68

    $packet = @"

$sep
  AI_OS CLAUDE DELEGATION PACKET
  Generated : $ts
  Preset    : $PacketPreset
  Worker    : $Worker
  Mode      : DRY_RUN
  STATUS    : REVIEW BEFORE SENDING -- do not auto-paste
$sep

ROLE:
  Isolated documentation auditor.

MODE:
  DRY_RUN. No files changed. Output is preview-only.

SCOPE:
  Allowed paths:
    docs/AI_OS/
    docs/governance/
    docs/infrastructure/
    docs/workflows/
    docs/audits/
    docs/decisions/
  Blocked paths:
    apps/
    services/
    automation/
    scripts/
    agent/
    aios/
    Reports/  (read allowed, write blocked)
    Any file containing: credentials, secrets, tokens, keys, .env
  Blocked actions:
    No commits. No pushes. No git staging.
    No file edits. No automation creation. No frontend code.
    No live trading. No broker connections.

RULES:
  - DRY_RUN only. Do not edit any file.
  - Report findings first. One finding per line.
  - Mark unverified facts as UNKNOWN.
  - Mark conflicting evidence as MISMATCH.
  - One role. One purpose. One output.

TASK:
  1. Inspect docs/AI_OS/ for files that do not carry a status label
     (DRAFT, CANDIDATE, CURRENT, HISTORICAL, SUPERSEDED).
  2. List files that reference live trading, OANDA, or broker
     execution as an active capability without a HISTORICAL or
     SUPERSEDED label.
  3. List files with no clear stop point or ownership declaration.
  Report only. Do not edit any file.

RETURN FORMAT:
  7-region worker layout per:
  docs/AI_OS/interface/AI_OS_WORKER_INTERFACE_SPECIFICATION_DRAFT.md
  Findings: one per line, PASS/WARN/FAIL/UNKNOWN label.
  Next Safe Action: one exact instruction.

STOP POINT:
  Stop after producing the findings report.
  Do not edit files. Do not proceed to APPLY without a separate
  explicit operator instruction.

ESCALATION PATH:
  If a protected governance file (AGENTS.md, RISK_POLICY.md,
  SECURITY.md, COMPLIANCE_BASELINE.md) requires labeling:
  output WARN and stop. Do not edit the file.

APPROVAL STATE:
  NOT_REQUIRED (DRY_RUN -- no files changed).

$sep
  NEXT OPERATOR ACTION:
  Review this packet. Confirm the allowed paths match your intent.
  Copy the text above. Paste into Claude Code manually.
  Do NOT send without reading the full packet.
$sep
"@

    Write-Host $packet
}
}

Write-Host "AIOS SHORTCUT END" -ForegroundColor Green


