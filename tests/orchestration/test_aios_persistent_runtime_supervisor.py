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
