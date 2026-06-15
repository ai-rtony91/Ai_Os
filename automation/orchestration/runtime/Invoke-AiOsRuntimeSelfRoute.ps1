param(
    [switch]$Apply,
    [switch]$QuietJson,
    [switch]$OutputJson,
    [switch]$Detailed
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

function Get-AiOsObjectProperty {
    param(
        [AllowNull()]$Object,
        [string]$Name,
        [AllowNull()]$Default = ""
    )

    if ($null -eq $Object) {
        return $Default
    }

    if ($Object.PSObject.Properties.Name -contains $Name) {
        return $Object.$Name
    }

    return $Default
}

function Invoke-AiOsPythonJsonArgumentScript {
    param(
        [string]$ScriptPath,
        [string]$ArgumentName,
        [string]$JsonPayload
    )

    $encodedPayload = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($JsonPayload))
    $pythonJsonArgumentRunner = 'import base64,runpy,sys;p=sys.argv[1];a=sys.argv[2];j=base64.b64decode(sys.argv[3]).decode();sys.argv=[p,a,j];n=chr(95)*2+chr(109)+chr(97)+chr(105)+chr(110)+chr(95)*2;runpy.run_path(p,run_name=n)'

    return @(
        python -c $pythonJsonArgumentRunner `
            $ScriptPath `
            $ArgumentName `
            $encodedPayload
    )
}

function New-AiOsBlockedRoutePreview {
    param(
        [string]$Reason,
        [AllowNull()]$SourceRecommendation,
        [AllowNull()]$ValidatedCommand
    )

    return [pscustomobject]@{
        schema = "AIOS_BOUNDED_WORKER_ROUTING_PREVIEW.v1"
        routing_status = "blocked"
        source_recommendation = $SourceRecommendation
        validated_command = $ValidatedCommand
        proposed_worker_identity = $null
        proposed_lane = $null
        proposed_task_summary = "No worker route available because route preview generation was blocked."
        proposed_write_scope = @()
        required_approvals = [pscustomobject]@{
            human_owner_review_before_execution = $true
            worker_dispatch = $true
            queue_mutation = $true
            approval_mutation = $true
            local_apply = $true
            commit = $true
            push = $true
            merge = $true
            scheduler_or_daemon = $true
            broker_or_trading = $true
        }
        blocked_actions = @(
            "execute_recommended_command",
            "launch_codex",
            "dispatch_worker",
            "mutate_runtime_queue",
            "mutate_worker_inbox",
            "mutate_approval_state",
            "start_scheduler",
            "start_daemon",
            "access_network",
            "write_reports",
            "touch_broker_trading_credentials_orders_or_webhooks",
            "git_add",
            "git_commit",
            "git_push",
            "git_merge",
            $Reason
        )
        commands_executed = @()
        queues_mutated = $false
        approvals_mutated = $false
        workers_dispatched = $false
        files_written = @()
        safety = [pscustomobject]@{
            preview_only = $true
            command_execution = $false
            codex_launch = $false
            worker_dispatch = $false
            queue_mutation = $false
            approval_mutation = $false
            scheduler_activation = $false
            daemon_activation = $false
            network_access = $false
            reports_written = $false
            file_writes = $false
            broker = $false
            credentials = $false
            live_trading = $false
            real_orders = $false
            real_webhooks = $false
            git_add = $false
            git_commit = $false
            git_push = $false
            merge = $false
            runtime_supervisor_consumable_status = $true
        }
        runtime_supervisor_blocker = $Reason
        next_safe_action = "Stop; routing preview evidence could not be generated."
    }
}

function New-AiOsPacketQueueFallbackPlan {
    param(
        [string]$QueueStatus,
        [string]$Reason
    )

    $nextSafeAction = if ($QueueStatus -eq "empty") {
        "Add candidate packet evidence before planning queue selection."
    }
    else {
        "Stop; packet queue planner evidence could not be generated."
    }

    return [pscustomobject]@{
        schema = "AIOS_PACKET_QUEUE_PLANNER.v1"
        queue_status = $QueueStatus
        selected_packet = $null
        ranked_packets = @()
        blocked_packets = @()
        collision_status = [pscustomobject]@{
            status = "clear"
            collisions = @()
        }
        required_approvals = @()
        next_safe_action = $nextSafeAction
        codex_ready_packet_preview = [pscustomobject]@{
            packet_ready = $false
            reason_code = $Reason
            packet_id = $null
            codex_prompt_text = ""
            write_scope = @()
            validator_chain = @()
        }
        commands_executed = @()
        workers_dispatched = $false
        queues_mutated = $false
        approvals_mutated = $false
        files_written = @()
        safety = [pscustomobject]@{
            preview_only = $true
            evidence_only = $true
            packet_execution = $false
            codex_launch = $false
            worker_dispatch = $false
            queue_mutation = $false
            approval_mutation = $false
            reports_written = $false
            network_access = $false
            git_commit = $false
            git_push = $false
            git_merge = $false
            branch_deletion = $false
        }
    }
}

function New-AiOsCandidateEvidenceFallbackResult {
    param(
        [string]$Status,
        [string]$Reason
    )

    return [pscustomobject]@{
        schema = "AIOS_CANDIDATE_PACKET_EVIDENCE_ADAPTER.v1"
        candidate_status = $Status
        candidate_packets = @()
        candidates = @()
        archive_noise = @()
        default_candidate_used = $false
        today_goal_alignment = [pscustomobject]@{
            milestone = "AIOS self-building machine -> first proof target: industrial-grade forex bot builder -> no broker/live/secrets until gates prove safety"
            proof_target = "industrial-grade forex bot builder"
            control_plane_role = "candidate packet evidence normalization"
            aligned = $false
            blocked_boundaries = @($Reason)
            requires_future_gates_before_execution = $true
        }
        commands_executed = @()
        files_written = @()
        workers_dispatched = $false
        queues_mutated = $false
        approvals_mutated = $false
        safety = [pscustomobject]@{
            preview_only = $true
            evidence_only = $true
            command_execution = $false
            filesystem_writes = $false
            reports_written = $false
            network_access = $false
            worker_dispatch = $false
            queue_mutation = $false
            approval_mutation = $false
            scheduler_activation = $false
            daemon_activation = $false
            broker = $false
            live_trading = $false
            credentials = $false
            real_orders = $false
            real_webhooks = $false
            git_add = $false
            git_commit = $false
            git_push = $false
            git_merge = $false
        }
        blocker = $Reason
        next_safe_action = "Stop; candidate packet evidence could not be generated."
    }
}

function New-AiOsCompletedPacketMemoryFallbackResult {
    param(
        [string]$Status,
        [string]$Reason
    )

    return [pscustomobject]@{
        schema = "AIOS_COMPLETED_PACKET_MEMORY_SUPPRESSION.v1"
        suppression_status = $Status
        active_candidates = @()
        suppressed_candidates = @()
        completed_packet_ids = @()
        suppression_reasons = [pscustomobject]@{}
        next_candidate_available = $false
        next_candidate = $null
        memory_source = [pscustomobject]@{
            source = "runtime_self_route_fallback"
            reason = $Reason
        }
        forex_builder_alignment = [pscustomobject]@{
            milestone = "AIOS self-building machine -> first proof target: industrial-grade forex bot builder -> no broker/live/secrets until gates prove safety"
            proof_target = "industrial-grade forex bot builder"
            control_plane_role = "completed packet memory suppression"
            aligned = $false
            blocked_boundaries = @($Reason)
            requires_future_gates_before_execution = $true
        }
        commands_executed = @()
        files_written = @()
        workers_dispatched = $false
        queues_mutated = $false
        approvals_mutated = $false
        safety = [pscustomobject]@{
            preview_only = $true
            evidence_only = $true
            command_execution = $false
            filesystem_writes = $false
            reports_written = $false
            network_access = $false
            worker_dispatch = $false
            queue_mutation = $false
            approval_mutation = $false
            scheduler_activation = $false
            daemon_activation = $false
            broker = $false
            live_trading = $false
            credentials = $false
            real_orders = $false
            real_webhooks = $false
            git_add = $false
            git_commit = $false
            git_push = $false
            git_merge = $false
        }
        blocker = $Reason
        next_safe_action = "Stop; completed packet memory evidence could not be generated."
    }
}

function New-AiOsForexRoadmapFallbackResult {
    param(
        [string]$Status,
        [string]$Reason
    )

    return [pscustomobject]@{
        schema = "AIOS_FOREX_BUILDER_ROADMAP_CANDIDATE_SOURCE.v1"
        roadmap_status = $Status
        today_goal_alignment = [pscustomobject]@{
            milestone = "AIOS self-building machine -> first proof target: industrial-grade forex bot builder -> no broker/live/secrets until gates prove safety"
            proof_target = "industrial-grade forex bot builder"
            control_plane_role = "safe forex-builder roadmap candidate source"
            aligned = $false
            non_live_only = $true
            blocked_boundaries = @($Reason)
            requires_future_gates_before_execution = $true
        }
        roadmap_candidates = @()
        candidate_packets = @()
        candidates = @()
        forbidden_lanes = @(
            "broker integration",
            "OANDA/live exchange integration",
            "live orders",
            "paper orders unless separately approved",
            "credentials/secrets/env reads/writes",
            "webhooks",
            "scheduler/daemon execution",
            "real-money trading",
            "account mutation",
            "network market automation"
        )
        next_recommended_candidate = $null
        commands_executed = @()
        files_written = @()
        workers_dispatched = $false
        queues_mutated = $false
        approvals_mutated = $false
        safety = [pscustomobject]@{
            preview_only = $true
            evidence_only = $true
            command_execution = $false
            filesystem_writes = $false
            reports_written = $false
            network_access = $false
            worker_dispatch = $false
            queue_mutation = $false
            approval_mutation = $false
            scheduler_activation = $false
            daemon_activation = $false
            broker = $false
            live_trading = $false
            credentials = $false
            real_orders = $false
            real_webhooks = $false
            git_add = $false
            git_commit = $false
            git_push = $false
            git_merge = $false
        }
        blocker = $Reason
        next_safe_action = "Stop; forex-builder roadmap evidence could not be generated."
    }
}

function New-AiOsApprovedExecutorFallbackContract {
    param(
        [string]$Status,
        [string]$Reason,
        [AllowNull()]$SelectedPacket
    )

    return [pscustomobject]@{
        schema = "AIOS_APPROVED_PACKET_EXECUTOR_CONTRACT.v1"
        executor_status = $Status
        selected_packet = $SelectedPacket
        approval_required = $true
        approval_status = "not_evaluated"
        approval_source = ""
        execution_allowed = $false
        command_preview_allowed = $false
        codex_launch_allowed = $false
        protected_action_required = $false
        blocked_reasons = @($Reason)
        rejected_reasons = @()
        required_validators = @()
        allowed_execution_mode = "none"
        forbidden_actions = @(
            "execute_without_matching_human_owner_approval",
            "launch_codex_without_matching_human_owner_approval",
            "dispatch_worker",
            "mutate_queue",
            "mutate_approval_state",
            "start_scheduler_without_separate_approval",
            "start_daemon_without_separate_approval",
            "write_reports",
            "access_network",
            "touch_broker_live_trading_credentials_orders_or_webhooks",
            "git_add",
            "git_commit_without_separate_approval",
            "git_push_without_separate_approval",
            "git_merge_without_separate_approval",
            "git_reset",
            "branch_deletion"
        )
        commands_executed = @()
        workers_dispatched = $false
        queues_mutated = $false
        approvals_mutated = $false
        files_written = @()
        safety = [pscustomobject]@{
            preview_only = $true
            evidence_only = $true
            execution_contract_only = $true
            command_execution = $false
            codex_launch = $false
            worker_dispatch = $false
            queue_mutation = $false
            approval_mutation = $false
            filesystem_writes = $false
            reports_written = $false
            network_access = $false
            scheduler_activation = $false
            daemon_activation = $false
            broker = $false
            live_trading = $false
            credentials = $false
            real_orders = $false
            real_webhooks = $false
            git_add = $false
            git_commit = $false
            git_push = $false
            git_merge = $false
            git_reset = $false
        }
        next_safe_action = "Stop; approved packet executor contract evidence could not be generated."
    }
}

function New-AiOsBlockedCycleLedgerResult {
    param(
        [string]$Reason,
        [AllowNull()]$SelectedPacket,
        [AllowNull()]$CodexReadyPacketPreview,
        [string]$NextSafeAction = "Stop; cycle ledger evidence could not be generated."
    )

    $timestampUtc = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    $safety = [pscustomobject]@{
        preview_only = $true
        evidence_only = $true
        command_execution = $false
        filesystem_writes = $false
        reports_written = $false
        network_access = $false
        subprocess = $false
        worker_dispatch = $false
        queue_mutation = $false
        approval_mutation = $false
        scheduler_activation = $false
        daemon_activation = $false
        broker = $false
        live_trading = $false
        credentials = $false
        real_orders = $false
        real_webhooks = $false
        git_add = $false
        git_commit = $false
        git_push = $false
        git_merge = $false
    }
    $forexAlignment = [pscustomobject]@{
        milestone = "AIOS self-building machine -> first proof target: industrial-grade forex bot builder -> no broker/live/secrets until gates prove safety"
        proof_target = "industrial-grade forex bot builder"
        control_plane_role = "cycle memory, dashboard progress, blocker/SOS decision, next safe action"
        aligned = $true
        blocked_boundaries = @()
        requires_future_gates_before_execution = $true
        sos_required = $false
    }
    $cycleLedger = [pscustomobject]@{
        schema = "AIOS_CYCLE_LEDGER_ENTRY.v1"
        cycle_id = "runtime_self_route_current"
        timestamp_utc = $timestampUtc
        repo_branch = "UNKNOWN"
        repo_head = "UNKNOWN"
        selected_packet = $SelectedPacket
        selected_reason = $Reason
        codex_prompt_emitted = [bool](Get-AiOsObjectProperty -Object $CodexReadyPacketPreview -Name "packet_ready" -Default $false)
        validation_status = "not_run"
        validation_summary = "Cycle ledger generation failed: $Reason"
        pr_number = $null
        pr_status = "none"
        checks_status = "not_run"
        blocker_status = "blocked"
        sos_required = $false
        sos_reason = "No SOS required for cycle ledger generation failure; stop/report."
        next_safe_action = $NextSafeAction
        forex_builder_alignment = $forexAlignment
        safety = $safety
    }
    $dashboardContract = [pscustomobject]@{
        schema = "AIOS_CYCLE_DASHBOARD_CONTRACT.v1"
        current_mission = "AIOS self-building control-plane cycle memory"
        current_cycle = $cycleLedger.cycle_id
        current_packet = [string](Get-AiOsObjectProperty -Object $SelectedPacket -Name "packet_id" -Default "")
        progress_status = "blocked"
        tests_passed = 0
        tests_failed = 0
        pr_status = "none"
        checks_status = "not_run"
        blocker_status = "blocked"
        sos_required = $false
        sos_reason = $cycleLedger.sos_reason
        next_safe_action = $NextSafeAction
        last_updated_utc = $timestampUtc
    }

    return [pscustomobject]@{
        schema = "AIOS_CYCLE_LEDGER_DASHBOARD_SOS.v1"
        cycle_ledger = $cycleLedger
        dashboard_contract = $dashboardContract
        commands_executed = @()
        files_written = @()
        workers_dispatched = $false
        queues_mutated = $false
        approvals_mutated = $false
        safety = $safety
    }
}

function New-AiOsOperatorCheckpointFallbackPanel {
    param(
        [string]$Reason
    )

    return [pscustomobject]@{
        schema = "AIOS_OPERATOR_CHECKPOINT_PANEL.v1"
        status = "blocked"
        mission = "self-building AIOS -> forex-builder proof -> daily earned repo work -> gated trade readiness"
        current_packet = "none"
        state = "BLOCKED"
        checkpoint_summary = [pscustomobject]@{
            mission_check = "aligned"
            packet_check = "none"
            approval_check = "BLOCKED"
            workbench_check = "not_written"
            validation_check = "unknown"
            pr_check = "none"
            sos_check = "no"
            bored_queue_check = "blocked"
        }
        progress_line = "selected=no | prompt=no | tests=unknown | PR=none | SOS=no"
        next_action = "inspect operator checkpoint module blocker"
        bored_queue = @()
        detail_hint = "run with -OutputJson for full report"
        safety_line = "no broker/live/secrets/orders/webhooks"
        lines = @(
            "AIOS STATUS",
            "Mission: self-building AIOS -> forex-builder proof -> daily earned repo work -> gated trade readiness",
            "Packet: none",
            "State: BLOCKED",
            "Progress: selected=no | prompt=no | tests=unknown | PR=none | SOS=no",
            "Next: inspect operator checkpoint module blocker",
            "Bored queue: unavailable because checkpoint panel failed: $Reason",
            "Safety: no broker/live/secrets/orders/webhooks",
            "Details: run with -OutputJson for full report"
        )
    }
}

$recommendation = powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/recommendations/Get-AiOsActionRecommendation.DRY_RUN.ps1 -QuietJson | ConvertFrom-Json
$recommendedCommand = [string](Get-AiOsObjectProperty -Object $recommendation -Name "recommended_command" -Default "")
$recommendationReason = [string](Get-AiOsObjectProperty -Object $recommendation -Name "reason" -Default "")
$contract = Get-AiOsObjectProperty -Object $recommendation -Name "orchestration_result_contract" -Default $null
$contractStatus = [string](Get-AiOsObjectProperty -Object $contract -Name "status" -Default "UNKNOWN")
$approvalRequired = [bool](Get-AiOsObjectProperty -Object $contract -Name "approval_required" -Default $false)
$contractNextSafeAction = [string](Get-AiOsObjectProperty -Object $contract -Name "next_safe_action" -Default "")
$normalizedCommand = $recommendedCommand.Trim()
$hasActionableCommand = -not [string]::IsNullOrWhiteSpace($normalizedCommand) -and $normalizedCommand -notmatch "(?i)^No command recommended"
$commandValidatorPath = "automation/orchestration/validators/Test-AiOsRecommendedCommand.ps1"
$routePreviewPath = "automation/orchestration/aios_bounded_worker_routing_preview.py"
$candidateEvidenceAdapterPath = "automation/orchestration/aios_candidate_packet_evidence_adapter.py"
$completedPacketMemoryPath = "automation/orchestration/aios_completed_packet_memory.py"
$forexBuilderRoadmapPath = "automation/orchestration/aios_forex_builder_roadmap.py"
$packetQueuePlannerPath = "automation/orchestration/aios_packet_queue_planner.py"
$approvedExecutorContractPath = "automation/orchestration/aios_approved_packet_executor_contract.py"
$cycleLedgerPath = "automation/orchestration/aios_cycle_ledger.py"
$operatorCheckpointDashboardPath = "automation/orchestration/aios_operator_checkpoint_dashboard.py"
$packetQueueCandidateEvidenceJson = "[]"
$validationOutput = @()
$validationExitCode = $null
$validationStatus = "NOT_RUN"
$routePreview = $null
$routePreviewOutput = @()
$routePreviewExitCode = $null
$routePreviewStatus = "NOT_RUN"
$routePreviewBlocker = ""
$routePreviewNextSafeAction = ""
$candidateEvidenceResult = $null
$candidateEvidenceOutput = @()
$candidateEvidenceExitCode = $null
$candidateEvidenceStatus = "NOT_RUN"
$candidateEvidenceBlocker = ""
$candidatePackets = @()
$candidateArchiveNoise = @()
$candidateNoisePaths = @()
$candidateArchivePaths = @()
$candidateDefaultUsed = $false
$completedPacketMemory = $null
$completedPacketMemoryOutput = @()
$completedPacketMemoryExitCode = $null
$completedPacketMemoryStatus = "NOT_RUN"
$completedPacketMemoryBlocker = ""
$activeCandidatePackets = @()
$suppressedCandidatePackets = @()
$suppressedPacketIds = @()
$nextCandidateAvailable = $false
$nextCandidate = $null
$completedMemoryNextSafeAction = ""
$forexRoadmap = $null
$forexRoadmapOutput = @()
$forexRoadmapExitCode = $null
$forexRoadmapStatus = "NOT_RUN"
$forexRoadmapBlocker = ""
$forexRoadmapCandidates = @()
$forexRoadmapActiveCandidates = @()
$forexRoadmapSuppressedCandidates = @()
$forexRoadmapSuppressedPacketIds = @()
$forexRoadmapNextCandidate = $null
$forexRoadmapForbiddenLanes = @()
$forexRoadmapNextSafeAction = ""
$forexRoadmapUsed = $false
$plannerCandidatePackets = @()
$packetQueuePlan = $null
$packetQueuePlannerOutput = @()
$packetQueuePlannerExitCode = $null
$packetQueuePlanStatus = "NOT_RUN"
$packetQueuePlannerBlocker = ""
$codexReadyPacketPreview = $null
$selectedPacket = $null
$packetQueueNextSafeAction = ""
$packetQueueCommandsExecuted = @()
$packetQueueWorkersDispatched = $false
$packetQueueQueuesMutated = $false
$packetQueueApprovalsMutated = $false
$packetQueueFilesWritten = @()
$approvedExecutorContract = $null
$approvedExecutorOutput = @()
$approvedExecutorExitCode = $null
$approvedExecutorStatus = "NOT_RUN"
$approvedExecutorBlocker = ""
$executionAllowed = $false
$commandPreviewAllowed = $false
$codexLaunchAllowed = $false
$executorApprovalRequired = $false
$executorApprovalStatus = "NOT_RUN"
$executorApprovalSource = ""
$protectedActionRequired = $false
$executorBlockedReasons = @()
$executorRejectedReasons = @()
$allowedExecutionMode = "none"
$executorNextSafeAction = ""
$cycleLedgerResult = $null
$cycleLedgerOutput = @()
$cycleLedgerExitCode = $null
$cycleLedgerStatus = "NOT_RUN"
$cycleLedgerBlocker = ""
$cycleLedger = $null
$dashboardContract = $null
$dashboardStatus = "NOT_RUN"
$sosRequired = $false
$sosReason = ""
$forexBuilderAlignment = $null
$cycleNextSafeAction = ""
$routeStatus = "report_only"
$exitCode = 0
$rejectionReasons = @()

if ($hasActionableCommand) {
    if (-not (Test-Path -LiteralPath $commandValidatorPath)) {
        $validationStatus = "BLOCKED"
        $routeStatus = "blocked"
        $exitCode = 1
        $rejectionReasons += "recommended_command_validator_missing"
    }
    else {
        $validationOutput = @(powershell -NoProfile -ExecutionPolicy Bypass -File $commandValidatorPath $normalizedCommand)
        $validationExitCode = $LASTEXITCODE
        $validationStatus = if ($validationExitCode -eq 0) { "PASS" } else { "BLOCKED" }

        if ($validationExitCode -ne 0) {
            $routeStatus = "rejected"
            $exitCode = 1
            $rejectionReasons += "recommended_command_failed_validation"
        }
    }
}
else {
    $validationStatus = "NOT_APPLICABLE"
}

$validatedCommandEvidence = [ordered]@{
    command = $normalizedCommand
    validator = $commandValidatorPath
    validation_status = $validationStatus
    status = $validationStatus
    exit_code = $validationExitCode
    output = @($validationOutput)
    execution_allowed = $false
}

$candidateEvidenceInput = [ordered]@{
    schema = "AIOS_RUNTIME_SELF_ROUTE_CANDIDATE_EVIDENCE_INPUT.v1"
    current_mission = "AIOS self-building machine; first proof target: industrial-grade forex bot builder; no broker/live/secrets until gates prove safety."
    today_milestone_context = "AIOS self-building machine -> first proof target: industrial-grade forex bot builder -> no broker/live/secrets until gates prove safety"
    default_candidate_packet_id = "PKT-AIOS-SELFROUTE-CANDIDATE-EVIDENCE-INTEGRATION"
    recommendation_contract_status = $contractStatus
    route_status = $routeStatus
    proposed_packet_records = @(Get-AiOsObjectProperty -Object $recommendation -Name "proposed_packet_records" -Default @())
    candidate_packets = @(Get-AiOsObjectProperty -Object $recommendation -Name "candidate_packets" -Default @())
    manual_candidate_specs = @(Get-AiOsObjectProperty -Object $recommendation -Name "manual_candidate_specs" -Default @())
    work_packet_preview_paths = @(Get-AiOsObjectProperty -Object $recommendation -Name "work_packet_preview_paths" -Default @())
    repo_status = Get-AiOsObjectProperty -Object $recommendation -Name "repo_status" -Default ([ordered]@{})
}

if (-not (Test-Path -LiteralPath $candidateEvidenceAdapterPath)) {
    $candidateEvidenceResult = New-AiOsCandidateEvidenceFallbackResult `
        -Status "blocked" `
        -Reason "candidate_evidence_adapter_missing"
    $candidateEvidenceStatus = "blocked"
    $candidateEvidenceBlocker = "candidate_evidence_adapter_missing"
    $candidateEvidenceExitCode = 1
}
else {
    try {
        $candidateEvidenceInputJson = ConvertTo-Json -InputObject $candidateEvidenceInput -Depth 30 -Compress
        $candidateEvidenceOutput = Invoke-AiOsPythonJsonArgumentScript `
            -ScriptPath $candidateEvidenceAdapterPath `
            -ArgumentName "--evidence" `
            -JsonPayload $candidateEvidenceInputJson
        $candidateEvidenceExitCode = $LASTEXITCODE
        $candidateEvidenceJson = ($candidateEvidenceOutput -join "`n")
        if ($candidateEvidenceExitCode -ne 0) {
            $candidateEvidenceResult = New-AiOsCandidateEvidenceFallbackResult `
                -Status "blocked" `
                -Reason "candidate_evidence_adapter_nonzero_exit"
            $candidateEvidenceStatus = "blocked"
            $candidateEvidenceBlocker = "candidate_evidence_adapter_nonzero_exit"
        }
        elseif ([string]::IsNullOrWhiteSpace($candidateEvidenceJson)) {
            $candidateEvidenceResult = New-AiOsCandidateEvidenceFallbackResult `
                -Status "blocked" `
                -Reason "candidate_evidence_adapter_empty_output"
            $candidateEvidenceStatus = "blocked"
            $candidateEvidenceBlocker = "candidate_evidence_adapter_empty_output"
        }
        else {
            $candidateEvidenceResult = $candidateEvidenceJson | ConvertFrom-Json
            $candidateEvidenceStatus = "ready"
        }
    }
    catch {
        $candidateEvidenceResult = New-AiOsCandidateEvidenceFallbackResult `
            -Status "blocked" `
            -Reason "candidate_evidence_adapter_generation_failed"
        $candidateEvidenceStatus = "blocked"
        $candidateEvidenceBlocker = "candidate_evidence_adapter_generation_failed"
        $candidateEvidenceExitCode = 1
    }
}

$candidatePackets = @(Get-AiOsObjectProperty -Object $candidateEvidenceResult -Name "candidate_packets" -Default @())
$candidateArchiveNoise = @(Get-AiOsObjectProperty -Object $candidateEvidenceResult -Name "archive_noise" -Default @())
$candidateNoisePaths = @(
    $candidateArchiveNoise |
        ForEach-Object { [string](Get-AiOsObjectProperty -Object $_ -Name "path" -Default "") } |
        Where-Object { -not [string]::IsNullOrWhiteSpace($_) }
)
$candidateArchivePaths = @($candidateNoisePaths)
$candidateDefaultUsed = [bool](Get-AiOsObjectProperty -Object $candidateEvidenceResult -Name "default_candidate_used" -Default $false)

if ($candidateEvidenceStatus -eq "blocked") {
    $routeStatus = "blocked"
    $exitCode = 1
    $rejectionReasons += "candidate_evidence_blocked:$candidateEvidenceBlocker"
}

$completedPacketMemoryEvidence = [ordered]@{
    schema = "AIOS_RUNTIME_SELF_ROUTE_COMPLETED_PACKET_MEMORY_EVIDENCE.v1"
    candidate_packets = @($candidatePackets)
    completed_packet_ids = @()
    landed_prs = @()
    commit_history_summary = @()
    cycle_ledger_history = @()
    manual_suppression_rules = @()
    today_goal_context = "AIOS self-building machine -> first proof target: industrial-grade forex bot builder -> no broker/live/secrets until gates prove safety"
}

if (-not (Test-Path -LiteralPath $completedPacketMemoryPath)) {
    $completedPacketMemory = New-AiOsCompletedPacketMemoryFallbackResult `
        -Status "blocked" `
        -Reason "completed_packet_memory_missing"
    $completedPacketMemoryStatus = "blocked"
    $completedPacketMemoryBlocker = "completed_packet_memory_missing"
    $completedPacketMemoryExitCode = 1
}
else {
    try {
        $completedPacketMemoryEvidenceJson = ConvertTo-Json -InputObject $completedPacketMemoryEvidence -Depth 30 -Compress
        $completedPacketMemoryOutput = Invoke-AiOsPythonJsonArgumentScript `
            -ScriptPath $completedPacketMemoryPath `
            -ArgumentName "--evidence" `
            -JsonPayload $completedPacketMemoryEvidenceJson
        $completedPacketMemoryExitCode = $LASTEXITCODE
        $completedPacketMemoryJson = ($completedPacketMemoryOutput -join "`n")
        if ($completedPacketMemoryExitCode -ne 0) {
            $completedPacketMemory = New-AiOsCompletedPacketMemoryFallbackResult `
                -Status "blocked" `
                -Reason "completed_packet_memory_nonzero_exit"
            $completedPacketMemoryStatus = "blocked"
            $completedPacketMemoryBlocker = "completed_packet_memory_nonzero_exit"
        }
        elseif ([string]::IsNullOrWhiteSpace($completedPacketMemoryJson)) {
            $completedPacketMemory = New-AiOsCompletedPacketMemoryFallbackResult `
                -Status "blocked" `
                -Reason "completed_packet_memory_empty_output"
            $completedPacketMemoryStatus = "blocked"
            $completedPacketMemoryBlocker = "completed_packet_memory_empty_output"
            $completedPacketMemoryExitCode = 1
        }
        else {
            $completedPacketMemory = $completedPacketMemoryJson | ConvertFrom-Json
            $completedPacketMemoryStatus = [string](Get-AiOsObjectProperty -Object $completedPacketMemory -Name "suppression_status" -Default "UNKNOWN")
        }
    }
    catch {
        $completedPacketMemory = New-AiOsCompletedPacketMemoryFallbackResult `
            -Status "blocked" `
            -Reason "completed_packet_memory_generation_failed"
        $completedPacketMemoryStatus = "blocked"
        $completedPacketMemoryBlocker = "completed_packet_memory_generation_failed"
        $completedPacketMemoryExitCode = 1
    }
}

$activeCandidatePackets = @(Get-AiOsObjectProperty -Object $completedPacketMemory -Name "active_candidates" -Default @())
$suppressedCandidatePackets = @(Get-AiOsObjectProperty -Object $completedPacketMemory -Name "suppressed_candidates" -Default @())
$suppressedPacketIds = @(
    $suppressedCandidatePackets |
        ForEach-Object { [string](Get-AiOsObjectProperty -Object $_ -Name "packet_id" -Default "") } |
        Where-Object { -not [string]::IsNullOrWhiteSpace($_) }
)
$nextCandidateAvailable = [bool](Get-AiOsObjectProperty -Object $completedPacketMemory -Name "next_candidate_available" -Default $false)
$nextCandidate = Get-AiOsObjectProperty -Object $completedPacketMemory -Name "next_candidate" -Default $null
$completedMemoryNextSafeAction = [string](Get-AiOsObjectProperty -Object $completedPacketMemory -Name "next_safe_action" -Default "")

$forexRoadmapNeeded = @($activeCandidatePackets).Count -eq 0
$forexRoadmapEvidence = [ordered]@{
    schema = "AIOS_RUNTIME_SELF_ROUTE_FOREX_ROADMAP_EVIDENCE.v1"
    completed_packet_memory_status = $completedPacketMemoryStatus
    suppressed_packet_ids = @($suppressedPacketIds)
    active_candidate_count = @($activeCandidatePackets).Count
    completed_memory_next_safe_action = $completedMemoryNextSafeAction
    today_goal_context = "AIOS self-building machine -> first proof target: industrial-grade forex bot builder -> no broker/live/secrets until gates prove safety"
}

if ($forexRoadmapNeeded) {
    if (-not (Test-Path -LiteralPath $forexBuilderRoadmapPath)) {
        $forexRoadmap = New-AiOsForexRoadmapFallbackResult `
            -Status "blocked" `
            -Reason "forex_builder_roadmap_missing"
        $forexRoadmapStatus = "blocked"
        $forexRoadmapBlocker = "forex_builder_roadmap_missing"
        $forexRoadmapExitCode = 1
    }
    else {
        try {
            $forexRoadmapEvidenceJson = ConvertTo-Json -InputObject $forexRoadmapEvidence -Depth 30 -Compress
            $forexRoadmapOutput = Invoke-AiOsPythonJsonArgumentScript `
                -ScriptPath $forexBuilderRoadmapPath `
                -ArgumentName "--evidence" `
                -JsonPayload $forexRoadmapEvidenceJson
            $forexRoadmapExitCode = $LASTEXITCODE
            $forexRoadmapJson = ($forexRoadmapOutput -join "`n")
            if ($forexRoadmapExitCode -ne 0) {
                $forexRoadmap = New-AiOsForexRoadmapFallbackResult `
                    -Status "blocked" `
                    -Reason "forex_builder_roadmap_nonzero_exit"
                $forexRoadmapStatus = "blocked"
                $forexRoadmapBlocker = "forex_builder_roadmap_nonzero_exit"
            }
            elseif ([string]::IsNullOrWhiteSpace($forexRoadmapJson)) {
                $forexRoadmap = New-AiOsForexRoadmapFallbackResult `
                    -Status "blocked" `
                    -Reason "forex_builder_roadmap_empty_output"
                $forexRoadmapStatus = "blocked"
                $forexRoadmapBlocker = "forex_builder_roadmap_empty_output"
                $forexRoadmapExitCode = 1
            }
            else {
                $forexRoadmap = $forexRoadmapJson | ConvertFrom-Json
                $forexRoadmapStatus = [string](Get-AiOsObjectProperty -Object $forexRoadmap -Name "roadmap_status" -Default "UNKNOWN")
            }
        }
        catch {
            $forexRoadmap = New-AiOsForexRoadmapFallbackResult `
                -Status "blocked" `
                -Reason "forex_builder_roadmap_generation_failed"
            $forexRoadmapStatus = "blocked"
            $forexRoadmapBlocker = "forex_builder_roadmap_generation_failed"
            $forexRoadmapExitCode = 1
        }
    }
}
else {
    $forexRoadmap = New-AiOsForexRoadmapFallbackResult `
        -Status "not_needed" `
        -Reason "active_candidate_packets_available"
    $forexRoadmapStatus = "not_needed"
}

$forexRoadmapCandidates = @(Get-AiOsObjectProperty -Object $forexRoadmap -Name "roadmap_candidates" -Default @())
$forexRoadmapNextCandidate = Get-AiOsObjectProperty -Object $forexRoadmap -Name "next_recommended_candidate" -Default $null
$forexRoadmapForbiddenLanes = @(Get-AiOsObjectProperty -Object $forexRoadmap -Name "forbidden_lanes" -Default @())
$forexRoadmapNextSafeAction = [string](Get-AiOsObjectProperty -Object $forexRoadmap -Name "next_safe_action" -Default "")
$forexRoadmapActiveCandidates = @($forexRoadmapCandidates)

if ($forexRoadmapNeeded -and $forexRoadmapStatus -eq "ready" -and @($forexRoadmapCandidates).Count -gt 0) {
    try {
        $forexRoadmapCompletedMemoryEvidence = [ordered]@{
            candidate_packets = @($forexRoadmapCandidates)
            today_goal_context = "AIOS self-building machine; forex-builder roadmap advancement after completed canonical spec #737."
        }
        $forexRoadmapCompletedMemoryEvidenceJson = ConvertTo-Json -InputObject $forexRoadmapCompletedMemoryEvidence -Depth 30 -Compress
        $forexRoadmapCompletedMemoryOutput = Invoke-AiOsPythonJsonArgumentScript `
            -ScriptPath $completedPacketMemoryPath `
            -ArgumentName "--evidence" `
            -JsonPayload $forexRoadmapCompletedMemoryEvidenceJson
        $forexRoadmapCompletedMemoryJson = ($forexRoadmapCompletedMemoryOutput -join "`n")
        if ($LASTEXITCODE -ne 0) {
            $forexRoadmapStatus = "blocked"
            $forexRoadmapBlocker = "forex_roadmap_completed_memory_nonzero_exit"
            $forexRoadmapActiveCandidates = @()
        }
        elseif ([string]::IsNullOrWhiteSpace($forexRoadmapCompletedMemoryJson)) {
            $forexRoadmapStatus = "blocked"
            $forexRoadmapBlocker = "forex_roadmap_completed_memory_empty_output"
            $forexRoadmapActiveCandidates = @()
        }
        else {
            $forexRoadmapCompletedMemory = $forexRoadmapCompletedMemoryJson | ConvertFrom-Json
            $forexRoadmapActiveCandidates = @(Get-AiOsObjectProperty -Object $forexRoadmapCompletedMemory -Name "active_candidates" -Default @())
            $forexRoadmapSuppressedCandidates = @(Get-AiOsObjectProperty -Object $forexRoadmapCompletedMemory -Name "suppressed_candidates" -Default @())
            $forexRoadmapSuppressedPacketIds = @(
                $forexRoadmapSuppressedCandidates |
                    ForEach-Object { [string](Get-AiOsObjectProperty -Object $_ -Name "packet_id" -Default "") } |
                    Where-Object { -not [string]::IsNullOrWhiteSpace($_) }
            )
            if ($forexRoadmapActiveCandidates.Count -gt 0) {
                $forexRoadmapNextCandidate = $forexRoadmapActiveCandidates[0]
            }
        }
    }
    catch {
        $forexRoadmapStatus = "blocked"
        $forexRoadmapBlocker = "forex_roadmap_completed_memory_generation_failed"
        $forexRoadmapActiveCandidates = @()
    }
}

$suppressedCandidatePackets = @($suppressedCandidatePackets + $forexRoadmapSuppressedCandidates)
$suppressedPacketIds = @($suppressedPacketIds + $forexRoadmapSuppressedPacketIds | Select-Object -Unique)
$forexRoadmapUsed = $forexRoadmapNeeded -and $forexRoadmapStatus -eq "ready" -and @($forexRoadmapActiveCandidates).Count -gt 0
$plannerCandidatePackets = if ($forexRoadmapUsed) { @($forexRoadmapNextCandidate) } else { @($activeCandidatePackets) }
$packetQueueCandidateEvidenceJson = ConvertTo-Json -InputObject @($plannerCandidatePackets) -Depth 30 -Compress

if ($completedPacketMemoryStatus -eq "blocked") {
    $routeStatus = "blocked"
    $exitCode = 1
    $rejectionReasons += "completed_packet_memory_blocked:$completedPacketMemoryBlocker"
}
elseif ($completedPacketMemoryStatus -eq "rejected") {
    $routeStatus = "rejected"
    $exitCode = 1
    $rejectionReasons += "completed_packet_memory_rejected"
}

if ($forexRoadmapNeeded -and $forexRoadmapStatus -eq "blocked") {
    $routeStatus = "blocked"
    $exitCode = 1
    $rejectionReasons += "forex_builder_roadmap_blocked:$forexRoadmapBlocker"
}
elseif ($forexRoadmapNeeded -and $forexRoadmapStatus -eq "rejected") {
    $routeStatus = "rejected"
    $exitCode = 1
    $rejectionReasons += "forex_builder_roadmap_rejected"
}

if (-not (Test-Path -LiteralPath $packetQueuePlannerPath)) {
    $packetQueuePlan = New-AiOsPacketQueueFallbackPlan `
        -QueueStatus "blocked" `
        -Reason "packet_queue_planner_missing"
    $packetQueuePlanStatus = "blocked"
    $packetQueuePlannerBlocker = "packet_queue_planner_missing"
    $packetQueuePlannerExitCode = 1
}
else {
    try {
        $packetQueuePlannerOutput = Invoke-AiOsPythonJsonArgumentScript `
            -ScriptPath $packetQueuePlannerPath `
            -ArgumentName "--candidates" `
            -JsonPayload $packetQueueCandidateEvidenceJson
        $packetQueuePlannerExitCode = $LASTEXITCODE
        $packetQueuePlanJson = ($packetQueuePlannerOutput -join "`n")
        if ($packetQueuePlannerExitCode -ne 0) {
            $packetQueuePlan = New-AiOsPacketQueueFallbackPlan `
                -QueueStatus "blocked" `
                -Reason "packet_queue_planner_nonzero_exit"
            $packetQueuePlanStatus = "blocked"
            $packetQueuePlannerBlocker = "packet_queue_planner_nonzero_exit"
        }
        elseif ([string]::IsNullOrWhiteSpace($packetQueuePlanJson)) {
            $packetQueuePlan = New-AiOsPacketQueueFallbackPlan `
                -QueueStatus "empty" `
                -Reason "packet_queue_candidate_evidence_missing"
            $packetQueuePlanStatus = "empty"
            $packetQueuePlannerBlocker = "packet_queue_candidate_evidence_missing"
        }
        else {
            $packetQueuePlan = $packetQueuePlanJson | ConvertFrom-Json
            $packetQueuePlanStatus = [string](Get-AiOsObjectProperty -Object $packetQueuePlan -Name "queue_status" -Default "UNKNOWN")
        }
    }
    catch {
        $packetQueuePlan = New-AiOsPacketQueueFallbackPlan `
            -QueueStatus "blocked" `
            -Reason "packet_queue_planner_generation_failed"
        $packetQueuePlanStatus = "blocked"
        $packetQueuePlannerBlocker = "packet_queue_planner_generation_failed"
        $packetQueuePlannerExitCode = 1
    }
}

$codexReadyPacketPreview = Get-AiOsObjectProperty -Object $packetQueuePlan -Name "codex_ready_packet_preview" -Default $null
$selectedPacket = Get-AiOsObjectProperty -Object $packetQueuePlan -Name "selected_packet" -Default $null
$packetQueueNextSafeAction = [string](Get-AiOsObjectProperty -Object $packetQueuePlan -Name "next_safe_action" -Default "")
$packetQueueCommandsExecuted = @(Get-AiOsObjectProperty -Object $packetQueuePlan -Name "commands_executed" -Default @())
$packetQueueWorkersDispatched = [bool](Get-AiOsObjectProperty -Object $packetQueuePlan -Name "workers_dispatched" -Default $false)
$packetQueueQueuesMutated = [bool](Get-AiOsObjectProperty -Object $packetQueuePlan -Name "queues_mutated" -Default $false)
$packetQueueApprovalsMutated = [bool](Get-AiOsObjectProperty -Object $packetQueuePlan -Name "approvals_mutated" -Default $false)
$packetQueueFilesWritten = @(Get-AiOsObjectProperty -Object $packetQueuePlan -Name "files_written" -Default @())

$approvedExecutorEvidence = [ordered]@{
    schema = "AIOS_RUNTIME_SELF_ROUTE_APPROVED_EXECUTOR_EVIDENCE.v1"
    selected_packet = $selectedPacket
    codex_ready_packet_preview = $codexReadyPacketPreview
    approval_evidence = @()
    source_recommendation_approval_required = $approvalRequired
    report_only = $true
    safety = [ordered]@{
        command_execution = $false
        codex_launch = $false
        worker_dispatch = $false
        queue_mutation = $false
        approval_mutation = $false
        scheduler_activation = $false
        daemon_activation = $false
        reports_written = $false
        network_access = $false
        broker = $false
        live_trading = $false
        credentials = $false
        real_orders = $false
        real_webhooks = $false
    }
}

if (-not (Test-Path -LiteralPath $approvedExecutorContractPath)) {
    $approvedExecutorContract = New-AiOsApprovedExecutorFallbackContract `
        -Status "blocked" `
        -Reason "approved_executor_contract_missing" `
        -SelectedPacket $selectedPacket
    $approvedExecutorStatus = "blocked"
    $approvedExecutorBlocker = "approved_executor_contract_missing"
    $approvedExecutorExitCode = 1
}
else {
    try {
        $approvedExecutorEvidenceJson = $approvedExecutorEvidence | ConvertTo-Json -Depth 30 -Compress
        $approvedExecutorOutput = Invoke-AiOsPythonJsonArgumentScript `
            -ScriptPath $approvedExecutorContractPath `
            -ArgumentName "--evidence" `
            -JsonPayload $approvedExecutorEvidenceJson
        $approvedExecutorExitCode = $LASTEXITCODE
        $approvedExecutorJson = ($approvedExecutorOutput -join "`n")
        if ($approvedExecutorExitCode -ne 0) {
            $approvedExecutorContract = New-AiOsApprovedExecutorFallbackContract `
                -Status "blocked" `
                -Reason "approved_executor_contract_nonzero_exit" `
                -SelectedPacket $selectedPacket
            $approvedExecutorStatus = "blocked"
            $approvedExecutorBlocker = "approved_executor_contract_nonzero_exit"
        }
        elseif ([string]::IsNullOrWhiteSpace($approvedExecutorJson)) {
            $approvedExecutorContract = New-AiOsApprovedExecutorFallbackContract `
                -Status "blocked" `
                -Reason "approved_executor_contract_empty_output" `
                -SelectedPacket $selectedPacket
            $approvedExecutorStatus = "blocked"
            $approvedExecutorBlocker = "approved_executor_contract_empty_output"
        }
        else {
            $approvedExecutorContract = $approvedExecutorJson | ConvertFrom-Json
            $approvedExecutorStatus = [string](Get-AiOsObjectProperty -Object $approvedExecutorContract -Name "executor_status" -Default "UNKNOWN")
        }
    }
    catch {
        $approvedExecutorContract = New-AiOsApprovedExecutorFallbackContract `
            -Status "blocked" `
            -Reason "approved_executor_contract_generation_failed" `
            -SelectedPacket $selectedPacket
        $approvedExecutorStatus = "blocked"
        $approvedExecutorBlocker = "approved_executor_contract_generation_failed"
        $approvedExecutorExitCode = 1
    }
}

$executionAllowed = [bool](Get-AiOsObjectProperty -Object $approvedExecutorContract -Name "execution_allowed" -Default $false)
$commandPreviewAllowed = [bool](Get-AiOsObjectProperty -Object $approvedExecutorContract -Name "command_preview_allowed" -Default $false)
$codexLaunchAllowed = $false
$executorApprovalRequired = [bool](Get-AiOsObjectProperty -Object $approvedExecutorContract -Name "approval_required" -Default $false)
$executorApprovalStatus = [string](Get-AiOsObjectProperty -Object $approvedExecutorContract -Name "approval_status" -Default "")
$executorApprovalSource = [string](Get-AiOsObjectProperty -Object $approvedExecutorContract -Name "approval_source" -Default "")
$protectedActionRequired = [bool](Get-AiOsObjectProperty -Object $approvedExecutorContract -Name "protected_action_required" -Default $false)
$executorBlockedReasons = @(Get-AiOsObjectProperty -Object $approvedExecutorContract -Name "blocked_reasons" -Default @())
$executorRejectedReasons = @(Get-AiOsObjectProperty -Object $approvedExecutorContract -Name "rejected_reasons" -Default @())
$allowedExecutionMode = [string](Get-AiOsObjectProperty -Object $approvedExecutorContract -Name "allowed_execution_mode" -Default "none")
$executorNextSafeAction = [string](Get-AiOsObjectProperty -Object $approvedExecutorContract -Name "next_safe_action" -Default "")

if ($approvedExecutorStatus -eq "rejected") {
    $routeStatus = "rejected"
    $exitCode = 1
    $rejectionReasons += "approved_executor_rejected"
    foreach ($executorReason in $executorRejectedReasons) {
        $rejectionReasons += "approved_executor_rejected:$executorReason"
    }
}

if ($routeStatus -eq "report_only") {
    if ($contractStatus -eq "BLOCKED") {
        $routeStatus = "blocked"
        $exitCode = 1
        $rejectionReasons += "recommendation_contract_blocked"
    }
    elseif ($hasActionableCommand -and $validationStatus -eq "PASS") {
        $routeStatus = "route_ready_report_only"
    }
    elseif (-not $hasActionableCommand) {
        $routeStatus = "no_action_report_only"
    }
}

if (-not (Test-Path -LiteralPath $routePreviewPath)) {
    $routePreview = New-AiOsBlockedRoutePreview `
        -Reason "route_preview_module_missing" `
        -SourceRecommendation $recommendation `
        -ValidatedCommand $validatedCommandEvidence
    $routePreviewStatus = "blocked"
    $routePreviewBlocker = "route_preview_module_missing"
    $routePreviewExitCode = 1
}
else {
    try {
        $recommendationJson = $recommendation | ConvertTo-Json -Depth 20 -Compress
        $validatedCommandJson = $validatedCommandEvidence | ConvertTo-Json -Depth 10 -Compress
        $routePreviewOutput = @(
            python $routePreviewPath `
                --recommendation $recommendationJson `
                --validated-command $validatedCommandJson
        )
        $routePreviewExitCode = $LASTEXITCODE
        $routePreviewJson = ($routePreviewOutput -join "`n")
        if ([string]::IsNullOrWhiteSpace($routePreviewJson)) {
            $routePreview = New-AiOsBlockedRoutePreview `
                -Reason "route_preview_empty_output" `
                -SourceRecommendation $recommendation `
                -ValidatedCommand $validatedCommandEvidence
            $routePreviewStatus = "blocked"
            $routePreviewBlocker = "route_preview_empty_output"
        }
        else {
            $routePreview = $routePreviewJson | ConvertFrom-Json
            $routePreviewStatus = [string](Get-AiOsObjectProperty -Object $routePreview -Name "routing_status" -Default "UNKNOWN")
            $routePreviewBlocker = [string](Get-AiOsObjectProperty -Object $routePreview -Name "runtime_supervisor_blocker" -Default "")
            $routePreviewNextSafeAction = [string](Get-AiOsObjectProperty -Object $routePreview -Name "next_safe_action" -Default "")
        }
    }
    catch {
        $routePreview = New-AiOsBlockedRoutePreview `
            -Reason "route_preview_generation_failed" `
            -SourceRecommendation $recommendation `
            -ValidatedCommand $validatedCommandEvidence
        $routePreviewStatus = "blocked"
        $routePreviewBlocker = "route_preview_generation_failed"
        $routePreviewExitCode = 1
    }
}

if ($routePreviewStatus -in @("blocked", "rejected")) {
    $routeStatus = $routePreviewStatus
    $exitCode = 1
    $rejectionReasons += "route_preview_$routePreviewStatus"
    if (-not [string]::IsNullOrWhiteSpace($routePreviewBlocker)) {
        $rejectionReasons += "route_preview_blocker:$routePreviewBlocker"
    }
}
elseif ($routePreviewStatus -eq "route_ready" -and $validationStatus -notin @("PASS")) {
    $routeStatus = "blocked"
    $exitCode = 1
    $rejectionReasons += "route_preview_ready_without_validated_command"
}

if ($packetQueuePlanStatus -in @("blocked", "rejected")) {
    $routeStatus = $packetQueuePlanStatus
    $exitCode = 1
    $rejectionReasons += "packet_queue_plan_$packetQueuePlanStatus"
    if (-not [string]::IsNullOrWhiteSpace($packetQueuePlannerBlocker)) {
        $rejectionReasons += "packet_queue_blocker:$packetQueuePlannerBlocker"
    }
}

$nextSafeAction = if ($forexRoadmapUsed -and -not [string]::IsNullOrWhiteSpace($executorNextSafeAction)) {
    $executorNextSafeAction
}
elseif ($forexRoadmapUsed -and -not [string]::IsNullOrWhiteSpace($forexRoadmapNextSafeAction)) {
    $forexRoadmapNextSafeAction
}
elseif ($completedPacketMemoryStatus -eq "ready" -and -not $nextCandidateAvailable -and -not $forexRoadmapUsed -and -not [string]::IsNullOrWhiteSpace($completedMemoryNextSafeAction)) {
    $completedMemoryNextSafeAction
}
elseif (-not [string]::IsNullOrWhiteSpace($contractNextSafeAction)) {
    $contractNextSafeAction
}
elseif ($routePreviewStatus -in @("blocked", "rejected") -and -not [string]::IsNullOrWhiteSpace($routePreviewNextSafeAction)) {
    $routePreviewNextSafeAction
}
elseif ($hasActionableCommand) {
    "Use this validated recommendation as evidence for a separate bounded packet. Do not execute it from self-route."
}
else {
    "Stop or idle according to the action recommendation; no command is executable from self-route."
}

$repoBranch = [string](Get-AiOsObjectProperty -Object $recommendation -Name "repo_branch" -Default "")
if ([string]::IsNullOrWhiteSpace($repoBranch)) {
    $repoBranch = [string](Get-AiOsObjectProperty -Object $contract -Name "repo_branch" -Default "UNKNOWN")
}
$repoHead = [string](Get-AiOsObjectProperty -Object $recommendation -Name "repo_head" -Default "")
if ([string]::IsNullOrWhiteSpace($repoHead)) {
    $repoHead = [string](Get-AiOsObjectProperty -Object $contract -Name "repo_head" -Default "UNKNOWN")
}
$selectedReason = if ($packetQueuePlanStatus -eq "selected") {
    "packet_queue_plan_selected"
}
elseif ($packetQueuePlanStatus -eq "empty") {
    "packet_queue_plan_empty"
}
else {
    "packet_queue_plan_$packetQueuePlanStatus"
}
$blockerStatus = if ($routeStatus -in @("blocked", "rejected") -or $rejectionReasons.Count -gt 0) {
    "blocked"
}
else {
    "none"
}
$validationSummary = if ($validationOutput.Count -gt 0) {
    ($validationOutput -join "; ")
}
elseif ($validationStatus -eq "NOT_APPLICABLE") {
    "No recommended command validation was needed."
}
else {
    "Validation status: $validationStatus"
}
$cycleEvidence = [ordered]@{
    cycle_id = "runtime_self_route_current"
    timestamp_utc = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    repo_branch = $repoBranch
    repo_head = $repoHead
    current_mission = "AIOS self-building machine; first proof target: industrial-grade forex bot builder; no broker/live/secrets until gates prove safety."
    route_status = $routeStatus
    packet_queue_plan = $packetQueuePlan
    selected_packet = $selectedPacket
    selected_reason = $selectedReason
    codex_ready_packet_preview = $codexReadyPacketPreview
    codex_prompt_emitted = [bool](Get-AiOsObjectProperty -Object $codexReadyPacketPreview -Name "packet_ready" -Default $false)
    validation_status = $validationStatus
    validation_summary = $validationSummary
    pr_number = $null
    pr_status = "none"
    checks_status = "not_run"
    blocker_status = $blockerStatus
    blockers = @($rejectionReasons | Select-Object -Unique)
    next_safe_action = $nextSafeAction
    stop_condition = "report_only"
    source_recommendation_approval_required = $approvalRequired
    approval_required = [ordered]@{
        human_owner_review = $false
    }
    safety = [ordered]@{
        broker = $false
        live_trading = $false
        credentials = $false
        secrets = $false
        real_orders = $false
        real_webhooks = $false
        worker_dispatch = $false
        queue_mutation = $false
        approval_mutation = $false
        scheduler_activation = $false
        daemon_activation = $false
        reports_written = $false
        network_access = $false
    }
}

if (-not (Test-Path -LiteralPath $cycleLedgerPath)) {
    $cycleLedgerResult = New-AiOsBlockedCycleLedgerResult `
        -Reason "cycle_ledger_module_missing" `
        -SelectedPacket $selectedPacket `
        -CodexReadyPacketPreview $codexReadyPacketPreview `
        -NextSafeAction "Stop; cycle ledger module is missing."
    $cycleLedgerStatus = "blocked"
    $cycleLedgerBlocker = "cycle_ledger_module_missing"
    $cycleLedgerExitCode = 1
}
else {
    try {
        $cycleEvidenceJson = $cycleEvidence | ConvertTo-Json -Depth 30 -Compress
        $cycleLedgerOutput = Invoke-AiOsPythonJsonArgumentScript `
            -ScriptPath $cycleLedgerPath `
            -ArgumentName "--evidence" `
            -JsonPayload $cycleEvidenceJson
        $cycleLedgerExitCode = $LASTEXITCODE
        $cycleLedgerJson = ($cycleLedgerOutput -join "`n")
        if ($cycleLedgerExitCode -ne 0) {
            $cycleLedgerResult = New-AiOsBlockedCycleLedgerResult `
                -Reason "cycle_ledger_nonzero_exit" `
                -SelectedPacket $selectedPacket `
                -CodexReadyPacketPreview $codexReadyPacketPreview `
                -NextSafeAction "Stop; cycle ledger generation returned a nonzero exit."
            $cycleLedgerStatus = "blocked"
            $cycleLedgerBlocker = "cycle_ledger_nonzero_exit"
        }
        elseif ([string]::IsNullOrWhiteSpace($cycleLedgerJson)) {
            $cycleLedgerResult = New-AiOsBlockedCycleLedgerResult `
                -Reason "cycle_ledger_empty_output" `
                -SelectedPacket $selectedPacket `
                -CodexReadyPacketPreview $codexReadyPacketPreview `
                -NextSafeAction "Stop; cycle ledger generation returned empty output."
            $cycleLedgerStatus = "blocked"
            $cycleLedgerBlocker = "cycle_ledger_empty_output"
        }
        else {
            $cycleLedgerResult = $cycleLedgerJson | ConvertFrom-Json
            $cycleLedgerStatus = "ready"
        }
    }
    catch {
        $cycleLedgerResult = New-AiOsBlockedCycleLedgerResult `
            -Reason "cycle_ledger_generation_failed" `
            -SelectedPacket $selectedPacket `
            -CodexReadyPacketPreview $codexReadyPacketPreview `
            -NextSafeAction "Stop; cycle ledger evidence could not be generated."
        $cycleLedgerStatus = "blocked"
        $cycleLedgerBlocker = "cycle_ledger_generation_failed"
        $cycleLedgerExitCode = 1
    }
}

$cycleLedger = Get-AiOsObjectProperty -Object $cycleLedgerResult -Name "cycle_ledger" -Default $null
$dashboardContract = Get-AiOsObjectProperty -Object $cycleLedgerResult -Name "dashboard_contract" -Default $null
$dashboardStatus = if ($null -eq $dashboardContract) { "blocked" } else { "ready" }
$sosRequired = [bool](Get-AiOsObjectProperty -Object $dashboardContract -Name "sos_required" -Default $false)
$sosReason = [string](Get-AiOsObjectProperty -Object $dashboardContract -Name "sos_reason" -Default "")
$forexBuilderAlignment = Get-AiOsObjectProperty -Object $cycleLedger -Name "forex_builder_alignment" -Default $null
$cycleNextSafeAction = [string](Get-AiOsObjectProperty -Object $dashboardContract -Name "next_safe_action" -Default "")

if ($cycleLedgerStatus -eq "blocked") {
    $routeStatus = "blocked"
    $exitCode = 1
    $rejectionReasons += "cycle_ledger_blocked:$cycleLedgerBlocker"
}
if ($sosRequired) {
    $routeStatus = "blocked"
    $exitCode = 1
    $rejectionReasons += "cycle_ledger_sos_required:$sosReason"
}

$report = [pscustomobject]@{
    schema = "AIOS_RUNTIME_SELF_ROUTE_REPORT.v1"
    mode = if ($Apply) { "APPLY_REPORT_ONLY" } else { "DRY_RUN_REPORT_ONLY" }
    route_status = $routeStatus
    recommended_command = $recommendedCommand
    recommendation_reason = $recommendationReason
    recommendation_contract_status = $contractStatus
    recommendation_approval_required = $approvalRequired
    command_validation_status = $validationStatus
    command_validation_exit_code = $validationExitCode
    command_validation_output = @($validationOutput)
    route_preview_status = $routePreviewStatus
    route_preview_exit_code = $routePreviewExitCode
    route_preview = $routePreview
    candidate_evidence_status = $candidateEvidenceStatus
    candidate_evidence = $candidateEvidenceResult
    candidate_packets = @($candidatePackets)
    candidate_noise_paths = @($candidateNoisePaths)
    candidate_archive_paths = @($candidateArchivePaths)
    candidate_default_used = $candidateDefaultUsed
    completed_packet_memory_status = $completedPacketMemoryStatus
    completed_packet_memory = $completedPacketMemory
    active_candidate_packets = @($activeCandidatePackets)
    suppressed_candidate_packets = @($suppressedCandidatePackets)
    suppressed_packet_ids = @($suppressedPacketIds)
    next_candidate_available = $nextCandidateAvailable
    next_candidate = $nextCandidate
    completed_memory_next_safe_action = $completedMemoryNextSafeAction
    forex_roadmap_status = $forexRoadmapStatus
    forex_roadmap = $forexRoadmap
    forex_roadmap_candidates = @($forexRoadmapCandidates)
    forex_roadmap_active_candidates = @($forexRoadmapActiveCandidates)
    forex_roadmap_next_candidate = $forexRoadmapNextCandidate
    forex_roadmap_suppressed_packet_ids = @($forexRoadmapSuppressedPacketIds)
    forex_roadmap_forbidden_lanes = @($forexRoadmapForbiddenLanes)
    forex_roadmap_used = $forexRoadmapUsed
    packet_queue_plan_status = $packetQueuePlanStatus
    packet_queue_plan = $packetQueuePlan
    codex_ready_packet_preview = $codexReadyPacketPreview
    selected_packet = $selectedPacket
    packet_queue_next_safe_action = $packetQueueNextSafeAction
    packet_queue_commands_executed = @($packetQueueCommandsExecuted)
    packet_queue_workers_dispatched = $packetQueueWorkersDispatched
    packet_queue_queues_mutated = $packetQueueQueuesMutated
    packet_queue_approvals_mutated = $packetQueueApprovalsMutated
    packet_queue_files_written = @($packetQueueFilesWritten)
    approved_executor_status = $approvedExecutorStatus
    approved_executor_contract = $approvedExecutorContract
    execution_allowed = $executionAllowed
    command_preview_allowed = $commandPreviewAllowed
    codex_launch_allowed = $codexLaunchAllowed
    approval_required = $executorApprovalRequired
    approval_status = $executorApprovalStatus
    approval_source = $executorApprovalSource
    protected_action_required = $protectedActionRequired
    executor_blocked_reasons = @($executorBlockedReasons)
    executor_rejected_reasons = @($executorRejectedReasons)
    allowed_execution_mode = $allowedExecutionMode
    executor_next_safe_action = $executorNextSafeAction
    cycle_ledger_status = $cycleLedgerStatus
    cycle_ledger = $cycleLedger
    dashboard_contract = $dashboardContract
    dashboard_status = $dashboardStatus
    sos_required = $sosRequired
    sos_reason = $sosReason
    forex_builder_alignment = $forexBuilderAlignment
    cycle_next_safe_action = $cycleNextSafeAction
    command_execution_allowed = $false
    command_executed = $false
    rejection_reasons = @($rejectionReasons | Select-Object -Unique)
    next_safe_action = $nextSafeAction
    stop_condition = "REPORT_ONLY_NO_RECOMMENDED_COMMAND_EXECUTION"
    safety = [pscustomobject]@{
        autonomous_execution = $false
        live_worker_dispatch = $false
        scheduler_activation = $false
        daemon_activation = $false
        queue_mutation = $false
        approval_mutation = $false
        broker = $false
        credentials = $false
        live_trading = $false
        real_orders = $false
        real_webhooks = $false
        network = $false
        reports_written = $false
        files_written = $false
        git_add = $false
        git_commit = $false
        git_push = $false
        merge = $false
    }
}

$operatorCheckpointPanel = $null
$operatorCheckpointExitCode = $null
$operatorCheckpointBlocker = ""

if (-not (Test-Path -LiteralPath $operatorCheckpointDashboardPath)) {
    $operatorCheckpointBlocker = "operator_checkpoint_dashboard_missing"
    $operatorCheckpointPanel = New-AiOsOperatorCheckpointFallbackPanel -Reason $operatorCheckpointBlocker
    $operatorCheckpointExitCode = 1
}
else {
    try {
        $operatorCheckpointEvidence = [ordered]@{
            selected_packet = $selectedPacket
            codex_ready_packet_preview = $codexReadyPacketPreview
            approved_executor_status = $approvedExecutorStatus
            approval_status = $executorApprovalStatus
            execution_allowed = $executionAllowed
            command_validation_status = $validationStatus
            dashboard_contract = $dashboardContract
            cycle_ledger = $cycleLedger
            sos_required = $sosRequired
            rejection_reasons = @($rejectionReasons | Select-Object -Unique)
            next_safe_action = $nextSafeAction
            active_candidate_packets = @($activeCandidatePackets)
            candidate_packets = @($candidatePackets)
            forex_roadmap_candidates = @($forexRoadmapCandidates)
            packet_queue_plan = $packetQueuePlan
        }
        $operatorCheckpointInputJson = $operatorCheckpointEvidence | ConvertTo-Json -Depth 30 -Compress
        $operatorCheckpointOutput = Invoke-AiOsPythonJsonArgumentScript `
            -ScriptPath $operatorCheckpointDashboardPath `
            -ArgumentName "--report" `
            -JsonPayload $operatorCheckpointInputJson
        $operatorCheckpointExitCode = $LASTEXITCODE
        $operatorCheckpointJson = ($operatorCheckpointOutput -join "`n")
        if ($operatorCheckpointExitCode -ne 0) {
            $operatorCheckpointBlocker = "operator_checkpoint_dashboard_nonzero_exit"
            $operatorCheckpointPanel = New-AiOsOperatorCheckpointFallbackPanel -Reason $operatorCheckpointBlocker
        }
        elseif ([string]::IsNullOrWhiteSpace($operatorCheckpointJson)) {
            $operatorCheckpointBlocker = "operator_checkpoint_dashboard_empty_output"
            $operatorCheckpointPanel = New-AiOsOperatorCheckpointFallbackPanel -Reason $operatorCheckpointBlocker
        }
        else {
            $operatorCheckpointPanel = $operatorCheckpointJson | ConvertFrom-Json
        }
    }
    catch {
        $operatorCheckpointBlocker = "operator_checkpoint_dashboard_generation_failed"
        $operatorCheckpointPanel = New-AiOsOperatorCheckpointFallbackPanel -Reason $operatorCheckpointBlocker
        $operatorCheckpointExitCode = 1
    }
}

$operatorCheckpointStatus = [string](Get-AiOsObjectProperty -Object $operatorCheckpointPanel -Name "status" -Default "blocked")
$operatorCheckpointLines = @(Get-AiOsObjectProperty -Object $operatorCheckpointPanel -Name "lines" -Default @("AIOS STATUS", "State: BLOCKED", "Next: inspect operator checkpoint details"))
$boredQueueCandidates = @(Get-AiOsObjectProperty -Object $operatorCheckpointPanel -Name "bored_queue" -Default @())
$boredQueueStatus = if ($boredQueueCandidates.Count -gt 0) {
    "available"
}
elseif ($null -eq $selectedPacket) {
    "empty"
}
else {
    "inactive"
}
$compactDashboardStatus = if ($operatorCheckpointStatus -eq "ready" -and $operatorCheckpointLines.Count -gt 0) {
    "ready"
}
else {
    "blocked"
}

$report | Add-Member -NotePropertyName operator_checkpoint_status -NotePropertyValue $operatorCheckpointStatus -Force
$report | Add-Member -NotePropertyName operator_checkpoint_panel -NotePropertyValue $operatorCheckpointPanel -Force
$report | Add-Member -NotePropertyName operator_checkpoint_lines -NotePropertyValue $operatorCheckpointLines -Force
$report | Add-Member -NotePropertyName bored_queue_status -NotePropertyValue $boredQueueStatus -Force
$report | Add-Member -NotePropertyName bored_queue_candidates -NotePropertyValue $boredQueueCandidates -Force
$report | Add-Member -NotePropertyName compact_dashboard_status -NotePropertyValue $compactDashboardStatus -Force

if ($QuietJson -or $OutputJson) {
    $report | ConvertTo-Json -Depth 20
    exit $exitCode
}

foreach ($line in $operatorCheckpointLines) {
    Write-Host $line
}

if ($Detailed) {
    Write-Host ""
    Write-Host "Recommended command:"
    Write-Host $recommendedCommand
    Write-Host ""
    Write-Host "Route status: $routeStatus"
    Write-Host "Contract status: $contractStatus"
    Write-Host "Approval required: $approvalRequired"
    Write-Host "Command validation: $validationStatus"
    Write-Host "Route preview: $routePreviewStatus"
    if (-not [string]::IsNullOrWhiteSpace($routePreviewBlocker)) {
        Write-Host "Route preview blocker: $routePreviewBlocker"
    }
    Write-Host "Candidate evidence: $candidateEvidenceStatus"
    if (-not [string]::IsNullOrWhiteSpace($candidateEvidenceBlocker)) {
        Write-Host "Candidate evidence blocker: $candidateEvidenceBlocker"
    }
    Write-Host "Completed packet memory: $completedPacketMemoryStatus"
    if (-not [string]::IsNullOrWhiteSpace($completedPacketMemoryBlocker)) {
        Write-Host "Completed packet memory blocker: $completedPacketMemoryBlocker"
    }
    Write-Host "Forex roadmap: $forexRoadmapStatus"
    if (-not [string]::IsNullOrWhiteSpace($forexRoadmapBlocker)) {
        Write-Host "Forex roadmap blocker: $forexRoadmapBlocker"
    }
    Write-Host "Packet queue plan: $packetQueuePlanStatus"
    if (-not [string]::IsNullOrWhiteSpace($packetQueuePlannerBlocker)) {
        Write-Host "Packet queue blocker: $packetQueuePlannerBlocker"
    }
    Write-Host "Approved executor: $approvedExecutorStatus"
    Write-Host "Execution allowed: $executionAllowed"
    if (-not [string]::IsNullOrWhiteSpace($approvedExecutorBlocker)) {
        Write-Host "Approved executor blocker: $approvedExecutorBlocker"
    }
    Write-Host "Cycle ledger: $cycleLedgerStatus"
    Write-Host "Dashboard: $dashboardStatus"
    Write-Host "SOS required: $sosRequired"
    if (-not [string]::IsNullOrWhiteSpace($sosReason)) {
        Write-Host "SOS reason: $sosReason"
    }
    if (-not [string]::IsNullOrWhiteSpace($cycleLedgerBlocker)) {
        Write-Host "Cycle ledger blocker: $cycleLedgerBlocker"
    }
    foreach ($line in $validationOutput) {
        Write-Host $line
    }
    Write-Host ""
    Write-Host "Next safe action:"
    Write-Host $nextSafeAction
    Write-Host ""
    Write-Host "Command executed: NO"
    Write-Host "Commit performed: NO"
    Write-Host "Push performed: NO"
    Write-Host "Stop condition: REPORT_ONLY_NO_RECOMMENDED_COMMAND_EXECUTION"
}

exit $exitCode
