from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SUPERVISOR = (
    REPO_ROOT
    / "automation"
    / "orchestration"
    / "runtime"
    / "Start-AiOsPersistentRuntimeSupervisor.ps1"
)


def supervisor_text() -> str:
    return SUPERVISOR.read_text(encoding="utf-8").replace("\r\n", "\n")


def self_route_text() -> str:
    self_route = (
        REPO_ROOT
        / "automation"
        / "orchestration"
        / "runtime"
        / "Invoke-AiOsRuntimeSelfRoute.ps1"
    )
    return self_route.read_text(encoding="utf-8").replace("\r\n", "\n")


def forex_roadmap_text() -> str:
    roadmap = REPO_ROOT / "automation" / "orchestration" / "aios_forex_builder_roadmap.py"
    return roadmap.read_text(encoding="utf-8").replace("\r\n", "\n")


def test_self_route_apply_is_only_inside_apply_branch() -> None:
    text = supervisor_text()
    lines = text.splitlines()
    apply_line = (
        "        powershell -ExecutionPolicy Bypass -File "
        "automation/orchestration/runtime/Invoke-AiOsRuntimeSelfRoute.ps1 -Apply"
    )
    dry_run_line = (
        "        powershell -ExecutionPolicy Bypass -File "
        "automation/orchestration/runtime/Invoke-AiOsRuntimeSelfRoute.ps1"
    )

    assert apply_line in lines
    assert dry_run_line in lines
    assert (
        "    powershell -ExecutionPolicy Bypass -File "
        "automation/orchestration/runtime/Invoke-AiOsRuntimeSelfRoute.ps1 -Apply"
    ) not in lines


def test_self_route_apply_branch_has_non_apply_else_branch() -> None:
    text = supervisor_text()

    assert (
        "    if ($Apply) {\n"
        "        powershell -ExecutionPolicy Bypass -File "
        "automation/orchestration/runtime/Invoke-AiOsRuntimeSelfRoute.ps1 -Apply\n"
        "    } else {\n"
        "        powershell -ExecutionPolicy Bypass -File "
        "automation/orchestration/runtime/Invoke-AiOsRuntimeSelfRoute.ps1\n"
        "    }\n"
        "    $selfRouteResult = Convert-AiOsExitCodeToAuditResult -ExitCode $LASTEXITCODE"
    ) in text


def test_packet_advancement_remains_conditional() -> None:
    text = supervisor_text()

    assert (
        "    if ($Apply) {\n"
        "        powershell -ExecutionPolicy Bypass -File "
        "automation/orchestration/runtime/Invoke-AiOsRuntimePacketAdvancement.ps1 -Apply\n"
        "    } else {\n"
        "        powershell -ExecutionPolicy Bypass -File "
        "automation/orchestration/runtime/Invoke-AiOsRuntimePacketAdvancement.ps1\n"
        "    }\n"
        "    $packetAdvancementResult = Convert-AiOsExitCodeToAuditResult -ExitCode $LASTEXITCODE"
    ) in text


def test_self_route_never_executes_recommended_command() -> None:
    text = self_route_text()

    assert "Invoke-Expression" not in text
    assert "command_execution_allowed = $false" in text
    assert "command_executed = $false" in text
    assert "REPORT_ONLY_NO_RECOMMENDED_COMMAND_EXECUTION" in text


def test_self_route_apply_mode_is_report_only() -> None:
    text = self_route_text()

    assert "APPLY_REPORT_ONLY" in text
    assert "DRY_RUN_REPORT_ONLY" in text
    assert "Test-AiOsRecommendedCommand.ps1" in text
    assert "Do not execute it from self-route." in text


def test_self_route_json_includes_bounded_worker_route_preview() -> None:
    text = self_route_text()

    assert "AIOS_BOUNDED_WORKER_ROUTING_PREVIEW.v1" in text
    assert "automation/orchestration/aios_bounded_worker_routing_preview.py" in text
    assert "route_preview_status = $routePreviewStatus" in text
    assert "route_preview_exit_code = $routePreviewExitCode" in text
    assert "route_preview = $routePreview" in text


def test_self_route_passes_validation_evidence_to_route_preview() -> None:
    text = self_route_text()

    assert "$validatedCommandEvidence = [ordered]@{" in text
    assert "validation_status = $validationStatus" in text
    assert "status = $validationStatus" in text
    assert "execution_allowed = $false" in text
    assert "--validated-command $validatedCommandJson" in text


def test_self_route_route_preview_is_evidence_only() -> None:
    text = self_route_text()

    assert "commands_executed = @()" in text
    assert "queues_mutated = $false" in text
    assert "approvals_mutated = $false" in text
    assert "workers_dispatched = $false" in text
    assert "worker_dispatch = $false" in text
    assert "queue_mutation = $false" in text
    assert "approval_mutation = $false" in text


def test_self_route_blocked_route_preview_stops_advancement() -> None:
    text = self_route_text()

    assert 'if ($routePreviewStatus -in @("blocked", "rejected")) {' in text
    assert "$routeStatus = $routePreviewStatus" in text
    assert '$rejectionReasons += "route_preview_$routePreviewStatus"' in text
    assert "route_preview_blocker:$routePreviewBlocker" in text
    assert "$exitCode = 1" in text


def test_self_route_unvalidated_preview_cannot_be_route_ready() -> None:
    text = self_route_text()

    assert 'elseif ($routePreviewStatus -eq "route_ready" -and $validationStatus -notin @("PASS")) {' in text
    assert '$routeStatus = "blocked"' in text
    assert '$rejectionReasons += "route_preview_ready_without_validated_command"' in text


def test_self_route_references_packet_queue_planner() -> None:
    text = self_route_text()

    assert "automation/orchestration/aios_packet_queue_planner.py" in text
    assert '-ArgumentName "--candidates"' in text
    assert "-JsonPayload $packetQueueCandidateEvidenceJson" in text


def test_self_route_references_candidate_packet_evidence_adapter() -> None:
    text = self_route_text()

    assert "automation/orchestration/aios_candidate_packet_evidence_adapter.py" in text
    assert "-ScriptPath $candidateEvidenceAdapterPath" in text
    assert '-ArgumentName "--evidence"' in text
    assert "-JsonPayload $candidateEvidenceInputJson" in text


def test_self_route_uses_windows_safe_json_argument_handoff() -> None:
    text = self_route_text()

    assert "function Invoke-AiOsPythonJsonArgumentScript" in text
    assert "$encodedPayload = [Convert]::ToBase64String" in text
    assert "base64.b64decode(sys.argv[3]).decode()" in text
    assert "runpy.run_path(p,run_name=n)" in text


def test_self_route_json_includes_candidate_packet_evidence_contract() -> None:
    text = self_route_text()

    assert "candidate_evidence_status = $candidateEvidenceStatus" in text
    assert "candidate_evidence = $candidateEvidenceResult" in text
    assert "candidate_packets = @($candidatePackets)" in text
    assert "candidate_noise_paths = @($candidateNoisePaths)" in text
    assert "candidate_archive_paths = @($candidateArchivePaths)" in text
    assert "candidate_default_used = $candidateDefaultUsed" in text


def test_self_route_references_completed_packet_memory() -> None:
    text = self_route_text()

    assert "automation/orchestration/aios_completed_packet_memory.py" in text
    assert "-ScriptPath $completedPacketMemoryPath" in text
    assert '-ArgumentName "--evidence"' in text
    assert "-JsonPayload $completedPacketMemoryEvidenceJson" in text


def test_self_route_json_includes_completed_packet_memory_contract() -> None:
    text = self_route_text()

    assert "completed_packet_memory_status = $completedPacketMemoryStatus" in text
    assert "completed_packet_memory = $completedPacketMemory" in text
    assert "active_candidate_packets = @($activeCandidatePackets)" in text
    assert "suppressed_candidate_packets = @($suppressedCandidatePackets)" in text
    assert "suppressed_packet_ids = @($suppressedPacketIds)" in text
    assert "next_candidate_available = $nextCandidateAvailable" in text
    assert "next_candidate = $nextCandidate" in text
    assert "completed_memory_next_safe_action = $completedMemoryNextSafeAction" in text


def test_self_route_completed_memory_failure_becomes_safe_blocked_evidence() -> None:
    text = self_route_text()

    assert "New-AiOsCompletedPacketMemoryFallbackResult" in text
    assert "completed_packet_memory_missing" in text
    assert "completed_packet_memory_nonzero_exit" in text
    assert "completed_packet_memory_empty_output" in text
    assert "completed_packet_memory_generation_failed" in text
    assert '$rejectionReasons += "completed_packet_memory_blocked:$completedPacketMemoryBlocker"' in text


def test_self_route_all_suppressed_candidates_remain_no_packet_report_only() -> None:
    text = self_route_text()

    assert "$activeCandidatePackets = @(Get-AiOsObjectProperty -Object $completedPacketMemory -Name \"active_candidates\" -Default @())" in text
    assert "$nextCandidateAvailable = [bool](Get-AiOsObjectProperty -Object $completedPacketMemory -Name \"next_candidate_available\" -Default $false)" in text
    assert "$packetQueueCandidateEvidenceJson = ConvertTo-Json -InputObject @($plannerCandidatePackets) -Depth 30 -Compress" in text
    assert '$nextSafeAction = if ($forexRoadmapUsed -and -not [string]::IsNullOrWhiteSpace($executorNextSafeAction))' in text
    assert "$completedMemoryNextSafeAction" in text
    assert "selected_packet = $selectedPacket" in text
    assert "codex_ready_packet_preview = $codexReadyPacketPreview" in text


def test_self_route_references_forex_builder_roadmap() -> None:
    text = self_route_text()

    assert "automation/orchestration/aios_forex_builder_roadmap.py" in text
    assert "-ScriptPath $forexBuilderRoadmapPath" in text
    assert '-ArgumentName "--evidence"' in text
    assert "-JsonPayload $forexRoadmapEvidenceJson" in text


def test_self_route_json_includes_forex_roadmap_contract() -> None:
    text = self_route_text()

    assert "forex_roadmap_status = $forexRoadmapStatus" in text
    assert "forex_roadmap = $forexRoadmap" in text
    assert "forex_roadmap_candidates = @($forexRoadmapCandidates)" in text
    assert "forex_roadmap_next_candidate = $forexRoadmapNextCandidate" in text
    assert "forex_roadmap_forbidden_lanes = @($forexRoadmapForbiddenLanes)" in text
    assert "forex_roadmap_used = $forexRoadmapUsed" in text


def test_self_route_uses_forex_roadmap_when_active_candidates_are_empty() -> None:
    text = self_route_text()

    assert "$forexRoadmapNeeded = @($activeCandidatePackets).Count -eq 0" in text
    assert 'if ($forexRoadmapNeeded) {' in text
    assert '$forexRoadmapUsed = $forexRoadmapNeeded -and $forexRoadmapStatus -eq "ready" -and @($forexRoadmapCandidates).Count -gt 0' in text
    assert "$plannerCandidatePackets = if ($forexRoadmapUsed) { @($forexRoadmapCandidates) } else { @($activeCandidatePackets) }" in text


def test_self_route_packet_planner_receives_forex_roadmap_candidates() -> None:
    text = self_route_text()

    assert "$forexRoadmapCandidates = @(Get-AiOsObjectProperty -Object $forexRoadmap -Name \"roadmap_candidates\" -Default @())" in text
    assert "$packetQueueCandidateEvidenceJson = ConvertTo-Json -InputObject @($plannerCandidatePackets) -Depth 30 -Compress" in text
    assert "-ScriptPath $packetQueuePlannerPath" in text
    assert '-ArgumentName "--candidates"' in text
    assert "-JsonPayload $packetQueueCandidateEvidenceJson" in text


def test_self_route_forex_roadmap_failure_becomes_safe_blocked_evidence() -> None:
    text = self_route_text()

    assert "New-AiOsForexRoadmapFallbackResult" in text
    assert "forex_builder_roadmap_missing" in text
    assert "forex_builder_roadmap_nonzero_exit" in text
    assert "forex_builder_roadmap_empty_output" in text
    assert "forex_builder_roadmap_generation_failed" in text
    assert '$rejectionReasons += "forex_builder_roadmap_blocked:$forexRoadmapBlocker"' in text


def test_self_route_forex_roadmap_default_candidate_contract_is_canonical_spec() -> None:
    text = self_route_text()
    roadmap = forex_roadmap_text()

    assert "$forexRoadmapNextCandidate = Get-AiOsObjectProperty -Object $forexRoadmap -Name \"next_recommended_candidate\" -Default $null" in text
    assert "PKT-AIOS-FOREX-BUILDER-CANONICAL-SPEC" in roadmap
    assert '"forex-builder-spec"' in roadmap


def test_self_route_forex_candidate_propagates_to_executor_ledger_and_dashboard() -> None:
    text = self_route_text()

    assert "selected_packet = $selectedPacket" in text
    assert "codex_ready_packet_preview = $codexReadyPacketPreview" in text
    assert "approved_executor_status = $approvedExecutorStatus" in text
    assert "execution_allowed = $executionAllowed" in text
    assert "cycle_ledger = $cycleLedger" in text
    assert "dashboard_contract = $dashboardContract" in text
    assert "current_packet = [string](Get-AiOsObjectProperty -Object $SelectedPacket -Name \"packet_id\" -Default \"\")" in text


def test_self_route_forex_forbidden_lanes_cover_protected_boundaries() -> None:
    text = self_route_text()
    roadmap = forex_roadmap_text()

    assert "forex_roadmap_forbidden_lanes = @($forexRoadmapForbiddenLanes)" in text
    forbidden_text = roadmap.lower()
    for term in ("broker", "live", "orders", "secrets", "webhooks", "scheduler", "daemon"):
        assert term in forbidden_text


def test_self_route_does_not_select_broker_live_secret_order_or_webhook_forex_candidate() -> None:
    roadmap = forex_roadmap_text()

    assert "broker_allowed\": False" in roadmap
    assert "live_trading_allowed\": False" in roadmap
    assert "credentials_allowed\": False" in roadmap
    assert "orders_allowed\": False" in roadmap
    assert "webhooks_allowed\": False" in roadmap


def test_self_route_generated_archive_paths_are_not_planner_candidate_packets() -> None:
    text = self_route_text()

    assert "candidate_packets = @($candidatePackets)" in text
    assert "$activeCandidatePackets = @(Get-AiOsObjectProperty -Object $completedPacketMemory -Name \"active_candidates\" -Default @())" in text
    assert "$packetQueueCandidateEvidenceJson = ConvertTo-Json -InputObject @($plannerCandidatePackets) -Depth 30 -Compress" in text
    assert '-ArgumentName "--candidates"' in text
    assert "-JsonPayload $packetQueueCandidateEvidenceJson" in text
    assert "Reports/" not in text
    assert "control/review_bridge/" not in text
    assert "automation/orchestration/work_packets/preview/" not in text


def test_self_route_no_promoted_candidate_uses_default_safe_candidate_evidence() -> None:
    text = self_route_text()

    assert 'default_candidate_packet_id = "PKT-AIOS-SELFROUTE-CANDIDATE-EVIDENCE-INTEGRATION"' in text
    assert "$candidateDefaultUsed = [bool](Get-AiOsObjectProperty -Object $candidateEvidenceResult -Name \"default_candidate_used\" -Default $false)" in text
    assert "candidate_default_used = $candidateDefaultUsed" in text


def test_self_route_packet_queue_planner_receives_completed_memory_active_candidates() -> None:
    text = self_route_text()

    assert "$candidatePackets = @(Get-AiOsObjectProperty -Object $candidateEvidenceResult -Name \"candidate_packets\" -Default @())" in text
    assert "candidate_packets = @($candidatePackets)" in text
    assert "$activeCandidatePackets = @(Get-AiOsObjectProperty -Object $completedPacketMemory -Name \"active_candidates\" -Default @())" in text
    assert "$packetQueueCandidateEvidenceJson = ConvertTo-Json -InputObject @($plannerCandidatePackets) -Depth 30 -Compress" in text
    assert "-ScriptPath $packetQueuePlannerPath" in text
    assert '-ArgumentName "--candidates"' in text
    assert "-JsonPayload $packetQueueCandidateEvidenceJson" in text


def test_self_route_json_includes_packet_queue_plan_contract() -> None:
    text = self_route_text()

    assert "packet_queue_plan_status = $packetQueuePlanStatus" in text
    assert "packet_queue_plan = $packetQueuePlan" in text
    assert "codex_ready_packet_preview = $codexReadyPacketPreview" in text
    assert "selected_packet = $selectedPacket" in text
    assert "packet_queue_next_safe_action = $packetQueueNextSafeAction" in text


def test_self_route_packet_queue_side_effect_fields_are_reported() -> None:
    text = self_route_text()

    assert "packet_queue_commands_executed = @($packetQueueCommandsExecuted)" in text
    assert "packet_queue_workers_dispatched = $packetQueueWorkersDispatched" in text
    assert "packet_queue_queues_mutated = $packetQueueQueuesMutated" in text
    assert "packet_queue_approvals_mutated = $packetQueueApprovalsMutated" in text
    assert "packet_queue_files_written = @($packetQueueFilesWritten)" in text


def test_self_route_does_not_execute_packet_queue_preview_text() -> None:
    text = self_route_text()

    assert "Invoke-Expression" not in text
    assert "Start-Process" not in text
    assert "$packetQueueCommandsExecuted = @()" in text
    assert "command_execution_allowed = $false" in text
    assert "command_executed = $false" in text


def test_self_route_does_not_dispatch_or_mutate_packet_queue_state() -> None:
    text = self_route_text()

    assert "$packetQueueWorkersDispatched = $false" in text
    assert "$packetQueueQueuesMutated = $false" in text
    assert "$packetQueueApprovalsMutated = $false" in text
    assert "$packetQueueFilesWritten = @()" in text
    assert "worker_dispatch = $false" in text
    assert "queue_mutation = $false" in text
    assert "approval_mutation = $false" in text
    assert "reports_written = $false" in text
    assert "Reports/" not in text


def test_self_route_empty_packet_candidate_evidence_is_safe() -> None:
    text = self_route_text()

    assert '$packetQueueCandidateEvidenceJson = "[]"' in text
    assert 'QueueStatus "empty"' in text
    assert 'Reason "packet_queue_candidate_evidence_missing"' in text
    assert "Add candidate packet evidence before planning queue selection." in text


def test_self_route_packet_queue_selected_preview_is_stop_report_only() -> None:
    text = self_route_text()

    assert "selected_packet = $selectedPacket" in text
    assert "codex_ready_packet_preview = $codexReadyPacketPreview" in text
    assert 'default_candidate_packet_id = "PKT-AIOS-SELFROUTE-CANDIDATE-EVIDENCE-INTEGRATION"' in text
    assert "REPORT_ONLY_NO_RECOMMENDED_COMMAND_EXECUTION" in text
    assert "No staging. No commit. No push." not in text
    assert "launch_codex" in text


def test_self_route_completed_memory_suppresses_default_candidate_before_planning() -> None:
    text = self_route_text()

    assert '"PKT-AIOS-SELFROUTE-CANDIDATE-EVIDENCE-INTEGRATION"' in text
    assert "$completedPacketMemoryPath = \"automation/orchestration/aios_completed_packet_memory.py\"" in text
    assert "$completedPacketMemoryOutput = Invoke-AiOsPythonJsonArgumentScript" in text
    assert "-ScriptPath $completedPacketMemoryPath" in text
    assert "$suppressedPacketIds = @(" in text
    assert "suppressed_packet_ids = @($suppressedPacketIds)" in text
    assert "$packetQueueCandidateEvidenceJson = ConvertTo-Json -InputObject @($plannerCandidatePackets) -Depth 30 -Compress" in text


def test_self_route_references_approved_packet_executor_contract() -> None:
    text = self_route_text()

    assert "automation/orchestration/aios_approved_packet_executor_contract.py" in text
    assert "-ScriptPath $approvedExecutorContractPath" in text
    assert '-ArgumentName "--evidence"' in text
    assert "-JsonPayload $approvedExecutorEvidenceJson" in text


def test_self_route_json_includes_approved_executor_contract_fields() -> None:
    text = self_route_text()

    assert "approved_executor_status = $approvedExecutorStatus" in text
    assert "approved_executor_contract = $approvedExecutorContract" in text
    assert "execution_allowed = $executionAllowed" in text
    assert "command_preview_allowed = $commandPreviewAllowed" in text
    assert "codex_launch_allowed = $codexLaunchAllowed" in text
    assert "approval_required = $executorApprovalRequired" in text
    assert "approval_status = $executorApprovalStatus" in text
    assert "approval_source = $executorApprovalSource" in text
    assert "protected_action_required = $protectedActionRequired" in text
    assert "allowed_execution_mode = $allowedExecutionMode" in text
    assert "executor_next_safe_action = $executorNextSafeAction" in text


def test_self_route_passes_selected_packet_to_approved_executor_contract() -> None:
    text = self_route_text()

    assert "$approvedExecutorEvidence = [ordered]@{" in text
    assert "selected_packet = $selectedPacket" in text
    assert "codex_ready_packet_preview = $codexReadyPacketPreview" in text
    assert "approval_evidence = @()" in text


def test_self_route_missing_executor_approval_blocks_execution_by_default() -> None:
    text = self_route_text()

    assert "approval_evidence = @()" in text
    assert "$executorApprovalStatus = [string](Get-AiOsObjectProperty -Object $approvedExecutorContract -Name \"approval_status\" -Default \"\")" in text
    assert "executor_blocked_reasons = @($executorBlockedReasons)" in text


def test_self_route_executor_execution_and_codex_launch_are_false_by_default() -> None:
    text = self_route_text()

    assert "$executionAllowed = $false" in text
    assert "$codexLaunchAllowed = $false" in text
    assert "execution_allowed = $executionAllowed" in text
    assert "codex_launch_allowed = $codexLaunchAllowed" in text


def test_self_route_executor_approval_required_and_blocked_reasons_are_exposed() -> None:
    text = self_route_text()

    assert "approval_required = $true" in text
    assert "$executorApprovalRequired = [bool](Get-AiOsObjectProperty -Object $approvedExecutorContract -Name \"approval_required\" -Default $false)" in text
    assert "$executorBlockedReasons = @(Get-AiOsObjectProperty -Object $approvedExecutorContract -Name \"blocked_reasons\" -Default @())" in text
    assert "$executorRejectedReasons = @(Get-AiOsObjectProperty -Object $approvedExecutorContract -Name \"rejected_reasons\" -Default @())" in text
    assert "executor_blocked_reasons = @($executorBlockedReasons)" in text
    assert "executor_rejected_reasons = @($executorRejectedReasons)" in text


def test_self_route_executor_command_preview_remains_report_only() -> None:
    text = self_route_text()

    assert "command_preview_allowed = $commandPreviewAllowed" in text
    assert "REPORT_ONLY_NO_RECOMMENDED_COMMAND_EXECUTION" in text
    assert "Command executed: NO" in text


def test_self_route_executor_does_not_launch_codex_or_execute_commands() -> None:
    text = self_route_text()

    assert "Invoke-Expression" not in text
    assert "Start-Process" not in text
    assert "$codexLaunchAllowed = $false" in text
    assert "command_execution = $false" in text
    assert "codex_launch = $false" in text


def test_self_route_executor_does_not_dispatch_mutate_reports_or_touch_trading_boundaries() -> None:
    text = self_route_text()

    assert "worker_dispatch = $false" in text
    assert "queue_mutation = $false" in text
    assert "approval_mutation = $false" in text
    assert "reports_written = $false" in text
    assert "broker = $false" in text
    assert "live_trading = $false" in text
    assert "credentials = $false" in text
    assert "real_orders = $false" in text
    assert "real_webhooks = $false" in text
    assert "Reports/" not in text


def test_self_route_references_cycle_ledger_module() -> None:
    text = self_route_text()

    assert "automation/orchestration/aios_cycle_ledger.py" in text
    assert "-ScriptPath $cycleLedgerPath" in text
    assert '-ArgumentName "--evidence"' in text
    assert "-JsonPayload $cycleEvidenceJson" in text


def test_self_route_json_includes_cycle_ledger_dashboard_and_sos_contract() -> None:
    text = self_route_text()

    assert "cycle_ledger_status = $cycleLedgerStatus" in text
    assert "cycle_ledger = $cycleLedger" in text
    assert "dashboard_contract = $dashboardContract" in text
    assert "dashboard_status = $dashboardStatus" in text
    assert "sos_required = $sosRequired" in text
    assert "sos_reason = $sosReason" in text
    assert "forex_builder_alignment = $forexBuilderAlignment" in text
    assert "cycle_next_safe_action = $cycleNextSafeAction" in text


def test_self_route_passes_selected_packet_and_preview_to_cycle_ledger_evidence() -> None:
    text = self_route_text()

    assert "$cycleEvidence = [ordered]@{" in text
    assert "packet_queue_plan = $packetQueuePlan" in text
    assert "selected_packet = $selectedPacket" in text
    assert "codex_ready_packet_preview = $codexReadyPacketPreview" in text
    assert 'codex_prompt_emitted = [bool](Get-AiOsObjectProperty -Object $codexReadyPacketPreview -Name "packet_ready" -Default $false)' in text


def test_self_route_report_only_recommendation_approval_does_not_become_cycle_sos_gate() -> None:
    text = self_route_text()

    assert "source_recommendation_approval_required = $approvalRequired" in text
    assert "approval_required = [ordered]@{\n        human_owner_review = $false\n    }" in text
    assert '$rejectionReasons += "human_owner_review_required"' not in text


def test_self_route_cycle_ledger_and_dashboard_receive_selected_candidate_evidence() -> None:
    text = self_route_text()

    assert "selected_packet = $selectedPacket" in text
    assert "codex_ready_packet_preview = $codexReadyPacketPreview" in text
    assert "cycle_ledger = $cycleLedger" in text
    assert "dashboard_contract = $dashboardContract" in text
    assert "current_packet = [string](Get-AiOsObjectProperty -Object $SelectedPacket -Name \"packet_id\" -Default \"\")" in text


def test_self_route_cycle_ledger_evidence_includes_today_goal_alignment() -> None:
    text = self_route_text()

    assert "AIOS self-building machine; first proof target: industrial-grade forex bot builder" in text
    assert "no broker/live/secrets until gates prove safety" in text
    assert "forex_builder_alignment = $forexBuilderAlignment" in text


def test_self_route_does_not_execute_cycle_ledger_or_dashboard_output() -> None:
    text = self_route_text()

    assert "Invoke-Expression" not in text
    assert "Start-Process" not in text
    assert "command_execution_allowed = $false" in text
    assert "command_executed = $false" in text
    assert "codex_prompt_text |" not in text


def test_self_route_cycle_ledger_does_not_write_reports_or_mutate_state() -> None:
    text = self_route_text()

    assert "Reports/" not in text
    assert "reports_written = $false" in text
    assert "workers_dispatched = $false" in text
    assert "queues_mutated = $false" in text
    assert "approvals_mutated = $false" in text
    assert "worker_dispatch = $false" in text
    assert "queue_mutation = $false" in text
    assert "approval_mutation = $false" in text


def test_self_route_cycle_ledger_failure_becomes_safe_blocked_evidence() -> None:
    text = self_route_text()

    assert "New-AiOsBlockedCycleLedgerResult" in text
    assert "cycle_ledger_module_missing" in text
    assert "cycle_ledger_nonzero_exit" in text
    assert "cycle_ledger_empty_output" in text
    assert "cycle_ledger_generation_failed" in text
    assert '$rejectionReasons += "cycle_ledger_blocked:$cycleLedgerBlocker"' in text


def test_self_route_candidate_adapter_failure_becomes_safe_blocked_evidence() -> None:
    text = self_route_text()

    assert "New-AiOsCandidateEvidenceFallbackResult" in text
    assert "candidate_evidence_adapter_missing" in text
    assert "candidate_evidence_adapter_nonzero_exit" in text
    assert "candidate_evidence_adapter_empty_output" in text
    assert "candidate_evidence_adapter_generation_failed" in text
    assert '$rejectionReasons += "candidate_evidence_blocked:$candidateEvidenceBlocker"' in text


def test_self_route_empty_no_candidate_state_remains_safe_and_reportable() -> None:
    text = self_route_text()

    assert '$packetQueueCandidateEvidenceJson = "[]"' in text
    assert 'elseif ($packetQueuePlanStatus -eq "empty") {' in text
    assert '"packet_queue_plan_empty"' in text
    assert "No recommended command validation was needed." in text
    assert "Stop or idle according to the action recommendation; no command is executable from self-route." in text


def test_self_route_sos_blocks_but_remains_report_only() -> None:
    text = self_route_text()

    assert "if ($sosRequired) {" in text
    assert '$rejectionReasons += "cycle_ledger_sos_required:$sosReason"' in text
    assert "$exitCode = 1" in text
    assert "REPORT_ONLY_NO_RECOMMENDED_COMMAND_EXECUTION" in text


def test_self_route_references_operator_checkpoint_dashboard() -> None:
    text = self_route_text()

    assert "automation/orchestration/aios_operator_checkpoint_dashboard.py" in text
    assert "$operatorCheckpointDashboardPath" in text
    assert "-ScriptPath $operatorCheckpointDashboardPath" in text
    assert '-ArgumentName "--report"' in text
    assert "-JsonPayload $operatorCheckpointInputJson" in text


def test_self_route_json_includes_operator_checkpoint_contract() -> None:
    text = self_route_text()

    assert "operator_checkpoint_status" in text
    assert "operator_checkpoint_panel" in text
    assert "operator_checkpoint_lines" in text
    assert "bored_queue_status" in text
    assert "bored_queue_candidates" in text
    assert "compact_dashboard_status" in text


def test_self_route_default_human_output_is_compact_operator_panel() -> None:
    text = self_route_text()

    assert "AIOS STATUS" in text
    assert "Packet:" in text
    assert "State:" in text
    assert "Next:" in text
    assert "foreach ($line in $operatorCheckpointLines)" in text
    assert "if ($Detailed) {" in text
    assert "Recommended command:" in text


def test_self_route_default_output_does_not_dump_raw_json() -> None:
    text = self_route_text()

    assert "if ($QuietJson -or $OutputJson)" in text
    assert "$report | ConvertTo-Json -Depth 20" in text
    assert "foreach ($line in $operatorCheckpointLines)" in text
    assert "Write-Host ($report | ConvertTo-Json" not in text
    assert "$report | ConvertTo-Json -Depth 20 | Write-Host" not in text


def test_self_route_output_json_still_returns_full_json() -> None:
    text = self_route_text()

    assert "[switch]$OutputJson" in text
    assert "if ($QuietJson -or $OutputJson) {" in text
    assert "$report | ConvertTo-Json -Depth 20" in text
    assert "operator_checkpoint_panel" in text
    assert "cycle_ledger = $cycleLedger" in text
    assert "dashboard_contract = $dashboardContract" in text


def test_self_route_operator_checkpoint_preserves_safety_fields() -> None:
    text = self_route_text()

    assert "broker = $false" in text
    assert "live_trading = $false" in text
    assert "credentials = $false" in text
    assert "real_orders = $false" in text
    assert "real_webhooks = $false" in text
    assert "workers_dispatched = $false" in text
    assert "queues_mutated = $false" in text
    assert "approvals_mutated = $false" in text
    assert "reports_written = $false" in text
    assert "git_add = $false" in text
    assert "git_commit = $false" in text
    assert "git_push = $false" in text


def test_supervisor_does_not_advance_packets_after_self_route_failure() -> None:
    text = supervisor_text()

    assert (
        "    if ($LASTEXITCODE -ne 0) {\n"
        "        $cycleResult = \"FAIL\"\n"
        "        $blocker = \"self route failed\"\n"
        "        Write-AiOsSupervisorCycleAuditLog `\n"
    ) in text
    assert (
        "        Write-Host \"Runtime halted due to self-route blocker.\"\n"
        "        continue\n"
        "    }\n\n"
        "    if ($Apply) {\n"
        "        powershell -ExecutionPolicy Bypass -File "
        "automation/orchestration/runtime/Invoke-AiOsRuntimePacketAdvancement.ps1 -Apply"
    ) in text


def test_static_test_does_not_execute_supervisor() -> None:
    text = Path(__file__).read_text(encoding="utf-8")

    forbidden_execution_terms = (
        "check" + "_call",
        "check" + "_output",
        "Po" + "pen",
        "run" + "([",
    )
    for term in forbidden_execution_terms:
        assert term not in text
    assert "Start-AiOsPersistentRuntimeSupervisor.ps1" in text
