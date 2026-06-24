from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.oanda_demo_result_to_bucket_and_next_allocation_v1 import (  # noqa: E402
    BUCKET_BLOCKED_ALLOCATION_POLICY,
    BUCKET_BLOCKED_MISSING_BUCKET_STATE,
    BUCKET_BLOCKED_MISSING_POST_TRADE_CAPTURE,
    BUCKET_BLOCKED_OWNER_CONFIRMATION,
    BUCKET_BLOCKED_POST_TRADE_NOT_READY,
    BUCKET_REJECTED,
    BUCKET_UPDATE_READY,
    evaluate_oanda_demo_result_to_bucket_and_next_allocation_v1,
)
from scripts.forex_delivery.run_oanda_demo_result_to_bucket_and_next_allocation_v1 import (  # noqa: E402
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


def post_trade_capture(classification="PROFIT", realized_pl=10.0, **overrides):
    result = {
        "status": "EVIDENCE_CAPTURE_READY",
        "post_trade_classification": classification,
        "normalized_evidence_package": {
            "realized_pl_when_closed": realized_pl,
            "post_trade_classification": classification,
        },
        "execution_authority": EXECUTION_AUTHORITY_FALSE.copy(),
    }
    result.update(overrides)
    return result


def bucket_state(**overrides):
    state = {
        "bucket_currency": "USD",
        "starting_bucket_balance": 1000.0,
        "current_bucket_balance": 1000.0,
        "total_realized_pl": 0.0,
        "current_cycle_start_balance": 1000.0,
        "current_cycle_realized_pl": 0.0,
        "cycle_profit_target_min_pct": 2.0,
        "cycle_profit_target_max_pct": 5.0,
        "max_single_trade_risk_pct": 1.0,
        "one_order_only": True,
        "demo_only": True,
        "live_trading": False,
    }
    state.update(overrides)
    return state


def allocation_policy(**overrides):
    policy = {
        "allocation_mode": "CONTINUE_DEMO",
        "compounding_enabled": False,
        "collect_profit_at_target": True,
        "require_more_evidence_after_loss": True,
        "require_owner_approval_for_next_trade": True,
        "max_next_trade_risk_pct": 1.0,
        "no_live_allocation": True,
    }
    policy.update(overrides)
    return policy


def owner_confirmation(**overrides):
    confirmation = {
        "owner_confirmed_result_reviewed": True,
        "owner_confirmed_bucket_update_demo_only": True,
        "owner_confirmed_no_live_allocation": True,
        "owner_confirmed_next_trade_requires_approval": True,
        "owner_confirmed_no_autonomous_compounding": True,
    }
    confirmation.update(overrides)
    return confirmation


def evaluate(**overrides):
    payload = {
        "post_trade_capture_result": post_trade_capture(),
        "bucket_state": bucket_state(),
        "allocation_policy": allocation_policy(),
        "owner_bucket_confirmation": owner_confirmation(),
    }
    payload.update(overrides)
    return evaluate_oanda_demo_result_to_bucket_and_next_allocation_v1(**payload)


def run_script(args):
    stream = StringIO()
    with redirect_stdout(stream):
        code = script_main(args)
    return code, json.loads(stream.getvalue())


def assert_execution_authority_false(result):
    assert result["execution_authority"] == EXECUTION_AUTHORITY_FALSE


def test_default_blocks_missing_post_trade_capture():
    result = evaluate_oanda_demo_result_to_bucket_and_next_allocation_v1()
    assert result["status"] == BUCKET_BLOCKED_MISSING_POST_TRADE_CAPTURE
    assert "missing_post_trade_capture_result" in result["blockers"]
    assert_execution_authority_false(result)


def test_post_trade_not_ready_blocks():
    result = evaluate(
        post_trade_capture_result=post_trade_capture(status="EVIDENCE_BLOCKED")
    )
    assert result["status"] == BUCKET_BLOCKED_POST_TRADE_NOT_READY
    assert "post_trade_capture_status_not_ready" in result["blockers"]


def test_missing_bucket_state_blocks():
    result = evaluate(bucket_state=None)
    assert result["status"] == BUCKET_BLOCKED_MISSING_BUCKET_STATE
    assert "missing_bucket_state" in result["blockers"]


def test_invalid_bucket_currency_blocks():
    result = evaluate(bucket_state=bucket_state(bucket_currency="EUR"))
    assert result["status"] == BUCKET_BLOCKED_MISSING_BUCKET_STATE
    assert "bucket_state_currency_must_be_usd" in result["blockers"]


def test_live_trading_true_blocks():
    result = evaluate(bucket_state=bucket_state(live_trading=True))
    assert result["status"] == BUCKET_BLOCKED_MISSING_BUCKET_STATE
    assert "bucket_state_live_trading_must_be_false" in result["blockers"]


def test_max_single_trade_risk_above_five_pct_blocks():
    result = evaluate(bucket_state=bucket_state(max_single_trade_risk_pct=5.1))
    assert result["status"] == BUCKET_BLOCKED_MISSING_BUCKET_STATE
    assert "bucket_state_max_single_trade_risk_pct_must_be_lte_five" in result[
        "blockers"
    ]


def test_missing_allocation_policy_blocks():
    result = evaluate(allocation_policy=None)
    assert result["status"] == BUCKET_BLOCKED_ALLOCATION_POLICY
    assert "missing_allocation_policy" in result["blockers"]


def test_live_allocation_allowed_blocks():
    result = evaluate(allocation_policy=allocation_policy(no_live_allocation=False))
    assert result["status"] == BUCKET_BLOCKED_ALLOCATION_POLICY
    assert "allocation_policy_no_live_allocation_required" in result["blockers"]


def test_missing_owner_confirmation_blocks():
    result = evaluate(owner_bucket_confirmation=None)
    assert result["status"] == BUCKET_BLOCKED_OWNER_CONFIRMATION
    assert "missing_owner_bucket_confirmation" in result["blockers"]


def test_token_account_key_in_capture_result_rejects():
    result = evaluate(post_trade_capture_result=post_trade_capture(token="SECRET"))
    assert result["status"] == BUCKET_REJECTED
    assert "post_trade_capture_forbidden_token_field" in result["blockers"]


def test_dry_run_result_does_not_change_bucket():
    result = evaluate(
        post_trade_capture_result=post_trade_capture(
            classification="DRY_RUN_ONLY",
            realized_pl=None,
        )
    )
    assert result["bucket_update"]["new_bucket_balance"] == 1000.0
    assert result["next_allocation_decision"]["action"] == "continue_demo_rehearsal"


def test_rejected_no_fill_result_does_not_change_bucket():
    result = evaluate(
        post_trade_capture_result=post_trade_capture(
            classification="NO_FILL_REJECTED",
            realized_pl=None,
        )
    )
    assert result["bucket_update"]["new_bucket_balance"] == 1000.0
    assert (
        result["next_allocation_decision"]["action"]
        == "repair_order_or_context_before_retry"
    )


def test_open_position_does_not_change_bucket_and_recommends_wait():
    result = evaluate(
        post_trade_capture_result=post_trade_capture(
            classification="OPEN_POSITION",
            realized_pl=None,
        )
    )
    assert result["bucket_update"]["new_bucket_balance"] == 1000.0
    assert (
        result["next_allocation_decision"]["action"]
        == "wait_for_post_trade_close_evidence"
    )


def test_profit_adds_realized_pl_to_bucket():
    result = evaluate(post_trade_capture_result=post_trade_capture(realized_pl=12.5))
    assert result["bucket_update"]["new_bucket_balance"] == 1012.5
    assert result["bucket_update"]["new_total_realized_pl"] == 12.5


def test_loss_subtracts_realized_pl_from_bucket():
    result = evaluate(
        post_trade_capture_result=post_trade_capture(
            classification="LOSS",
            realized_pl=-7.5,
        )
    )
    assert result["bucket_update"]["new_bucket_balance"] == 992.5
    assert result["bucket_update"]["new_total_realized_pl"] == -7.5


def test_breakeven_leaves_bucket_unchanged():
    result = evaluate(
        post_trade_capture_result=post_trade_capture(
            classification="BREAKEVEN",
            realized_pl=0.0,
        )
    )
    assert result["bucket_update"]["new_bucket_balance"] == 1000.0


def test_profit_below_target_continues_demo_same_lower_risk():
    result = evaluate(post_trade_capture_result=post_trade_capture(realized_pl=10.0))
    assert (
        result["next_allocation_decision"]["action"]
        == "continue_demo_with_same_or_lower_risk"
    )


def test_profit_hitting_target_recommends_collect_profit_and_pause():
    result = evaluate(post_trade_capture_result=post_trade_capture(realized_pl=25.0))
    assert (
        result["next_allocation_decision"]["action"]
        == "collect_profit_and_pause_for_owner_review"
    )
    assert result["cycle_progress"]["target_band_min_hit"] is True


def test_loss_recommends_reduce_risk_and_more_evidence():
    result = evaluate(
        post_trade_capture_result=post_trade_capture(
            classification="LOSS",
            realized_pl=-5.0,
        )
    )
    assert (
        result["next_allocation_decision"]["action"]
        == "reduce_risk_and_require_more_evidence"
    )


def test_breakeven_recommends_no_size_increase():
    result = evaluate(
        post_trade_capture_result=post_trade_capture(
            classification="BREAKEVEN",
            realized_pl=0.0,
        )
    )
    assert (
        result["next_allocation_decision"]["action"]
        == "continue_demo_with_no_size_increase"
    )


def test_next_trade_always_requires_owner_approval():
    result = evaluate()
    assert result["recommendation"]["next_trade_requires_owner_approval"] is True
    assert result["next_allocation_decision"][
        "next_trade_requires_owner_approval"
    ] is True


def test_live_allocation_always_false():
    result = evaluate()
    assert result["recommendation"]["live_allocation_allowed"] is False
    assert result["next_allocation_decision"]["live_allocation_allowed"] is False


def test_autonomous_compounding_always_false():
    result = evaluate()
    assert result["recommendation"]["autonomous_compounding_allowed"] is False
    assert result["next_allocation_decision"][
        "autonomous_compounding_allowed"
    ] is False


def test_all_execution_authority_fields_remain_false():
    assert_execution_authority_false(evaluate())


def test_output_is_json_serializable():
    json.dumps(evaluate(), sort_keys=True)


def test_script_dry_run_prints_json_and_performs_no_broker_action():
    code, payload = run_script([])
    assert code == 0
    assert payload["script_status"] == "RESULT_TO_BUCKET_DRY_RUN_PACKAGE"
    assert payload["broker_network_call_performed"] is False
    assert payload["order_placement_performed"] is False
    assert payload["credential_read_performed"] is False
    assert payload["account_id_read_performed"] is False


def test_script_print_template_prints_sanitized_template():
    code, payload = run_script(["--print-template"])
    assert code == 0
    assert payload["script_status"] == "RESULT_TO_BUCKET_TEMPLATE_ONLY"
    assert payload["template"]["bucket_state"]["bucket_currency"] == "USD"
    rendered = json.dumps(payload, sort_keys=True)
    assert "SECRET" not in rendered
    assert payload["order_placement_performed"] is False


def test_script_evaluate_demo_result_without_confirmations_blocks():
    code, payload = run_script(["--evaluate-demo-result"])
    assert code == 1
    assert payload["script_status"] == "BLOCKED_MISSING_BUCKET_CONFIRMATIONS"
    assert "--i-confirm-result-reviewed" in payload["missing_confirmations"]
    assert payload["order_placement_performed"] is False


def test_script_evaluate_demo_result_with_confirmations_returns_bucket_package():
    args = [
        "--evaluate-demo-result",
        "--i-confirm-result-reviewed",
        "--i-confirm-demo-only-bucket-update",
        "--i-confirm-no-live-allocation",
        "--i-confirm-next-trade-requires-approval",
        "--i-confirm-no-autonomous-compounding",
    ]
    code, payload = run_script(args)
    assert code == 0
    assert payload["script_status"] == BUCKET_UPDATE_READY
    assert payload["decision"]["bucket_update"]["ready"] is True
    assert payload["broker_network_call_performed"] is False
    assert payload["order_placement_performed"] is False
