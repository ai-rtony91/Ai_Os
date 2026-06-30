from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "apps" / "trading_lab" / "trading_lab" / "forex_short_side_readiness_v1.py"


def load_module():
    spec = importlib.util.spec_from_file_location("forex_short_side_readiness_v1", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def signal(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "pair": "EURUSD",
        "action": "sell",
        "entry_price": 1.1000,
        "stop_loss": 1.1010,
        "take_profit": 1.0990,
        "spread_pips": 1.0,
        "slippage_pips": 0.2,
        "sizing_model": "fixed_fractional",
        "evidence_replay_ok": True,
        "position_size_units": 1000,
        "risk_percent": 0.5,
        "paper_only": True,
    }
    payload.update(overrides)
    return payload


def account() -> dict[str, object]:
    return {"short_permission": True}


def limits() -> dict[str, object]:
    return {"max_spread_pips": 2.0, "max_slippage_pips": 1.0, "max_pair_risk_percent": 1.0}


def evaluate(payload: dict[str, object] | None = None, **kwargs: object) -> dict[str, object]:
    module = load_module()
    options: dict[str, object] = {
        "account_snapshot": account(),
        "limits": limits(),
    }
    options.update(kwargs)
    return module.evaluate_short_readiness(payload if payload is not None else signal(), **options)


def test_short_module_imports_and_valid_review_remains_paper_only() -> None:
    module = load_module()
    assert module.FOREX_SHORT_SIDE_READINESS_V1 == "FOREX_SHORT_SIDE_READINESS_V1"

    result = evaluate(signal(action="short"))
    assert result["allowed"] is True
    assert result["mode"] == "PAPER_ONLY"
    assert result["paper_only"] is True
    assert result["short_readiness"]["live_readiness"] is False


def test_sell_or_short_action_and_broker_permission_are_required() -> None:
    assert evaluate(signal(action="buy"))["blocked_reason"] == "short_action_required"
    assert evaluate(signal(), account_snapshot={})["blocked_reason"] == "broker_short_permission_missing"


def test_short_stop_loss_and_take_profit_direction_are_enforced() -> None:
    assert evaluate(signal(stop_loss=1.0995))["blocked_reason"] == "short_stop_loss_not_above_entry"
    assert evaluate(signal(take_profit=1.1005))["blocked_reason"] == "short_take_profit_not_below_entry"


def test_short_spread_slippage_evidence_and_sizing_guards() -> None:
    assert evaluate(signal(spread_pips=3.0))["blocked_reason"] == "short_spread_guard_violated"
    assert evaluate(signal(slippage_pips=2.0))["blocked_reason"] == "short_slippage_guard_violated"
    assert evaluate(signal(evidence_replay_ok=False))["blocked_reason"] == "short_evidence_replay_missing"
    assert evaluate(signal(sizing_model="martingale"))["blocked_reason"] == "forbidden_short_sizing_model"
    assert evaluate(signal(is_revenge=True))["blocked_reason"] == "forbidden_short_sizing_model"


def test_live_short_execution_is_blocked_without_owner_short_gate() -> None:
    result = evaluate(signal(request_short_live_execution=True))
    assert result["allowed"] is False
    assert result["blocked_reason"] == "owner_approval_required_for_short_live_execution"


def test_short_safety_flags_keep_runtime_permissions_false() -> None:
    result = evaluate(signal(), scheduler_enabled=True, daemon_enabled=True, webhook_enabled=True)
    safety = result["safety"]
    assert safety["broker_integration"] is False
    assert safety["live_short_execution"] is False
    assert safety["scheduler_allowed"] is False
    assert safety["daemon_allowed"] is False
    assert safety["webhook_allowed"] is False

    blocked = evaluate(signal(), live_execution=True)
    assert blocked["allowed"] is False
    assert blocked["safety"]["broker_integration"] is False
    assert blocked["safety"]["live_short_execution"] is False


def test_short_source_has_no_forbidden_runtime_tokens() -> None:
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
