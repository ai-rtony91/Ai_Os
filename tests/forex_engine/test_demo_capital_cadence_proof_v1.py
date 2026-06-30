from __future__ import annotations

from pathlib import Path
import re

from automation.forex_engine.demo_capital_cadence_proof_v1 import (
    ACTION_COMPOUND_IN_ACCOUNT,
    ACTION_OWNER_REVIEW_PROFIT_SWEEP,
    ACTION_NO_TRANSFER,
    DEMO_CAPITAL_CADENCE_SCENARIO_COUNT,
    DEMO_CAPITAL_CADENCE_INCOMPLETE_INPUTS,
    DEMO_CAPITAL_CADENCE_PROOF_FAILED,
    DEMO_CAPITAL_CADENCE_PROOF_PASSED,
    DEMO_SCENARIO_ID_APPROVAL_TOKEN_MISMATCH_BLOCKED,
    DEMO_SCENARIO_ID_BROKER_POLICY_MISSING_BLOCKED,
    DEMO_SCENARIO_ID_COMPOUND_ELIGIBLE,
    DEMO_SCENARIO_ID_DAILY_LOSS_STOP_BLOCKED,
    DEMO_SCENARIO_ID_DEPOSIT_COOLDOWN_BLOCKED,
    DEMO_SCENARIO_ID_DEPOSIT_CADENCE_EXHAUSTED,
    DEMO_SCENARIO_ID_DRAWDOWN_BLOCKED,
    DEMO_SCENARIO_ID_EXACT_VOICE_TOKEN_ACCEPTED,
    DEMO_SCENARIO_ID_BUCKET_PURGE_ELIGIBLE,
    DEMO_SCENARIO_ID_BELOW_THRESHOLD_NO_TRANSFER,
    DEMO_SCENARIO_ID_GENERIC_VOICE_YES_BLOCKED,
    DEMO_SCENARIO_ID_KILL_SWITCH_BLOCKED,
    DEMO_SCENARIO_ID_LIVE_REVIEW_WITH_DEMO_PROOF_READY,
    DEMO_SCENARIO_ID_LIVE_REVIEW_WITHOUT_DEMO_PROOF_BLOCKED,
    DEMO_SCENARIO_ID_MARGIN_USED_BLOCKED,
    DEMO_SCENARIO_ID_OPEN_POSITION_BLOCKED,
    DEMO_SCENARIO_ID_PENDING_SETTLEMENT_BLOCKED,
    DEMO_SCENARIO_ID_PROFIT_SWEEP_ELIGIBLE,
    DEMO_SCENARIO_ID_TERMS_NOT_ACKNOWLEDGED_BLOCKED,
    DEMO_SCENARIO_ID_WITHDRAWAL_COOLDOWN_BLOCKED,
    DEMO_SCENARIO_ID_WITHDRAWAL_CADENCE_EXHAUSTED,
    DEMO_SCENARIO_ID_DEPOSIT_TOP_UP_OWNER_REVIEW,
    DEMO_CAPITAL_CADENCE_PROOF_PASSED,
    DEMO_CAPITAL_CADENCE_INCOMPLETE_INPUTS,
    DEMO_CAPITAL_CADENCE_SCENARIO_COUNT,
    DEMO_CAPITAL_CADENCE_PROOF_FAILED,
    REQUIRED_SCENARIO_OUTCOMES,
    REQUIRED_OWNER_ACTION_IDS,
    NEXT_PACKET_FAIL,
    NEXT_PACKET_PASS,
    BLOCKED_BY_SCENARIO_MISMATCH,
    STATUS_BLOCKED_BY_APPROVAL_TOKEN,
    STATUS_BLOCKED_BY_COMPLIANCE_EVIDENCE,
    STATUS_BLOCKED_BY_DEMO_PROOF,
    STATUS_BLOCKED_BY_DRAWDOWN_OR_DAILY_LOSS,
    STATUS_BLOCKED_BY_OPEN_RISK,
    STATUS_BLOCKED_BY_PROFIT_THRESHOLD,
    STATUS_BLOCKED_BY_TRANSFER_CADENCE,
    STATUS_CAPITAL_ACTION_READY_FOR_OWNER_REVIEW,
    STATUS_READY_FOR_LIVE_CAPITAL_EXCEPTION_REVIEW,
    run_demo_capital_cadence_proof_v1,
)


REQUIRED_SCENARIOS = (
    DEMO_SCENARIO_ID_COMPOUND_ELIGIBLE,
    DEMO_SCENARIO_ID_PROFIT_SWEEP_ELIGIBLE,
    DEMO_SCENARIO_ID_DEPOSIT_TOP_UP_OWNER_REVIEW,
    DEMO_SCENARIO_ID_BUCKET_PURGE_ELIGIBLE,
    DEMO_SCENARIO_ID_BELOW_THRESHOLD_NO_TRANSFER,
    DEMO_SCENARIO_ID_WITHDRAWAL_CADENCE_EXHAUSTED,
    DEMO_SCENARIO_ID_DEPOSIT_CADENCE_EXHAUSTED,
    DEMO_SCENARIO_ID_WITHDRAWAL_COOLDOWN_BLOCKED,
    DEMO_SCENARIO_ID_DEPOSIT_COOLDOWN_BLOCKED,
    DEMO_SCENARIO_ID_OPEN_POSITION_BLOCKED,
    DEMO_SCENARIO_ID_MARGIN_USED_BLOCKED,
    DEMO_SCENARIO_ID_PENDING_SETTLEMENT_BLOCKED,
    DEMO_SCENARIO_ID_DRAWDOWN_BLOCKED,
    DEMO_SCENARIO_ID_DAILY_LOSS_STOP_BLOCKED,
    DEMO_SCENARIO_ID_KILL_SWITCH_BLOCKED,
    DEMO_SCENARIO_ID_BROKER_POLICY_MISSING_BLOCKED,
    DEMO_SCENARIO_ID_TERMS_NOT_ACKNOWLEDGED_BLOCKED,
    DEMO_SCENARIO_ID_APPROVAL_TOKEN_MISMATCH_BLOCKED,
    DEMO_SCENARIO_ID_GENERIC_VOICE_YES_BLOCKED,
    DEMO_SCENARIO_ID_EXACT_VOICE_TOKEN_ACCEPTED,
    DEMO_SCENARIO_ID_LIVE_REVIEW_WITHOUT_DEMO_PROOF_BLOCKED,
    DEMO_SCENARIO_ID_LIVE_REVIEW_WITH_DEMO_PROOF_READY,
)


def test_default_run_returns_demo_proof_passed() -> None:
    result = run_demo_capital_cadence_proof_v1()
    assert result["demo_proof_status"] == DEMO_CAPITAL_CADENCE_PROOF_PASSED
    assert result["proof_passed"] is True
    assert result["read_only"] is True
    assert result["demo_only"] is True
    assert result["scenario_count"] >= 20
    assert result["scenario_count"] >= len(REQUIRED_SCENARIOS)
    assert result["next_best_packet"] == NEXT_PACKET_PASS


def test_required_scenario_ids_present() -> None:
    result = run_demo_capital_cadence_proof_v1()
    actual_ids = {entry["scenario_id"] for entry in result["scenario_results"]}
    for scenario_id in REQUIRED_SCENARIOS:
        assert scenario_id in actual_ids


def test_required_outcome_pairs_match_actuals() -> None:
    result = run_demo_capital_cadence_proof_v1()
    scenario_map = {entry["scenario_id"]: entry for entry in result["scenario_results"]}
    for scenario_id in REQUIRED_SCENARIOS:
        expected = REQUIRED_SCENARIO_OUTCOMES[scenario_id]
        actual = scenario_map[scenario_id]
        assert actual["expected_status"] == expected["expected_status"]
        assert actual["expected_action"] == expected["expected_action"]
        assert actual["actual_status"] == expected["expected_status"]
        assert actual["actual_action"] == expected["expected_action"]
        assert actual["passed"] is True


def test_hard_false_safety_flags_in_all_outputs() -> None:
    result = run_demo_capital_cadence_proof_v1()
    assert result["money_movement_allowed"] is False
    assert result["bank_access_allowed"] is False
    assert result["broker_api_allowed"] is False
    assert result["credential_storage_allowed"] is False
    assert result["credential_read_allowed"] is False
    assert result["live_capital_action_authorized"] is False
    for item in result["scenario_results"]:
        snapshot = item["safety_snapshot"]
        assert snapshot["money_movement_allowed"] is False
        assert snapshot["bank_access_allowed"] is False
        assert snapshot["broker_api_allowed"] is False
        assert snapshot["credential_storage_allowed"] is False
        assert snapshot["credential_read_allowed"] is False
        assert snapshot["live_capital_action_authorized"] is False


def test_sensitive_payload_is_blocked_and_not_quoted() -> None:
    result = run_demo_capital_cadence_proof_v1({"routing_number": "000111222"})
    assert result["demo_proof_status"] == "BLOCKED_BY_SENSITIVE_DATA"
    assert "000111222" not in str(result)


def test_live_exception_probe_does_not_authorize_live() -> None:
    result = run_demo_capital_cadence_proof_v1()
    probes = result["live_exception_probe"]
    assert probes[DEMO_SCENARIO_ID_LIVE_REVIEW_WITHOUT_DEMO_PROOF_BLOCKED]["actual_status"] == STATUS_BLOCKED_BY_DEMO_PROOF
    assert probes[DEMO_SCENARIO_ID_LIVE_REVIEW_WITH_DEMO_PROOF_READY]["actual_status"] == STATUS_READY_FOR_LIVE_CAPITAL_EXCEPTION_REVIEW
    for probe in probes.values():
        assert probe["safety_snapshot"]["live_capital_action_authorized"] is False


def test_generic_and_exact_voice_approval_behavior() -> None:
    result = run_demo_capital_cadence_proof_v1()
    scenario_map = {entry["scenario_id"]: entry for entry in result["scenario_results"]}
    assert scenario_map[DEMO_SCENARIO_ID_GENERIC_VOICE_YES_BLOCKED]["actual_status"] == STATUS_BLOCKED_BY_APPROVAL_TOKEN
    assert scenario_map[DEMO_SCENARIO_ID_EXACT_VOICE_TOKEN_ACCEPTED]["actual_status"] == STATUS_CAPITAL_ACTION_READY_FOR_OWNER_REVIEW
    assert scenario_map[DEMO_SCENARIO_ID_EXACT_VOICE_TOKEN_ACCEPTED]["actual_action"] == ACTION_OWNER_REVIEW_PROFIT_SWEEP


def test_status_and_action_distributions_cover_expected_blocks() -> None:
    result = run_demo_capital_cadence_proof_v1()
    failed_gate_distribution = result["failed_gate_distribution"]
    assert failed_gate_distribution["status:BLOCKED_BY_TRANSFER_CADENCE"] >= 4
    assert failed_gate_distribution["status:BLOCKED_BY_OPEN_RISK"] >= 3
    assert failed_gate_distribution["status:BLOCKED_BY_DRAWDOWN_OR_DAILY_LOSS"] >= 3
    assert failed_gate_distribution["status:BLOCKED_BY_APPROVAL_TOKEN"] >= 2
    assert failed_gate_distribution["status:BLOCKED_BY_COMPLIANCE_EVIDENCE"] == 1
    assert failed_gate_distribution["status:BLOCKED_BY_DEMO_PROOF"] == 1

    action_distribution = result["simulated_action_distribution"]
    assert action_distribution[ACTION_COMPOUND_IN_ACCOUNT] >= 1
    assert action_distribution[ACTION_OWNER_REVIEW_PROFIT_SWEEP] >= 5


def test_owner_action_queue_and_next_packet_shape() -> None:
    result = run_demo_capital_cadence_proof_v1()
    action_ids = {action["owner_action_id"] for action in result["owner_action_queue"]}
    for action_id in REQUIRED_OWNER_ACTION_IDS:
        assert action_id in action_ids
    for action in result["owner_action_queue"]:
        assert action["owner_decision_required"] is True
        assert action["money_movement_allowed"] is False
        assert action["live_capital_action_authorized"] is False
    assert result["next_best_packet"] == NEXT_PACKET_PASS


def test_expected_blocked_status_pairs() -> None:
    result = run_demo_capital_cadence_proof_v1()
    scenario_map = {entry["scenario_id"]: entry for entry in result["scenario_results"]}
    assert scenario_map[DEMO_SCENARIO_ID_WITHDRAWAL_CADENCE_EXHAUSTED]["actual_status"] == STATUS_BLOCKED_BY_TRANSFER_CADENCE
    assert scenario_map[DEMO_SCENARIO_ID_DEPOSIT_CADENCE_EXHAUSTED]["actual_status"] == STATUS_BLOCKED_BY_TRANSFER_CADENCE
    assert scenario_map[DEMO_SCENARIO_ID_WITHDRAWAL_COOLDOWN_BLOCKED]["actual_status"] == STATUS_BLOCKED_BY_TRANSFER_CADENCE
    assert scenario_map[DEMO_SCENARIO_ID_DEPOSIT_COOLDOWN_BLOCKED]["actual_status"] == STATUS_BLOCKED_BY_TRANSFER_CADENCE
    assert scenario_map[DEMO_SCENARIO_ID_OPEN_POSITION_BLOCKED]["actual_status"] == STATUS_BLOCKED_BY_OPEN_RISK
    assert scenario_map[DEMO_SCENARIO_ID_MARGIN_USED_BLOCKED]["actual_status"] == STATUS_BLOCKED_BY_OPEN_RISK
    assert scenario_map[DEMO_SCENARIO_ID_PENDING_SETTLEMENT_BLOCKED]["actual_status"] == STATUS_BLOCKED_BY_OPEN_RISK
    assert scenario_map[DEMO_SCENARIO_ID_DRAWDOWN_BLOCKED]["actual_status"] == STATUS_BLOCKED_BY_DRAWDOWN_OR_DAILY_LOSS
    assert scenario_map[DEMO_SCENARIO_ID_DAILY_LOSS_STOP_BLOCKED]["actual_status"] == STATUS_BLOCKED_BY_DRAWDOWN_OR_DAILY_LOSS
    assert scenario_map[DEMO_SCENARIO_ID_KILL_SWITCH_BLOCKED]["actual_status"] == STATUS_BLOCKED_BY_DRAWDOWN_OR_DAILY_LOSS
    assert scenario_map[DEMO_SCENARIO_ID_BELOW_THRESHOLD_NO_TRANSFER]["actual_status"] == STATUS_BLOCKED_BY_PROFIT_THRESHOLD


def test_mismatch_scenario_marks_failed() -> None:
    result = run_demo_capital_cadence_proof_v1(
        {
            "scenario_set": [
                {
                    "scenario_id": DEMO_SCENARIO_ID_COMPOUND_ELIGIBLE,
                    "payload": {"requested_action": ACTION_COMPOUND_IN_ACCOUNT},
                    "expected_status": "BROKEN_STATUS",
                    "expected_action": ACTION_COMPOUND_IN_ACCOUNT,
                },
            ],
        },
    )
    assert result["demo_proof_status"] == DEMO_CAPITAL_CADENCE_PROOF_FAILED
    assert result["proof_passed"] is False
    assert result["scenario_count"] == 1
    assert BLOCKED_BY_SCENARIO_MISMATCH in result["proof_blockers"]


def test_core_module_does_not_contain_forbidden_runtime_tokens() -> None:
    module_path = Path("automation/forex_engine/demo_capital_cadence_proof_v1.py")
    text = module_path.read_text(encoding="utf-8")
    for phrase in [
        "requests",
        "socket",
        "urllib",
        "subprocess",
        "os.environ",
        "broker_sdk",
        "schedule.every",
        "start-process",
    ]:
        assert phrase not in text


def test_core_module_has_no_direct_fund_transfer_exec_functions() -> None:
    module_path = Path("automation/forex_engine/demo_capital_cadence_proof_v1.py")
    text = module_path.read_text(encoding="utf-8")
    assert not re.search(r"^\\s*def\\s+(transfer|withdraw|deposit)_", text, flags=re.MULTILINE | re.IGNORECASE)


def test_forbidden_phrases_are_absent_from_packet_files() -> None:
    paths = [
        Path("automation/forex_engine/demo_capital_cadence_proof_v1.py"),
        Path("tests/forex_engine/test_demo_capital_cadence_proof_v1.py"),
        Path("docs/trading_lab/FOREX_DEMO_CAPITAL_CADENCE_PROOF_V1.md"),
        Path("Reports/forex_delivery/AIOS_FOREX_DEMO_CAPITAL_CADENCE_PROOF_V1_REPORT.md"),
    ]
    forbidden = tuple(
        "".join(parts)
        for parts in (
            ("100", "-", "120"),
            ("100", " ", "to", " ", "120"),
            ("120", "%", " return"),
            ("100", "%", " return"),
            ("guaranteed", " ", "return"),
            ("guaranteed", " ", "profit"),
            ("trade", " ", "now"),
            ("withdraw", " ", "now"),
            ("autonomous", " ", "withdrawal"),
            ("autonomous", " ", "deposit"),
            ("store", " ", "credentials"),
        )
    )
    for path in paths:
        text = path.read_text(encoding="utf-8")
        for phrase in forbidden:
            assert phrase not in text


def test_review_queue_contains_next_packet_action() -> None:
    result = run_demo_capital_cadence_proof_v1()
    action_ids = {entry["owner_action_id"] for entry in result["owner_action_queue"]}
    assert "REVIEW_NEXT_PACKET" in action_ids


def test_next_best_packet_for_failed_proof_is_self() -> None:
    result = run_demo_capital_cadence_proof_v1({"scenario_set": []})
    assert result["demo_proof_status"] == DEMO_CAPITAL_CADENCE_INCOMPLETE_INPUTS
    assert result["next_best_packet"] == NEXT_PACKET_FAIL
