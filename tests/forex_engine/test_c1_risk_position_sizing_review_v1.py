from __future__ import annotations

import json
from pathlib import Path

from automation.forex_engine.c1_risk_position_sizing_review_v1 import (
    evaluate_c1_risk_position_sizing_review,
)
from scripts.forex_delivery.run_c1_risk_position_sizing_review_v1 import (
    generate_artifacts,
)


ALLOWED_P4_REVIEW_STATUSES = {
    "P4_RISK_POSITION_SIZING_PASSED_FOR_P5_REVIEW",
    "P4_RISK_POSITION_SIZING_FAILED_RULES_REQUIRED",
    "P4_RISK_POSITION_SIZING_FAILED_P3_REPAIR_REQUIRED",
}

REQUIRED_RISK_RULES = {
    "max_risk_per_trade_percent",
    "max_daily_loss_percent",
    "max_weekly_loss_percent",
    "max_consecutive_losses",
    "max_open_positions",
    "max_orders_per_signal",
    "stop_loss_required",
    "take_profit_required",
    "minimum_reward_to_risk",
    "max_strategy_drawdown_percent",
    "one_order_rule",
    "daily_stop_rule",
    "weekly_stop_rule",
    "kill_switch_triggers",
    "position_size_formula",
    "broker_account_dependency_block",
    "no_demo_live_approval",
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
]

GENERATED_PATHS = [
    Path("Reports/forex_delivery/AIOS_FOREX_C1_RISK_POSITION_SIZING_REVIEW_V1.json"),
    Path(
        "Reports/forex_delivery/AIOS_FOREX_C1_RISK_POSITION_SIZING_REVIEW_V1_REPORT.md"
    ),
    Path(
        "Reports/forex_delivery/AIOS_FOREX_C1_RISK_POSITION_SIZING_REVIEW_NEXT_ACTION_QUEUE_V1.md"
    ),
]


def test_p4_review_contract() -> None:
    result = evaluate_c1_risk_position_sizing_review()

    assert result["candidate_id"] == "c1-eur-buy"
    assert result["input_score"] in [85, 100]
    assert result["post_p4_score"] <= 100
    assert result["p4_review_status"] in ALLOWED_P4_REVIEW_STATUSES
    assert result["p5_readiness"] in {"P5_READY", "NOT_READY"}

    if result["p5_readiness"] == "P5_READY":
        assert (
            result["next_required_lane"]
            == "P5_SUPERVISED_DEMO_TRADE_READINESS_REVIEW"
        )
    if result["p5_readiness"] == "NOT_READY":
        assert (
            result["next_required_lane"]
            != "P5_SUPERVISED_DEMO_TRADE_READINESS_REVIEW"
        )


def test_risk_policy_contains_conservative_required_rules() -> None:
    result = evaluate_c1_risk_position_sizing_review()
    risk_policy = result["risk_policy"]

    assert REQUIRED_RISK_RULES.issubset(set(risk_policy))
    assert risk_policy["max_risk_per_trade_percent"] <= 0.25
    assert risk_policy["max_daily_loss_percent"] <= 1.00
    assert risk_policy["max_weekly_loss_percent"] <= 2.00
    assert risk_policy["max_open_positions"] == 1
    assert risk_policy["max_orders_per_signal"] == 1
    assert risk_policy["stop_loss_required"] is True
    assert risk_policy["take_profit_required"] is True
    assert risk_policy["one_order_rule"] is True
    assert risk_policy["daily_stop_rule"] is True
    assert risk_policy["weekly_stop_rule"] is True
    assert risk_policy["no_demo_live_approval"] is True


def test_position_sizing_is_formula_only() -> None:
    result = evaluate_c1_risk_position_sizing_review()
    formula = result["position_sizing_formula"]
    formula_text = " ".join(
        [
            formula["risk_amount_formula"],
            formula["position_size_formula"],
            " ".join(formula["required_inputs"]),
        ]
    )

    assert formula["formula_only"] is True
    assert "account_equity" in formula_text
    assert "stop_loss_value_per_unit" in formula_text
    assert "risk_amount = account_equity *" in formula["risk_amount_formula"]
    assert (
        "position_size = risk_amount / stop_loss_value_per_unit"
        in formula["position_size_formula"]
    )


def test_broker_account_dependency_and_forbidden_actions() -> None:
    result = evaluate_c1_risk_position_sizing_review()
    broker_block = result["broker_account_dependency_block"]

    assert broker_block
    assert broker_block["blocked"] is True
    assert "sanitized broker/account snapshot" in broker_block["p5_requirement"]
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
    assert generated["post_p4_score"] == result["post_p4_score"]
    assert generated["p4_review_status"] == result["p4_review_status"]
    assert generated["p5_readiness"] == result["p5_readiness"]
    assert generated["next_required_lane"] == result["next_required_lane"]
