from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.oanda_readonly_account_snapshot_balance_separation_adapter_v1 import (  # noqa: E402
    BLOCKED_BALANCE_SEPARATION_INPUTS,
    BLOCKED_MISSING_ACCOUNT_SNAPSHOT,
    OANDA_READONLY_ACCOUNT_SNAPSHOT_BALANCE_SEPARATION_READY,
    REJECTED_UNSAFE_CAPTURE_AUTHORITY,
    evaluate_oanda_readonly_account_snapshot_balance_separation_adapter_v1,
)
from scripts.forex_delivery.run_oanda_readonly_account_snapshot_balance_separation_adapter_v1 import (  # noqa: E402
    main as script_main,
)


def account_snapshot(**overrides):
    snapshot = {
        "balance": "10000.00",
        "NAV": "9999.9999",
        "unrealizedPL": "-0.0001",
        "pl": "0.00",
        "marginUsed": "0.01",
        "marginAvailable": "9999.98",
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


def read_only_capture_result(
    *,
    snapshot=None,
    open_trade_evidence=None,
    open_position_evidence=None,
):
    return {
        "pl_evidence": {
            "realized_pl_values": [],
            "realized_pl_total": "0",
            "open_trade_evidence": open_trade_evidence or [],
            "open_position_evidence": open_position_evidence or [],
            "account_summary_snapshot": snapshot or account_snapshot(),
            "evidence_found": True,
        },
        "execution_authority": {
            "network_allowed": False,
            "broker_call_allowed": False,
            "credential_access_allowed": False,
            "order_placement_allowed": False,
            "order_close_allowed": False,
            "order_mutation_allowed": False,
            "trade_mutation_allowed": False,
            "position_mutation_allowed": False,
            "live_endpoint_allowed": False,
            "live_trading_allowed": False,
            "raw_broker_payload_persistence_allowed": False,
        },
        "broker_network_call_performed": False,
        "broker_api_call_performed": False,
        "credential_read_performed": False,
        "account_id_read_performed": False,
        "order_placement_performed": False,
        "order_close_performed": False,
        "order_mutation_performed": False,
        "trade_mutation_performed": False,
        "position_mutation_performed": False,
        "live_endpoint_used": False,
        "raw_broker_payload_persisted": False,
        "file_persistence_performed": False,
    }


def evaluate(capture=None, policy=None):
    return evaluate_oanda_readonly_account_snapshot_balance_separation_adapter_v1(
        read_only_capture_result=capture or read_only_capture_result(),
        bucket_risk_policy=policy or bucket_risk_policy(),
    )


def run_script(args):
    stream = StringIO()
    with redirect_stdout(stream):
        code = script_main(args)
    return code, json.loads(stream.getvalue())


def test_adapter_extracts_account_summary_snapshot_from_pl_evidence() -> None:
    result = evaluate()

    assert result["status"] == OANDA_READONLY_ACCOUNT_SNAPSHOT_BALANCE_SEPARATION_READY
    assert result["normalized_account_snapshot"]["balance"] == "10000.00"
    assert result["normalized_account_snapshot"]["NAV"] == "9999.9999"
    assert (
        result["source_capture_summary"]["account_snapshot_source"]
        == "pl_evidence.account_summary_snapshot"
    )


def test_adapter_derives_open_trade_count_from_open_trade_evidence() -> None:
    result = evaluate(
        capture=read_only_capture_result(
            open_trade_evidence=[
                {
                    "trade_id": "328",
                    "instrument": "EUR_USD",
                    "currentUnits": "1",
                    "unrealizedPL": "-0.0001",
                },
            ],
            open_position_evidence=[
                {
                    "instrument": "EUR_USD",
                    "long_units": "1",
                    "short_units": "0",
                    "unrealizedPL": "-0.0001",
                },
            ],
        )
    )

    assert result["normalized_account_snapshot"]["openTradeCount"] == 1
    assert result["normalized_account_snapshot"]["openPositionCount"] == 1
    assert result["source_capture_summary"]["open_trade_evidence_count"] == 1


def test_open_trade_blocks_next_trade_by_default_through_balance_separation() -> None:
    result = evaluate(
        capture=read_only_capture_result(
            open_trade_evidence=[{"trade_id": "328", "unrealizedPL": "-0.0001"}],
            open_position_evidence=[{"instrument": "EUR_USD", "long_units": "1"}],
        )
    )
    separation = result["balance_separation_decision"]

    assert separation["open_exposure_present"] is True
    assert separation["next_trade_allowed"] is False
    assert "open_trade_or_position_blocks_next_trade" in separation["next_trade_blockers"]
    assert "owner_approval_required_for_next_trade" in separation["next_trade_blockers"]


def test_risk_amount_uses_configured_bucket_not_full_broker_balance() -> None:
    result = evaluate(
        capture=read_only_capture_result(
            snapshot=account_snapshot(balance="10000.00", NAV="10000.00")
        ),
        policy=bucket_risk_policy(configured_trade_bucket_balance=1000.0),
    )
    separation = result["balance_separation_decision"]

    assert separation["broker_reported_balance"] == 10000.0
    assert separation["aios_trade_bucket_balance"] == 1000.0
    assert separation["max_single_trade_risk_amount"] == 10.0
    assert separation["risk_available_balance"] == 1000.0
    assert (
        separation["decision_summary"][
            "risk_uses_configured_aios_bucket_not_full_broker_balance"
        ]
        is True
    )


def test_missing_account_snapshot_blocks() -> None:
    result = evaluate(
        capture={
            "pl_evidence": {
                "open_trade_evidence": [],
                "open_position_evidence": [],
            }
        }
    )

    assert result["status"] == BLOCKED_MISSING_ACCOUNT_SNAPSHOT
    assert result["balance_separation_decision"] is None
    assert "sanitized_account_snapshot_required" in result["blockers"]


def test_unsafe_authority_true_rejects() -> None:
    capture = read_only_capture_result()
    capture["network_allowed"] = True

    result = evaluate(capture=capture)

    assert result["status"] == REJECTED_UNSAFE_CAPTURE_AUTHORITY
    assert "unsafe_read_only_capture_result_network_allowed_true" in result["blockers"]
    assert result["balance_separation_decision"] is None


def test_live_trading_true_rejects_through_balance_separation() -> None:
    result = evaluate(policy=bucket_risk_policy(live_trading=True))

    assert result["status"] == BLOCKED_BALANCE_SEPARATION_INPUTS
    assert result["balance_separation_decision"]["status"] == "REJECTED_LIVE_TRADING"
    assert "bucket_policy_live_trading_must_be_false" in result["blockers"]
    assert result["balance_separation_decision"]["live_allocation_allowed"] is False


def test_decision_pl_evidence_account_snapshot_shape_is_supported() -> None:
    result = evaluate(
        capture={
            "decision": {
                "pl_capture_classification": "FILLED_TRADE_PL_OPEN_UNREALIZED",
                "pl_evidence": {
                    "account_summary_snapshot": account_snapshot(),
                    "open_trade_evidence": [],
                    "open_position_evidence": [],
                },
            }
        }
    )

    assert result["status"] == OANDA_READONLY_ACCOUNT_SNAPSHOT_BALANCE_SEPARATION_READY
    assert (
        result["source_capture_summary"]["account_snapshot_source"]
        == "decision.pl_evidence.account_summary_snapshot"
    )


def test_cli_prints_sanitized_json_and_no_broker_order_credential_flags_true() -> None:
    code, payload = run_script([])

    assert code == 0
    assert payload["script_status"] == (
        "OANDA_READONLY_ACCOUNT_SNAPSHOT_BALANCE_SEPARATION_ADAPTER_PACKAGE"
    )
    assert payload["decision"]["status"] == (
        OANDA_READONLY_ACCOUNT_SNAPSHOT_BALANCE_SEPARATION_READY
    )
    false_flags = (
        "broker_network_call_performed",
        "broker_api_call_performed",
        "credential_read_performed",
        "account_id_read_performed",
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
        assert payload[flag] is False
        assert payload["decision"][flag] is False
        assert payload["decision"]["safety_proof"][flag] is False
    assert all(
        value is False for value in payload["decision"]["execution_authority"].values()
    )


def test_cli_print_template_prints_sanitized_template() -> None:
    code, payload = run_script(["--print-template"])

    assert code == 0
    assert payload["script_status"] == (
        "OANDA_READONLY_ACCOUNT_SNAPSHOT_BALANCE_SEPARATION_ADAPTER_TEMPLATE_ONLY"
    )
    assert payload["bucket_risk_policy"]["live_trading"] is False
    assert payload["broker_network_call_performed"] is False
    assert payload["credential_read_performed"] is False
