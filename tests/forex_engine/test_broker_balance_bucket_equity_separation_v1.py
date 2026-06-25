from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.broker_balance_bucket_equity_separation_v1 import (  # noqa: E402
    BROKER_BALANCE_BUCKET_EQUITY_SEPARATION_READY,
    REJECTED_LIVE_TRADING,
    evaluate_broker_balance_bucket_equity_separation_v1,
)
from scripts.forex_delivery.run_broker_balance_bucket_equity_separation_v1 import (  # noqa: E402
    main as script_main,
)


def account_snapshot(**overrides):
    snapshot = {
        "balance": "10000.00",
        "NAV": "10000.25",
        "unrealizedPL": "0.25",
        "pl": "0.00",
        "marginUsed": "0.01",
        "marginAvailable": "9999.99",
        "openTradeCount": 0,
        "openPositionCount": 0,
        "pendingOrderCount": 0,
    }
    snapshot.update(overrides)
    return snapshot


def bucket_risk_policy(**overrides):
    policy = {
        "bucket_currency": "USD",
        "configured_trade_bucket_balance": 1000.0,
        "allow_bucket_to_equal_broker_balance": False,
        "max_single_trade_risk_pct": 1.0,
        "max_next_trade_risk_pct": 0.5,
        "demo_only": True,
        "live_trading": False,
        "one_order_only": True,
        "require_owner_approval_for_next_trade": True,
        "allow_next_trade_while_open_position": False,
        "compounding_enabled": False,
        "no_live_allocation": True,
    }
    policy.update(overrides)
    return policy


def evaluate(account=None, policy=None):
    return evaluate_broker_balance_bucket_equity_separation_v1(
        account_snapshot=account or account_snapshot(),
        bucket_risk_policy=policy or bucket_risk_policy(),
    )


def run_script(args):
    stream = StringIO()
    with redirect_stdout(stream):
        code = script_main(args)
    return code, json.loads(stream.getvalue())


def test_open_trade_blocks_next_trade_by_default() -> None:
    result = evaluate(
        account=account_snapshot(openTradeCount=1, openPositionCount=1)
    )

    assert result["status"] == BROKER_BALANCE_BUCKET_EQUITY_SEPARATION_READY
    assert result["open_exposure_present"] is True
    assert result["next_trade_allowed"] is False
    assert "open_trade_or_position_blocks_next_trade" in result["next_trade_blockers"]
    assert "owner_approval_required_for_next_trade" in result["next_trade_blockers"]


def test_nav_equity_differs_from_broker_balance_when_unrealized_pl_exists() -> None:
    result = evaluate(
        account=account_snapshot(
            balance="10000.00",
            NAV="10000.25",
            unrealizedPL="0.25",
        )
    )

    assert result["broker_reported_balance"] == 10000.0
    assert result["broker_reported_nav"] == 10000.25
    assert result["account_equity"] == 10000.25
    assert result["account_equity"] != result["broker_reported_balance"]
    assert result["decision_summary"]["nav_or_equity_includes_open_unrealized_pl"]


def test_trade_bucket_remains_separate_from_full_broker_balance() -> None:
    result = evaluate(
        account=account_snapshot(balance="10000.00"),
        policy=bucket_risk_policy(configured_trade_bucket_balance=1000.0),
    )

    assert result["broker_reported_balance"] == 10000.0
    assert result["aios_trade_bucket_balance"] == 1000.0
    assert result["decision_summary"]["broker_balance_is_not_aios_trade_bucket"]
    assert result["decision_summary"]["broker_balance_equals_aios_trade_bucket"] is False


def test_bucket_equal_to_broker_balance_requires_explicit_policy() -> None:
    result = evaluate(
        account=account_snapshot(balance="10000.00"),
        policy=bucket_risk_policy(configured_trade_bucket_balance=10000.0),
    )

    assert result["status"] == "BLOCKED_INVALID_BUCKET_RISK_POLICY"
    assert (
        "bucket_balance_matches_broker_balance_without_explicit_policy"
        in result["blockers"]
    )


def test_max_risk_amount_uses_trade_bucket_not_full_broker_balance() -> None:
    result = evaluate(
        account=account_snapshot(balance="10000.00"),
        policy=bucket_risk_policy(
            configured_trade_bucket_balance=1000.0,
            max_single_trade_risk_pct=1.0,
            max_next_trade_risk_pct=0.5,
        ),
    )

    assert result["max_single_trade_risk_amount"] == 10.0
    assert result["max_next_trade_risk_amount"] == 5.0
    assert result["max_single_trade_risk_amount"] != 100.0
    assert result["risk_available_balance"] == 1000.0


def test_live_trading_true_is_rejected() -> None:
    result = evaluate(policy=bucket_risk_policy(live_trading=True))

    assert result["status"] == REJECTED_LIVE_TRADING
    assert "bucket_policy_live_trading_must_be_false" in result["blockers"]
    assert result["next_trade_allowed"] is False
    assert result["live_allocation_allowed"] is False
    assert result["no_live_allocation"] is True


def test_compounding_and_withdraw_remain_false_while_trade_is_open_unrealized() -> None:
    result = evaluate(
        account=account_snapshot(openTradeCount=1, unrealizedPL="0.25"),
        policy=bucket_risk_policy(compounding_enabled=True),
    )

    assert result["compound_allowed"] is False
    assert result["withdraw_allowed"] is False
    assert "unrealized_pl_not_compoundable" in result["compound_blockers"]
    assert "unrealized_pl_not_withdrawable" in result["withdraw_blockers"]
    assert result["realized_pl_applied_to_bucket_here"] is False


def test_no_network_broker_order_or_credential_flags_remain_false() -> None:
    result = evaluate()

    false_flags = (
        "network_call_performed",
        "broker_network_call_performed",
        "broker_api_call_performed",
        "credential_read_performed",
        "account_id_read_performed",
        "dotenv_read",
        "env_read",
        "order_placement_performed",
        "order_close_performed",
        "order_mutation_performed",
        "trade_mutation_performed",
        "position_mutation_performed",
        "live_endpoint_used",
        "raw_broker_payload_persisted",
        "file_persistence_performed",
    )
    for flag in false_flags:
        assert result[flag] is False
        assert result["safety_proof"][flag] is False
    assert all(value is False for value in result["execution_authority"].values())


def test_account_equity_uses_balance_plus_unrealized_when_nav_absent() -> None:
    snapshot = account_snapshot(balance="10000.00", unrealizedPL="-0.25")
    snapshot.pop("NAV")

    result = evaluate(account=snapshot)

    assert result["broker_reported_nav"] is None
    assert result["account_equity"] == 9999.75
    assert result["decision_summary"]["account_equity_source"] == (
        "balance_plus_unrealized_pl"
    )


def test_script_default_prints_sanitized_json_only() -> None:
    code, payload = run_script([])

    assert code == 0
    assert payload["script_status"] == "BROKER_BALANCE_BUCKET_EQUITY_SEPARATION_PACKAGE"
    assert payload["sanitized_input_only"] is True
    assert payload["broker_network_call_performed"] is False
    assert payload["credential_read_performed"] is False
    assert payload["order_placement_performed"] is False
    assert payload["decision"]["next_trade_allowed"] is False


def test_script_print_template_prints_sanitized_template() -> None:
    code, payload = run_script(["--print-template"])

    assert code == 0
    assert (
        payload["script_status"]
        == "BROKER_BALANCE_BUCKET_EQUITY_SEPARATION_TEMPLATE_ONLY"
    )
    assert payload["bucket_risk_policy"]["live_trading"] is False
    assert payload["raw_broker_payload_persisted"] is False
    rendered = json.dumps(payload, sort_keys=True)
    assert "SECRET" not in rendered
    assert "TOKEN" not in rendered
