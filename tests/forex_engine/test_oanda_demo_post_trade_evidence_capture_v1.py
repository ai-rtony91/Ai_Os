from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.oanda_demo_post_trade_evidence_capture_v1 import (  # noqa: E402
    EVIDENCE_BLOCKED_BROKER_CALL_NOT_ATTEMPTED,
    EVIDENCE_BLOCKED_MISSING_BROKER_CALL_RESULT,
    EVIDENCE_BLOCKED_MISSING_OWNER_COMMAND,
    EVIDENCE_BLOCKED_MISSING_POST_TRADE_EVIDENCE,
    EVIDENCE_BLOCKED_OWNER_COMMAND_NOT_READY,
    EVIDENCE_BLOCKED_OWNER_CONFIRMATION,
    EVIDENCE_CAPTURE_READY,
    EVIDENCE_REJECTED,
    evaluate_oanda_demo_post_trade_evidence_capture_v1,
)
from scripts.forex_delivery.run_oanda_demo_post_trade_evidence_capture_v1 import (  # noqa: E402
    main as script_main,
)


EXECUTION_AUTHORITY_FALSE = {
    "execution_allowed": False,
    "demo_order_allowed": False,
    "live_order_allowed": False,
    "broker_write_allowed": False,
    "autonomous_order_allowed": False,
    "scheduler_allowed": False,
    "daemon_allowed": False,
    "webhook_allowed": False,
}


def owner_command_result(**overrides):
    result = {
        "status": "OWNER_COMMAND_READY_FOR_MANUAL_DEMO_ORDER_COMMAND",
        "execution_authority": EXECUTION_AUTHORITY_FALSE.copy(),
    }
    result.update(overrides)
    return result


def broker_call_result(**overrides):
    result = {
        "status": "BROKER_CALL_ATTEMPTED_DEMO_ORDER_ONCE",
        "order_attempt_count": 1,
        "live_order_allowed": False,
        "autonomous_order_allowed": False,
        "execution_authority": EXECUTION_AUTHORITY_FALSE.copy(),
    }
    result.update(overrides)
    return result


def dry_run_broker_call_result(**overrides):
    result = broker_call_result(
        status="BROKER_CALL_DRY_RUN_READY",
        order_attempt_count=0,
    )
    result.update(overrides)
    return result


def post_trade_evidence(**overrides):
    evidence = {
        "evidence_mode": "ORDER_CLOSED",
        "broker": "OANDA_DEMO",
        "environment": "DEMO",
        "order_attempted": True,
        "order_id_or_sanitized_reference": "ORDER-REF-001",
        "filled_or_rejected": "CLOSED",
        "fill_price_or_rejection_reason": "1.1000",
        "stop_loss_attached": True,
        "take_profit_attached": True,
        "realized_pl_when_closed": 1.25,
        "unrealized_pl_snapshot": None,
        "close_reason": "take_profit",
        "post_balance": 1001.25,
        "post_nav": 1001.25,
        "timestamp_utc": "2026-06-24T12:00:00Z",
        "one_order_only": True,
        "max_order_attempts": 1,
        "no_second_order": True,
        "hold_allowed_overnight": False,
        "credential_persistence_detected": False,
        "account_id_persistence_detected": False,
    }
    evidence.update(overrides)
    return evidence


def dry_run_evidence(**overrides):
    evidence = post_trade_evidence(
        evidence_mode="DRY_RUN_REHEARSAL",
        order_attempted=False,
        order_id_or_sanitized_reference="",
        filled_or_rejected="DRY_RUN",
        fill_price_or_rejection_reason="dry_run_rehearsal",
        stop_loss_attached=False,
        take_profit_attached=False,
        realized_pl_when_closed=None,
        close_reason=None,
        post_balance=None,
        post_nav=None,
    )
    evidence.update(overrides)
    return evidence


def owner_confirmation(**overrides):
    confirmation = {
        "owner_confirmed_post_trade_evidence_reviewed": True,
        "owner_confirmed_no_second_order": True,
        "owner_confirmed_no_credentials_in_evidence": True,
        "owner_confirmed_no_account_ids_in_evidence": True,
        "owner_confirmed_stop_loss_checked": True,
        "owner_confirmed_take_profit_checked": True,
        "owner_confirmed_pl_recorded": True,
    }
    confirmation.update(overrides)
    return confirmation


def evaluate(**overrides):
    payload = {
        "owner_command_result": owner_command_result(),
        "broker_call_result": broker_call_result(),
        "post_trade_evidence": post_trade_evidence(),
        "owner_evidence_confirmation": owner_confirmation(),
    }
    payload.update(overrides)
    return evaluate_oanda_demo_post_trade_evidence_capture_v1(**payload)


def run_script(args):
    stream = StringIO()
    with redirect_stdout(stream):
        code = script_main(args)
    return code, json.loads(stream.getvalue())


def assert_execution_authority_false(result):
    assert result["execution_authority"] == EXECUTION_AUTHORITY_FALSE


def test_default_blocks_missing_owner_command():
    result = evaluate_oanda_demo_post_trade_evidence_capture_v1()
    assert result["status"] == EVIDENCE_BLOCKED_MISSING_OWNER_COMMAND
    assert "missing_owner_command_result" in result["blockers"]
    assert_execution_authority_false(result)


def test_owner_command_not_ready_blocks():
    result = evaluate(
        owner_command_result=owner_command_result(status="OWNER_COMMAND_BLOCKED")
    )
    assert result["status"] == EVIDENCE_BLOCKED_OWNER_COMMAND_NOT_READY
    assert "owner_command_status_not_ready" in result["blockers"]


def test_missing_broker_call_result_blocks():
    result = evaluate(broker_call_result=None)
    assert result["status"] == EVIDENCE_BLOCKED_MISSING_BROKER_CALL_RESULT
    assert "missing_broker_call_result" in result["blockers"]


def test_broker_call_not_attempted_blocks():
    result = evaluate(
        broker_call_result=broker_call_result(
            status="BROKER_CALL_READY_BUT_TRANSPORT_REQUIRED"
        )
    )
    assert result["status"] == EVIDENCE_BLOCKED_BROKER_CALL_NOT_ATTEMPTED
    assert "broker_call_result_must_be_attempted_once_or_dry_run" in result[
        "blockers"
    ]


def test_missing_post_trade_evidence_blocks():
    result = evaluate(post_trade_evidence=None)
    assert result["status"] == EVIDENCE_BLOCKED_MISSING_POST_TRADE_EVIDENCE
    assert "missing_post_trade_evidence" in result["blockers"]


def test_missing_owner_evidence_confirmation_blocks():
    result = evaluate(owner_evidence_confirmation=None)
    assert result["status"] == EVIDENCE_BLOCKED_OWNER_CONFIRMATION
    assert "missing_owner_evidence_confirmation" in result["blockers"]


def test_token_account_key_in_broker_call_result_rejects():
    result = evaluate(broker_call_result=broker_call_result(token="demo_SECRET"))
    assert result["status"] == EVIDENCE_REJECTED
    assert "broker_call_forbidden_token_field" in result["blockers"]


def test_token_account_key_in_evidence_rejects():
    result = evaluate(post_trade_evidence=post_trade_evidence(account_id="ACC-123"))
    assert result["status"] == EVIDENCE_REJECTED
    assert "post_trade_evidence_forbidden_account_id_field" in result["blockers"]


def test_credential_persistence_rejects():
    result = evaluate(
        post_trade_evidence=post_trade_evidence(
            credential_persistence_detected=True
        )
    )
    assert result["status"] == EVIDENCE_REJECTED
    assert "post_trade_evidence_credential_persistence_detected" in result[
        "blockers"
    ]


def test_account_id_persistence_rejects():
    result = evaluate(
        post_trade_evidence=post_trade_evidence(
            account_id_persistence_detected=True
        )
    )
    assert result["status"] == EVIDENCE_REJECTED
    assert "post_trade_evidence_account_id_persistence_detected" in result[
        "blockers"
    ]


def test_missing_sanitized_order_reference_blocks_for_submitted_order():
    result = evaluate(
        post_trade_evidence=post_trade_evidence(
            evidence_mode="ORDER_SUBMITTED",
            order_id_or_sanitized_reference="",
            filled_or_rejected="SUBMITTED",
            realized_pl_when_closed=None,
            close_reason=None,
        )
    )
    assert result["status"] == EVIDENCE_BLOCKED_MISSING_POST_TRADE_EVIDENCE
    assert "post_trade_evidence_sanitized_order_reference_required" in result[
        "blockers"
    ]


def test_missing_stop_loss_checked_confirmation_blocks():
    result = evaluate(
        owner_evidence_confirmation=owner_confirmation(
            owner_confirmed_stop_loss_checked=False
        )
    )
    assert result["status"] == EVIDENCE_BLOCKED_OWNER_CONFIRMATION
    assert "owner_confirmed_stop_loss_checked_required" in result["blockers"]


def test_missing_take_profit_checked_confirmation_blocks():
    result = evaluate(
        owner_evidence_confirmation=owner_confirmation(
            owner_confirmed_take_profit_checked=False
        )
    )
    assert result["status"] == EVIDENCE_BLOCKED_OWNER_CONFIRMATION
    assert "owner_confirmed_take_profit_checked_required" in result["blockers"]


def test_dry_run_rehearsal_classifies_dry_run_only():
    result = evaluate(
        broker_call_result=dry_run_broker_call_result(),
        post_trade_evidence=dry_run_evidence(),
    )
    assert result["status"] == EVIDENCE_CAPTURE_READY
    assert result["post_trade_classification"] == "DRY_RUN_ONLY"


def test_rejected_order_classifies_no_fill_rejected():
    result = evaluate(
        post_trade_evidence=post_trade_evidence(
            evidence_mode="ORDER_REJECTED",
            order_attempted=True,
            order_id_or_sanitized_reference="",
            filled_or_rejected="REJECTED",
            fill_price_or_rejection_reason="margin_check_rejected",
            stop_loss_attached=False,
            take_profit_attached=False,
            realized_pl_when_closed=None,
            close_reason=None,
            post_balance=1000.0,
            post_nav=1000.0,
        )
    )
    assert result["post_trade_classification"] == "NO_FILL_REJECTED"


def test_open_submitted_pending_classifies_open_or_pending():
    result = evaluate(
        post_trade_evidence=post_trade_evidence(
            evidence_mode="ORDER_SUBMITTED",
            filled_or_rejected="PENDING",
            realized_pl_when_closed=None,
            close_reason=None,
        )
    )
    assert result["post_trade_classification"] == "OPEN_OR_PENDING"


def test_filled_open_position_classifies_open_position():
    result = evaluate(
        post_trade_evidence=post_trade_evidence(
            evidence_mode="ORDER_FILLED",
            filled_or_rejected="FILLED",
            realized_pl_when_closed=None,
            unrealized_pl_snapshot=0.25,
            close_reason=None,
        )
    )
    assert result["post_trade_classification"] == "OPEN_POSITION"


def test_closed_positive_pl_classifies_profit():
    result = evaluate(post_trade_evidence=post_trade_evidence(realized_pl_when_closed=2.0))
    assert result["post_trade_classification"] == "PROFIT"


def test_closed_negative_pl_classifies_loss():
    result = evaluate(
        post_trade_evidence=post_trade_evidence(realized_pl_when_closed=-2.0)
    )
    assert result["post_trade_classification"] == "LOSS"


def test_closed_zero_pl_classifies_breakeven():
    result = evaluate(
        post_trade_evidence=post_trade_evidence(realized_pl_when_closed=0.0)
    )
    assert result["post_trade_classification"] == "BREAKEVEN"


def test_overnight_open_position_requires_morning_proof_when_hold_allowed():
    result = evaluate(
        post_trade_evidence=post_trade_evidence(
            evidence_mode="ORDER_FILLED",
            filled_or_rejected="FILLED",
            realized_pl_when_closed=None,
            unrealized_pl_snapshot=-0.1,
            close_reason=None,
            hold_allowed_overnight=True,
        )
    )
    assert result["overnight_followup_required"] is True
    assert result["morning_proof_required"] is True


def test_no_overnight_proof_when_closed():
    result = evaluate(
        post_trade_evidence=post_trade_evidence(
            evidence_mode="ORDER_CLOSED",
            realized_pl_when_closed=1.0,
            hold_allowed_overnight=True,
        )
    )
    assert result["overnight_followup_required"] is False
    assert result["morning_proof_required"] is False


def test_normalized_evidence_package_contains_no_token_account_id():
    result = evaluate()
    normalized = json.dumps(result["normalized_evidence_package"], sort_keys=True)
    assert "SECRET" not in normalized
    assert "REAL_TOKEN" not in normalized
    assert "REAL_ACCOUNT" not in normalized
    assert "account_id" not in normalized
    assert "token" not in normalized


def test_all_execution_authority_fields_remain_false():
    assert_execution_authority_false(evaluate())


def test_output_is_json_serializable():
    json.dumps(evaluate(), sort_keys=True)


def test_script_dry_run_prints_json_and_performs_no_broker_action():
    code, payload = run_script([])
    assert code == 0
    assert payload["script_status"] == "POST_TRADE_EVIDENCE_DRY_RUN_PACKAGE"
    assert payload["broker_network_call_performed"] is False
    assert payload["order_placement_performed"] is False
    assert payload["credential_read_performed"] is False
    assert payload["account_id_read_performed"] is False


def test_script_print_template_prints_sanitized_template():
    code, payload = run_script(["--print-template"])
    assert code == 0
    assert payload["script_status"] == "POST_TRADE_EVIDENCE_TEMPLATE_ONLY"
    assert payload["template"]["broker"] == "OANDA_DEMO"
    rendered = json.dumps(payload, sort_keys=True)
    assert "SECRET" not in rendered
    assert payload["order_placement_performed"] is False


def test_script_capture_evidence_without_confirmations_blocks():
    code, payload = run_script(["--capture-evidence"])
    assert code == 1
    assert payload["script_status"] == "BLOCKED_MISSING_EVIDENCE_CONFIRMATIONS"
    assert "--i-confirm-post-trade-evidence-reviewed" in payload[
        "missing_confirmations"
    ]
    assert payload["order_placement_performed"] is False


def test_script_capture_evidence_with_confirmations_returns_package():
    args = [
        "--capture-evidence",
        "--i-confirm-post-trade-evidence-reviewed",
        "--i-confirm-no-second-order",
        "--i-confirm-no-credentials-in-evidence",
        "--i-confirm-no-account-ids-in-evidence",
        "--i-confirm-stop-loss-checked",
        "--i-confirm-take-profit-checked",
        "--i-confirm-pl-recorded",
    ]
    code, payload = run_script(args)
    assert code == 0
    assert payload["script_status"] == EVIDENCE_CAPTURE_READY
    assert payload["decision"]["normalized_evidence_package"]["ready"] is True
    assert payload["broker_network_call_performed"] is False
    assert payload["order_placement_performed"] is False
