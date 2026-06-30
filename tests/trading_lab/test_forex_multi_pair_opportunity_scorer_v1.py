from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "apps" / "trading_lab" / "trading_lab" / "forex_multi_pair_opportunity_scorer_v1.py"


def load_module():
    spec = importlib.util.spec_from_file_location("forex_multi_pair_opportunity_scorer_v1", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def pair(symbol: str = "EURUSD", **overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "pair": symbol,
        "confidence_score": 82.0,
        "spread_bps": 1.0,
        "volatility": 0.6,
        "liquidity_score": 78.0,
        "expectancy_score": 74.0,
        "max_drawdown_pct": 3.0,
        "sample_size": 90,
        "evidence_age_days": 4,
        "evidence_quality_score": 88.0,
    }
    payload.update(overrides)
    return payload


def test_app_level_scorer_imports_and_returns_required_fields() -> None:
    module = load_module()
    assert module.FOREX_MULTI_PAIR_OPPORTUNITY_SCORER_V1 == "FOREX_MULTI_PAIR_OPPORTUNITY_SCORER_V1"

    result = module.score_multi_pair_opportunities([pair(), pair("GBPUSD", confidence_score=76.0)])

    assert result["schema"] == "AIOS_FOREX_MULTI_PAIR_OPPORTUNITY_SCORER_V1"
    assert result["mode"] == "PAPER_ONLY"
    assert result["review_only"] is True
    for key in (
        "ranked_pairs",
        "confidence_score",
        "spread_score",
        "volatility_score",
        "liquidity_score",
        "expectancy_score",
        "risk_adjusted_score",
        "proposed_allocation_percent",
        "max_pair_risk_percent",
        "total_portfolio_risk_percent",
        "rejection_reasons",
        "safe_next_action",
    ):
        assert key in result


def test_app_level_scorer_safety_permissions_remain_false() -> None:
    module = load_module()
    result = module.score_multi_pair_opportunities([pair()])

    safety = result["safety"]
    assert safety["scheduler_allowed"] is False
    assert safety["daemon_allowed"] is False
    assert safety["webhook_allowed"] is False
    assert safety["broker_integration"] is False
    assert safety["live_trading"] is False


def test_app_level_scorer_invalid_or_no_input_fails_closed() -> None:
    module = load_module()

    no_input = module.score_multi_pair_opportunities(None)
    assert no_input["total_portfolio_risk_percent"] == 0.0
    assert no_input["proposed_allocation_percent"] == 0.0
    assert "no_valid_pair_metrics" in no_input["rejection_reasons"]

    invalid_input = module.score_multi_pair_opportunities(123)
    assert invalid_input["ranked_pairs"] == []
    assert invalid_input["total_portfolio_risk_percent"] == 0.0
    assert "input_must_be_sequence" in invalid_input["rejection_reasons"]


def test_app_level_policy_caps_prevent_all_in_allocation() -> None:
    module = load_module()
    result = module.score_multi_pair_opportunities(
        [pair(confidence_score=96.0, expectancy_score=90.0)],
        risk_policy={"max_pair_risk_percent": 140.0, "max_total_portfolio_risk_percent": 140.0},
    )

    assert result["total_portfolio_risk_percent"] < 100.0
    assert result["max_pair_risk_percent"] < 100.0
    assert result["proposed_allocation_percent"] == result["total_portfolio_risk_percent"]


def test_app_level_scorer_source_has_no_forbidden_runtime_tokens() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8").lower()
    for token in (
        "requests",
        "socket",
        "urllib",
        "subprocess",
        "os.environ",
        "broker_sdk",
        "schedule.every",
        "start-process",
    ):
        assert token not in source
