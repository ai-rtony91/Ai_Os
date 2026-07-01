from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.forex_completion_campaign_part2_v1 import (  # noqa: E402
    BLOCKED_BY_22H_6D_READINESS,
    BLOCKED_BY_BROKER_RUNTIME_EVIDENCE,
    BLOCKED_BY_DASHBOARD_OWNER_CONTROL,
    BLOCKED_BY_POST_EXECUTION_REVIEW_LOOP,
    BLOCKED_BY_PROFIT_PROOF,
    BLOCKED_BY_PROTECTED_RUNTIME_EXECUTION_GATE,
    BLOCKED_BY_RETURN_TARGET_EVIDENCE,
    BLOCKED_BY_RUNTIME_CREDENTIAL_SESSION_BRIDGE,
    BLOCKED_BY_SAFETY_REAL_MONEY_GATE,
    BLOCKED_BY_SENSITIVE_DATA,
    FOREX_COMPLETION_CAMPAIGN_PART2_CONTINUE_EVIDENCE_CAPTURE,
    FOREX_COMPLETION_CAMPAIGN_PART2_READY_FOR_100_PLUS_REVIEW,
    INCOMPLETE_INPUTS,
    evaluate_forex_completion_campaign_part2_v1,
)
from automation.forex_engine.live_execution_and_capital_operation_campaign_v1 import (  # noqa: E402
    evaluate_live_execution_and_capital_operation_campaign_v1,
)
from automation.forex_engine.oanda_demo_owner_approved_one_order_protected_runtime_execution_v1 import (  # noqa: E402
    HARD_FALSE_FIELDS,
)
from scripts.forex_delivery.run_forex_completion_campaign_part2_v1 import (  # noqa: E402
    main as runner_main,
    safe_sample_payload,
)


PRODUCTION_FILES = (
    ROOT
    / "automation"
    / "forex_engine"
    / "oanda_demo_owner_approved_one_order_protected_runtime_execution_v1.py",
    ROOT / "automation" / "forex_engine" / "owner_runtime_credential_session_bridge_v1.py",
    ROOT / "automation" / "forex_engine" / "forex_post_execution_review_loop_v1.py",
    ROOT / "automation" / "forex_engine" / "forex_22h6d_supervised_operation_readiness_v1.py",
    ROOT / "automation" / "forex_engine" / "forex_completion_campaign_part2_v1.py",
    ROOT / "scripts" / "forex_delivery" / "run_forex_completion_campaign_part2_v1.py",
)


def _payload() -> dict:
    return safe_sample_payload()


def _live_campaign_credential_bridge_payload() -> dict:
    return {
        "credential_session_boundary": {
            "owner_enters_credentials_outside_repo_chat": True,
            "runtime_only_credential_handoff": True,
            "no_stored_api_key": True,
            "no_stored_account_id": True,
            "no_master_password": True,
            "no_vault_password": True,
            "no_raw_token": True,
            "secret_scan_required": True,
            "redaction_required": True,
            "session_expiry_required": True,
            "session_unexpired": True,
            "one_order_session_scope": True,
            "credential_values_provided": False,
            "credential_values_persisted": False,
            "credential_values_logged": False,
            "credential_values_requested_by_aios": False,
            "repo_secret_storage_allowed": False,
            "chat_secret_sharing_allowed": False,
            "env_var_read_allowed": False,
            "account_id_provided": False,
            "bridge_ready_for_review": True,
        }
    }


def _run(payload: dict | None = None) -> dict:
    return evaluate_forex_completion_campaign_part2_v1(payload)


def test_empty_payload_incomplete() -> None:
    assert _run({})["campaign_status"] == INCOMPLETE_INPUTS


def test_sensitive_data_blocked_and_value_not_echoed() -> None:
    payload = _payload()
    payload["password"] = "DO-NOT-ECHO"
    result = _run(payload)
    assert result["campaign_status"] == BLOCKED_BY_SENSITIVE_DATA
    assert "DO-NOT-ECHO" not in repr(result)


def test_raw_password_api_key_token_fields_still_block() -> None:
    for key in ("password", "api_key", "token"):
        payload = _payload()
        payload[key] = "DO-NOT-ECHO"
        result = _run(payload)
        assert result["campaign_status"] == BLOCKED_BY_SENSITIVE_DATA
        assert "DO-NOT-ECHO" not in repr(result)


def test_generated_live_campaign_result_with_secret_session_text_is_allowed() -> None:
    generated = evaluate_live_execution_and_capital_operation_campaign_v1(
        _live_campaign_credential_bridge_payload()
    )
    assert "SECRET_SESSION" in generated["next_best_packet"]

    payload = _payload()
    payload["live_execution_and_capital_operation_campaign_result"] = generated
    result = _run(payload)

    assert result["campaign_status"] != BLOCKED_BY_SENSITIVE_DATA
    assert result["sensitive_data_detected"] is False
    assert result["capital_operation_summary"]["money_moved"] is False


def test_all_five_lanes_pass_and_score_reaches_100_or_above() -> None:
    result = _run(_payload())
    assert all(result["five_lane_summary"].values())
    assert result["completion_score"] >= 100


def test_full_post_100_package_reaches_110() -> None:
    result = _run(_payload())
    assert result["campaign_status"] == FOREX_COMPLETION_CAMPAIGN_PART2_READY_FOR_100_PLUS_REVIEW
    assert result["completion_score"] == 110


def test_profit_proof_missing_blocks() -> None:
    payload = _payload()
    payload["profit_proof_metadata"]["evidence_sample_count"] = 1
    assert _run(payload)["campaign_status"] == BLOCKED_BY_PROFIT_PROOF


def test_return_target_partial_routes_to_continue_evidence_capture() -> None:
    payload = _payload()
    payload["return_target_validation_metadata"]["target_evidence_status"] = "PARTIAL"
    payload["return_target_validation_metadata"]["evidence_supports_target_review"] = False
    result = _run(payload)
    assert result["campaign_status"] == FOREX_COMPLETION_CAMPAIGN_PART2_CONTINUE_EVIDENCE_CAPTURE
    assert result["return_target_validation_lane"]["status"] == "REVIEW_REQUIRED"


def test_guaranteed_profit_claimed_blocks_return_target_lane() -> None:
    payload = _payload()
    payload["return_target_validation_metadata"]["guaranteed_profit_claimed"] = True
    assert _run(payload)["campaign_status"] == BLOCKED_BY_RETURN_TARGET_EVIDENCE


def test_broker_runtime_missing_blocks() -> None:
    payload = _payload()
    payload["broker_runtime_evidence_metadata"]["one_order_protected_gate_present"] = False
    assert _run(payload)["campaign_status"] == BLOCKED_BY_BROKER_RUNTIME_EVIDENCE


def test_safety_real_money_gate_missing_blocks() -> None:
    payload = _payload()
    payload["safety_real_money_gate_metadata"]["kill_switch_ready"] = False
    assert _run(payload)["campaign_status"] == BLOCKED_BY_SAFETY_REAL_MONEY_GATE


def test_dashboard_truth_missing_blocks() -> None:
    payload = _payload()
    payload["dashboard_truth_owner_control_metadata"]["dashboard_truth_contract_present"] = False
    assert _run(payload)["campaign_status"] == BLOCKED_BY_DASHBOARD_OWNER_CONTROL


def test_protected_runtime_gate_missing_blocks() -> None:
    payload = _payload()
    payload["protected_runtime_execution_result"]["protected_runtime_status"] = "BLOCKED"
    assert _run(payload)["campaign_status"] == BLOCKED_BY_PROTECTED_RUNTIME_EXECUTION_GATE


def test_credential_session_bridge_missing_blocks() -> None:
    payload = _payload()
    payload["credential_session_bridge_result"]["credential_session_bridge_status"] = "BLOCKED"
    assert _run(payload)["campaign_status"] == BLOCKED_BY_RUNTIME_CREDENTIAL_SESSION_BRIDGE


def test_post_execution_loop_missing_blocks() -> None:
    payload = _payload()
    payload["post_execution_review_loop_result"]["post_execution_review_status"] = "BLOCKED"
    assert _run(payload)["campaign_status"] == BLOCKED_BY_POST_EXECUTION_REVIEW_LOOP


def test_22h_6d_readiness_missing_blocks() -> None:
    payload = _payload()
    payload["supervised_operation_readiness_result"]["total_score"] = 90
    assert _run(payload)["campaign_status"] == BLOCKED_BY_22H_6D_READINESS


def test_next_best_packet_routes_correctly() -> None:
    payload = _payload()
    payload["credential_session_bridge_result"]["credential_session_bridge_status"] = "BLOCKED"
    result = _run(payload)
    assert result["next_best_packet"] == "AIOS_FOREX_OWNER_RUNTIME_CREDENTIAL_SESSION_BRIDGE_V1"


def test_hard_false_fields_remain_false() -> None:
    result = _run(_payload())
    for field in HARD_FALSE_FIELDS:
        assert result[field] is False


def test_source_scan_confirms_production_modules_have_no_forbidden_runtime_markers() -> None:
    forbidden = [
        "re" + "quests",
        "so" + "cket",
        "ur" + "llib",
        "sub" + "process",
        "os." + "environ",
        "broker" + "_sdk",
        "schedule" + ".every",
        "start" + "-process",
    ]
    hits = {
        str(path): [marker for marker in forbidden if marker in path.read_text(encoding="utf-8").lower()]
        for path in PRODUCTION_FILES
    }
    assert not any(hits.values()), hits


def test_runner_script_returns_deterministic_json() -> None:
    first = io.StringIO()
    second = io.StringIO()
    with redirect_stdout(first):
        assert runner_main() == 0
    with redirect_stdout(second):
        assert runner_main() == 0
    left = json.loads(first.getvalue())
    right = json.loads(second.getvalue())
    assert left == right
    assert left["schema"] == "AIOS_FOREX_COMPLETION_CAMPAIGN_PART2_V1"
    assert left["campaign_status"]
