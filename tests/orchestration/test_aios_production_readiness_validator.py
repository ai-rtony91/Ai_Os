from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = (
    REPO_ROOT
    / "automation"
    / "orchestration"
    / "validators"
    / "Test-AiOsProductionReadiness.DRY_RUN.ps1"
)


def validator_text() -> str:
    return VALIDATOR.read_text(encoding="utf-8").replace("\r\n", "\n")


def test_declares_dry_run_read_only_contract() -> None:
    text = validator_text()

    assert 'AIOS_PRODUCTION_READINESS_VALIDATOR.v1' in text
    assert 'DRY_RUN_READ_ONLY' in text
    assert '$schema' in text
    assert '$mode' in text


def test_emits_required_report_fields() -> None:
    text = validator_text()

    for field in (
        "verdict",
        "checks",
        "warnings",
        "blockers",
        "next_safe_action",
    ):
        assert re.search(rf"\b{re.escape(field)}\b", text)


def test_safety_flags_deny_mutation_and_execution() -> None:
    text = validator_text()

    for flag in (
        "writes_files",
        "mutates_runtime",
        "mutates_queue",
        "mutates_approval",
        "launches_workers",
        "starts_scheduler",
        "starts_daemon",
        "commits",
        "pushes",
        "broker_or_live_trading",
    ):
        assert flag in text

    assert "writes_files = $false" in text
    assert "mutates_runtime = $false" in text
    assert "mutates_queue = $false" in text
    assert "mutates_approval = $false" in text
    assert "launches_workers = $false" in text
    assert "starts_scheduler = $false" in text
    assert "starts_daemon = $false" in text
    assert "commits = $false" in text
    assert "pushes = $false" in text
    assert "broker_or_live_trading = $false" in text


def test_evidence_dirty_state_allowances_are_explicit() -> None:
    text = validator_text()

    assert '"Reports/"' in text
    assert '"control/review_bridge/"' in text
    assert "Dirty state is limited to evidence artifacts or this validator package." in text


def test_required_production_readiness_surfaces_are_checked() -> None:
    text = validator_text()

    for path in (
        "automation/orchestration/aios_active_mission_cycle.py",
        "automation/orchestration/aios_autonomy_decision_governor.py",
        "automation/orchestration/aios_closed_autonomy_loop.py",
        "automation/orchestration/aios_closed_loop_packet_drafter.py",
        "automation/orchestration/aios_closed_loop_queue_injection_preview.py",
        "automation/orchestration/aios_executive_control_readiness.py",
        "automation/orchestration/aios_queue_admission_gate.py",
        "automation/orchestration/aios_queue_to_dispatch_gates.py",
        "tests/services/runtimeVisibilityContract.test.js",
        "tests/services/appServiceBridge.test.js",
    ):
        assert path in text


def test_validator_does_not_contain_mutating_commands() -> None:
    text = validator_text().lower()

    forbidden_patterns = (
        r"\bgit\s+add\b",
        r"\bgit\s+commit\b",
        r"\bgit\s+push\b",
        r"\bgit\s+reset\b",
        r"\bgit\s+merge\b",
        r"\bstart-process\b",
        r"\bregister-scheduledtask\b",
        r"\bschtasks\b",
        r"\bnew-service\b",
        r"\bstart-service\b",
        r"\bset-content\b",
        r"\badd-content\b",
        r"\bout-file\b",
        r"\bremove-item\b",
        r"\bmove-item\b",
        r"\bcopy-item\b",
        r"\brename-item\b",
        r"\bstart-aiosworkerdeamon\b",
        r"\bstart-aiosworkerdaemon\b",
        r"\bstart-aiospersistentruntimesupervisor\b",
        r"\binvoke-aiosruntimepacketadvancement\b",
        r"\badd-aioscommandqueueitem\b",
        r"\badd-aiosworkerinboxitem\b",
        r"\bcomplete-aiosworkerinboxitem\b",
        r"\bset-aiosworkertaskstate\b",
        r"\binvoke-aiosworkersafeexecute\b",
        r"\bstart-aiosautonomousworkercycle\b",
        r"\binvoke-aiosapprovalprocessor\b",
        r"\binvoke-aiosapprovedactionresume\b",
    )

    for pattern in forbidden_patterns:
        assert re.search(pattern, text) is None, pattern


def test_static_test_does_not_execute_validator() -> None:
    text = Path(__file__).read_text(encoding="utf-8")

    forbidden_execution_terms = (
        "check" + "_call",
        "check" + "_output",
        "Po" + "pen",
        "run" + "([",
    )
    for term in forbidden_execution_terms:
        assert term not in text
