from __future__ import annotations

import json
from pathlib import Path

from automation.forex_engine.c1_supervised_demo_trade_readiness_review_v1 import (
    evaluate_c1_supervised_demo_trade_readiness_review,
)
from scripts.forex_delivery.run_c1_supervised_demo_trade_readiness_review_v1 import (
    generate_artifacts,
)


ALLOWED_P5_REVIEW_STATUSES = {
    "P5_SUPERVISED_DEMO_READINESS_PASSED_FOR_P6_OWNER_APPROVAL",
    "P5_SUPERVISED_DEMO_READINESS_FAILED_RULES_REQUIRED",
    "P5_SUPERVISED_DEMO_READINESS_FAILED_P4_REPAIR_REQUIRED",
}

REQUIRED_READINESS_RULES = {
    "sanitized_broker_account_snapshot_required",
    "owner_approval_required",
    "demo_account_only",
    "live_trading_blocked",
    "broker_api_access_blocked",
    "credential_access_blocked",
    "order_placement_blocked",
    "money_movement_blocked",
    "one_order_rule_required",
    "tp_sl_required",
    "reward_to_risk_required",
    "daily_stop_required",
    "weekly_stop_required",
    "kill_switch_required",
    "audit_report_required",
    "manual_owner_review_required",
    "no_autonomy_approval",
    "no_demo_order_placement_in_this_packet",
    "minimum_reward_to_risk",
    "max_risk_per_trade_percent",
    "max_daily_loss_percent",
    "max_weekly_loss_percent",
    "max_open_positions",
    "max_orders_per_signal",
}

BANNED_TOKENS = [
    "TODO",
    "TBD",
    "@filename",
    "probably",
    "roughly",
    "approximately",
    "I estimate",
    "live ready",
    "profitable trading readiness: true",
    "autonomous trading readiness: true",
    "guaranteed profit",
    "guaranteed returns",
    "100-120 percent verified",
    "demo order approved",
    "live order approved",
]

GENERATED_PATHS = [
    Path(
        "Reports/forex_delivery/AIOS_FOREX_C1_SUPERVISED_DEMO_TRADE_READINESS_REVIEW_V1.json"
    ),
    Path(
        "Reports/forex_delivery/AIOS_FOREX_C1_SUPERVISED_DEMO_TRADE_READINESS_REVIEW_V1_REPORT.md"
    ),
    Path(
        "Reports/forex_delivery/AIOS_FOREX_C1_SUPERVISED_DEMO_TRADE_READINESS_REVIEW_NEXT_ACTION_QUEUE_V1.md"
    ),
]


def test_p5_review_contract() -> None:
    result = evaluate_c1_supervised_demo_trade_readiness_review()

    assert result["candidate_id"] == "c1-eur-buy"
    assert result["input_score"] in [85, 100]
    assert result["post_p5_score"] <= 100
    assert result["p5_review_status"] in ALLOWED_P5_REVIEW_STATUSES
    assert result["p6_readiness"] in {"P6_READY", "NOT_READY"}

    if result["p6_readiness"] == "P6_READY":
        assert (
            result["next_required_lane"]
            == "P6_DEMO_ORDER_INTENT_OWNER_APPROVAL_GATE"
        )
    if result["p6_readiness"] == "NOT_READY":
        assert (
            result["next_required_lane"]
            != "P6_DEMO_ORDER_INTENT_OWNER_APPROVAL_GATE"
        )


def test_demo_readiness_policy_contains_required_rules() -> None:
    result = evaluate_c1_supervised_demo_trade_readiness_review()
    policy = result["demo_readiness_policy"]

    assert REQUIRED_READINESS_RULES.issubset(set(policy))
    assert policy["sanitized_broker_account_snapshot_required"] is True
    assert policy["owner_approval_required"] is True
    assert policy["demo_account_only"] is True
    assert policy["live_trading_blocked"] is True
    assert policy["broker_api_access_blocked"] is True
    assert policy["credential_access_blocked"] is True
    assert policy["order_placement_blocked"] is True
    assert policy["money_movement_blocked"] is True
    assert policy["one_order_rule_required"] is True
    assert policy["tp_sl_required"] is True
    assert policy["minimum_reward_to_risk"] >= 1.20
    assert policy["max_risk_per_trade_percent"] <= 0.25
    assert policy["max_daily_loss_percent"] <= 1.00
    assert policy["max_weekly_loss_percent"] <= 2.00


def test_safety_gates_and_final_sentence_exist() -> None:
    result = evaluate_c1_supervised_demo_trade_readiness_review()

    assert result["snapshot_requirement"][
        "sanitized_broker_account_snapshot_required"
    ] is True
    assert result["owner_approval_gate"]["owner_approval_required"] is True
    assert result["one_order_rules"]["one_order_rule_required"] is True
    assert result["tp_sl_guardrails"]["tp_sl_required"] is True
    assert result["stop_rules"]["daily_stop_required"] is True
    assert result["stop_rules"]["weekly_stop_required"] is True
    assert result["kill_switch_rules"]["kill_switch_required"] is True
    assert result["audit_requirements"]["audit_report_required"] is True
    assert result["audit_requirements"]["manual_owner_review_required"] is True
    assert "broker/API access" in result["forbidden_actions"]
    assert "credentials" in result["forbidden_actions"]
    assert "account access" in result["forbidden_actions"]
    assert "live trading" in result["forbidden_actions"]
    assert "order placement" in result["forbidden_actions"]
    assert "money movement" in result["forbidden_actions"]
    assert result["final_owner_sentence"]


def test_generated_artifacts_are_present_and_clean() -> None:
    generate_artifacts()

    for path in GENERATED_PATHS:
        assert path.exists(), f"Missing generated artifact: {path}"
        text = path.read_text(encoding="utf-8")
        for token in BANNED_TOKENS:
            assert token not in text


def test_generated_json_matches_evaluator() -> None:
    result = generate_artifacts()
    generated = json.loads(GENERATED_PATHS[0].read_text(encoding="utf-8"))

    assert generated["campaign_id"] == result["campaign_id"]
    assert generated["candidate_id"] == result["candidate_id"]
    assert generated["input_score"] == result["input_score"]
    assert generated["post_p5_score"] == result["post_p5_score"]
    assert generated["p5_review_status"] == result["p5_review_status"]
    assert generated["p6_readiness"] == result["p6_readiness"]
    assert generated["next_required_lane"] == result["next_required_lane"]
