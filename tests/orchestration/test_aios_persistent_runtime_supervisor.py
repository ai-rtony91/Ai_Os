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
    assert "--candidates $packetQueueCandidateEvidenceJson" in text


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
    assert "REPORT_ONLY_NO_RECOMMENDED_COMMAND_EXECUTION" in text
    assert "No staging. No commit. No push." not in text
    assert "launch_codex" in text


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
