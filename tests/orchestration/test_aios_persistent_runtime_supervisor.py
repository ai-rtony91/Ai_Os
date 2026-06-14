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
