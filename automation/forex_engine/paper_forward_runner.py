from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any

from automation.forex_engine import local_fixture_catalog
from automation.forex_engine import paper_forward_simulator
from automation.forex_engine import schema_contracts as schemas


DEFAULT_STRATEGY_ID = "supertrend_pullback_v1"
DEFAULT_FIXTURE_ID = "EURUSD_5M_PULLBACK_SAMPLE"
DEFAULT_STARTING_BALANCE = 500.0
DEFAULT_UNITS = 1000.0
ALLOWED_LOCAL_CLASSIFICATIONS = {"FAIL", "WATCHLIST", "PAPER_FORWARD_READY"}


def run_paper_forward_demo_bundle(fixture_id: str = DEFAULT_FIXTURE_ID) -> dict[str, Any]:
    fixture = local_fixture_catalog.get_fixture_by_id(fixture_id)
    return run_local_paper_forward_session(
        fixture=fixture,
        strategy_id=DEFAULT_STRATEGY_ID,
        starting_balance=DEFAULT_STARTING_BALANCE,
    )


def build_demo_order_intents(
    fixture: schemas.MarketDataFixture | dict[str, Any],
    strategy_id: str = DEFAULT_STRATEGY_ID,
    units: float = DEFAULT_UNITS,
) -> list[schemas.OrderIntent]:
    active_fixture = _coerce_fixture(fixture)
    schemas.validate_market_fixture_schema(active_fixture)
    if units <= 0:
        raise ValueError("units must be positive for local paper-forward intent generation")

    intents: list[schemas.OrderIntent] = []
    for index in range(1, len(active_fixture.candles)):
        previous = active_fixture.candles[index - 1]
        current = active_fixture.candles[index]
        direction = _direction(previous.close, current.close)
        if direction == "HOLD":
            continue
        intent = schemas.OrderIntent(
            intent_id=f"{active_fixture.fixture_id}-intent-{len(intents) + 1}",
            signal_id=f"{active_fixture.fixture_id}-signal-{index}",
            symbol=active_fixture.symbol,
            direction=direction,
            requested_units=units,
            entry_reference_price=previous.close,
            stop_loss_reference_price=_stop_reference(direction, previous.close),
            take_profit_reference_price=_target_reference(direction, previous.close),
            status=schemas.INTENT_ONLY,
            broker_order_id=None,
            execution_allowed=False,
        )
        schemas.validate_order_intent_schema(intent)
        intents.append(intent)
    return intents


def run_local_paper_forward_session(
    fixture: schemas.MarketDataFixture | dict[str, Any],
    strategy_id: str,
    starting_balance: float = DEFAULT_STARTING_BALANCE,
) -> dict[str, Any]:
    active_fixture = _coerce_fixture(fixture)
    schemas.validate_market_fixture_schema(active_fixture)
    if starting_balance <= 0:
        raise ValueError("starting_balance must be positive for local paper-forward simulation")

    intents = build_demo_order_intents(active_fixture, strategy_id)
    entries: list[schemas.PaperLedgerEntry] = []
    for index, intent in enumerate(intents):
        entries.append(
            paper_forward_simulator.simulate_order_intent(
                intent,
                active_fixture.candles[index + 1],
                entries,
            )
        )
    summary = paper_forward_simulator.paper_forward_summary(entries)
    total_pnl = float(summary["total_simulated_pnl_usd"])
    blockers = [] if entries else ["no_order_intents_generated"]
    summary.update(
        {
            "starting_balance_usd": round(float(starting_balance), 4),
            "ending_balance_usd": round(float(starting_balance) + total_pnl, 4),
            "blockers": blockers,
            "reports_written": False,
            "files_written": [],
        }
    )

    bundle = {
        "schema": "AIOS_FOREX_PAPER_FORWARD_DEMO_BUNDLE.v1",
        "mode": schemas.PAPER_ONLY,
        "session_mode": "LOCAL_SIMULATION_ONLY",
        "fixture_id": active_fixture.fixture_id,
        "strategy_id": strategy_id,
        "intents": [asdict(intent) for intent in intents],
        "ledger_entries": [asdict(entry) for entry in entries],
        "paper_summary": summary,
        "safety": _safety(),
        "blockers": blockers,
        "next_safe_action": _next_safe_action(bool(entries)),
        "live_ready": False,
        "reports_written": False,
        "files_written": [],
    }
    schemas.assert_no_live_permissions(bundle)
    return bundle


def run_multi_fixture_paper_forward(
    fixture_ids: list[str] | tuple[str, ...] | None = None,
    strategy_id: str = DEFAULT_STRATEGY_ID,
) -> dict[str, Any]:
    active_fixture_ids = list(fixture_ids or local_fixture_catalog.list_fixture_ids())
    per_fixture_results = []
    blockers: list[str] = []

    for fixture_id in active_fixture_ids:
        fixture = local_fixture_catalog.get_fixture_by_id(fixture_id)
        local_fixture_catalog.assert_fixture_is_local_only(fixture)
        bundle = run_local_paper_forward_session(
            fixture=fixture,
            strategy_id=strategy_id,
            starting_balance=DEFAULT_STARTING_BALANCE,
        )
        result = _per_fixture_result(bundle, fixture)
        per_fixture_results.append(result)
        blockers.extend([f"{fixture_id}:{blocker}" for blocker in result["blockers"]])

    results = {
        "schema": "AIOS_FOREX_MULTI_FIXTURE_PAPER_FORWARD.v1",
        "mode": schemas.PAPER_ONLY,
        "strategy_id": strategy_id,
        "fixture_ids": active_fixture_ids,
        "per_fixture_results": per_fixture_results,
        "safety": _safety(),
        "blockers": blockers,
        "reports_written": False,
        "files_written": [],
    }
    summary = summarize_multi_fixture_paper_forward(results)
    results.update(
        {
            "fixture_count": summary["fixture_count"],
            "summary": summary,
            "classification": summary["classification"],
            "next_safe_action": summary["next_safe_action"],
        }
    )
    schemas.assert_no_live_permissions(results)
    return results


def summarize_multi_fixture_paper_forward(results: dict[str, Any]) -> dict[str, Any]:
    per_fixture_results = list(results.get("per_fixture_results") or [])
    fixture_count = len(per_fixture_results)
    total_intents = sum(int(item.get("intent_count", 0)) for item in per_fixture_results)
    total_ledger_entries = sum(int(item.get("ledger_entry_count", 0)) for item in per_fixture_results)
    aggregate_pnl = round(sum(float(item.get("paper_pnl_usd", 0.0)) for item in per_fixture_results), 4)
    positive_fixture_count = sum(1 for item in per_fixture_results if float(item.get("paper_pnl_usd", 0.0)) > 0)
    negative_fixture_count = sum(1 for item in per_fixture_results if float(item.get("paper_pnl_usd", 0.0)) < 0)
    blocked_fixture_count = sum(1 for item in per_fixture_results if item.get("blockers"))
    eligible_fixture_count = max(1, fixture_count - blocked_fixture_count)
    consistency_pct = round((positive_fixture_count / eligible_fixture_count) * 100, 2) if fixture_count else 0.0
    blockers = _unique(
        [
            str(blocker)
            for item in per_fixture_results
            for blocker in list(item.get("blockers") or [])
        ]
        + [str(blocker) for blocker in list(results.get("blockers") or [])]
    )
    summary = {
        "schema": "AIOS_FOREX_MULTI_FIXTURE_PAPER_FORWARD_SUMMARY.v1",
        "mode": schemas.PAPER_ONLY,
        "strategy_id": results.get("strategy_id", DEFAULT_STRATEGY_ID),
        "fixture_count": fixture_count,
        "per_fixture_results": per_fixture_results,
        "total_intents": total_intents,
        "total_ledger_entries": total_ledger_entries,
        "aggregate_pnl": aggregate_pnl,
        "aggregate_pnl_usd": aggregate_pnl,
        "positive_fixture_count": positive_fixture_count,
        "negative_fixture_count": negative_fixture_count,
        "blocked_fixture_count": blocked_fixture_count,
        "consistency_pct": consistency_pct,
        "safety": _safety(),
        "blockers": blockers,
        "live_ready": False,
        "protected_gate_required": True,
    }
    summary["classification"] = classify_multi_fixture_paper_forward(summary)
    summary["next_safe_action"] = _multi_next_safe_action(summary["classification"], blockers)
    schemas.assert_no_live_permissions(summary)
    return summary


def classify_multi_fixture_paper_forward(summary: dict[str, Any]) -> str:
    payload = dict(summary)
    if payload.get("live_ready") is True or payload.get("classification") == "LIVE_READY":
        return "FAIL"
    fixture_count = int(payload.get("fixture_count", 0))
    total_ledger_entries = int(payload.get("total_ledger_entries", 0))
    blocked_fixture_count = int(payload.get("blocked_fixture_count", 0))
    consistency_pct = float(payload.get("consistency_pct", 0.0))
    blockers = list(payload.get("blockers") or [])
    if fixture_count <= 0 or total_ledger_entries <= 0:
        return "FAIL"
    if blocked_fixture_count >= fixture_count or any(str(item).startswith("forbidden_") for item in blockers):
        return "FAIL"
    if blockers:
        return "WATCHLIST"
    if consistency_pct >= 60.0 and blocked_fixture_count == 0:
        return "PAPER_FORWARD_READY"
    return "WATCHLIST"


def calculate_regime_consistency(per_fixture_results: list[dict[str, Any]]) -> dict[str, Any]:
    regimes: dict[str, dict[str, Any]] = {}
    for item in per_fixture_results:
        regime = str(item.get("regime") or "unknown")
        regime_item = regimes.setdefault(
            regime,
            {
                "fixture_count": 0,
                "aggregate_pnl": 0.0,
                "fixture_ids": [],
                "blockers": [],
            },
        )
        regime_item["fixture_count"] += 1
        regime_item["aggregate_pnl"] = round(
            float(regime_item["aggregate_pnl"]) + float(item.get("paper_pnl_usd", 0.0)),
            4,
        )
        regime_item["fixture_ids"].append(str(item.get("fixture_id")))
        regime_item["blockers"].extend([str(blocker) for blocker in list(item.get("blockers") or [])])

    total_regimes = len(regimes)
    positive_regimes = sum(1 for item in regimes.values() if float(item["aggregate_pnl"]) > 0)
    negative_regimes = sum(1 for item in regimes.values() if float(item["aggregate_pnl"]) < 0)
    neutral_regimes = total_regimes - positive_regimes - negative_regimes
    consistent_regimes_pct = round((positive_regimes / total_regimes) * 100, 2) if total_regimes else 0.0
    ranked = sorted(
        (
            {"regime": regime, "aggregate_pnl": float(item["aggregate_pnl"]), "fixture_count": item["fixture_count"]}
            for regime, item in regimes.items()
        ),
        key=lambda item: item["aggregate_pnl"],
    )
    blockers = _unique(
        [
            f"{regime}:{blocker}"
            for regime, item in regimes.items()
            for blocker in list(item.get("blockers") or [])
        ]
    )
    result = {
        "schema": "AIOS_FOREX_REGIME_CONSISTENCY_SCORE.v1",
        "total_regimes": total_regimes,
        "positive_regimes": positive_regimes,
        "negative_regimes": negative_regimes,
        "neutral_regimes": neutral_regimes,
        "consistent_regimes_pct": consistent_regimes_pct,
        "weakest_regime": ranked[0] if ranked else None,
        "strongest_regime": ranked[-1] if ranked else None,
        "regimes": regimes,
        "blockers": blockers,
        "live_ready": False,
    }
    result["classification"] = _classify_regime_consistency(result)
    schemas.assert_no_live_permissions(result)
    return result


def paper_forward_demo_lines(bundle: dict[str, Any]) -> list[str]:
    summary = dict(bundle["paper_summary"])
    return [
        "AIOS Forex Paper-Forward Demo",
        f"Mode: {bundle['mode']}",
        f"Fixture: {bundle['fixture_id']}",
        f"Strategy: {bundle['strategy_id']}",
        f"Intents: {len(bundle['intents'])}",
        f"Simulated ledger entries: {len(bundle['ledger_entries'])}",
        f"Paper PnL: {summary['total_simulated_pnl_usd']}",
        f"Risk classification: {summary['classification']}",
        "Live ready: false",
        f"Next safe action: {bundle['next_safe_action']}",
        "Safety: no broker/API/network/live execution.",
    ]


def _coerce_fixture(value: schemas.MarketDataFixture | dict[str, Any]) -> schemas.MarketDataFixture:
    if isinstance(value, schemas.MarketDataFixture):
        return value
    payload = _payload(value)
    candles = [
        candle if isinstance(candle, schemas.Candle) else schemas.Candle(**dict(candle))
        for candle in payload.get("candles", [])
    ]
    return schemas.MarketDataFixture(
        fixture_id=str(payload["fixture_id"]),
        symbol=str(payload["symbol"]),
        timeframe=str(payload["timeframe"]),
        source=str(payload["source"]),
        candles=candles,
        mode=str(payload.get("mode", schemas.LOCAL_ONLY)),
        network_allowed=bool(payload.get("network_allowed", False)),
    )


def _payload(value: Any) -> dict[str, Any]:
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, dict):
        return dict(value)
    raise TypeError(f"Expected dataclass or dict, got {type(value).__name__}")


def _direction(previous_close: float, current_close: float) -> str:
    if current_close > previous_close:
        return "BUY"
    if current_close < previous_close:
        return "SELL"
    return "HOLD"


def _stop_reference(direction: str, reference_price: float) -> float:
    offset = 0.0010
    return round(reference_price - offset, 5) if direction == "BUY" else round(reference_price + offset, 5)


def _target_reference(direction: str, reference_price: float) -> float:
    offset = 0.0015
    return round(reference_price + offset, 5) if direction == "BUY" else round(reference_price - offset, 5)


def _per_fixture_result(bundle: dict[str, Any], fixture: schemas.MarketDataFixture) -> dict[str, Any]:
    paper_summary = dict(bundle.get("paper_summary") or {})
    ledger_entries = list(bundle.get("ledger_entries") or [])
    intents = list(bundle.get("intents") or [])
    blockers = list(bundle.get("blockers") or paper_summary.get("blockers") or [])
    result = {
        "fixture_id": fixture.fixture_id,
        "symbol": fixture.symbol,
        "timeframe": fixture.timeframe,
        "regime": local_fixture_catalog.fixture_regime(fixture.fixture_id),
        "intent_count": len(intents),
        "ledger_entry_count": len(ledger_entries),
        "paper_summary": paper_summary,
        "paper_pnl_usd": float(paper_summary.get("total_simulated_pnl_usd", 0.0)),
        "classification": paper_summary.get("classification", "WATCHLIST"),
        "blockers": blockers,
        "broker_order_ids": [entry.get("broker_order_id") for entry in ledger_entries],
        "live_orders": [bool(entry.get("live_order")) for entry in ledger_entries],
        "live_ready": False,
        "safety": _safety(),
    }
    schemas.assert_no_live_permissions(result)
    return result


def _classify_regime_consistency(result: dict[str, Any]) -> str:
    if result.get("live_ready") is True or result.get("classification") == "LIVE_READY":
        return "FAIL"
    total_regimes = int(result.get("total_regimes", 0))
    positive_regimes = int(result.get("positive_regimes", 0))
    consistent_pct = float(result.get("consistent_regimes_pct", 0.0))
    blockers = list(result.get("blockers") or [])
    if total_regimes <= 0:
        return "FAIL"
    if blockers:
        return "WATCHLIST"
    if positive_regimes >= max(1, total_regimes // 2) and consistent_pct >= 60.0:
        return "PAPER_FORWARD_READY"
    return "WATCHLIST"


def _unique(items: list[str]) -> list[str]:
    unique: list[str] = []
    for item in items:
        if item and item not in unique:
            unique.append(item)
    return unique


def _multi_next_safe_action(classification: str, blockers: list[str]) -> str:
    if classification == "PAPER_FORWARD_READY":
        return "Use V2 evidence for local risk-governor threshold hardening; live and broker paths remain blocked."
    if blockers:
        return "Resolve multi-fixture paper-forward blockers before claiming V2 local readiness."
    return "Run more local out-of-sample fixtures before any protected downstream gate."


def _safety() -> dict[str, Any]:
    return {
        "local_simulation_only": True,
        "broker_allowed": False,
        "broker_order_id": None,
        "broker_paper_orders": False,
        "network_allowed": False,
        "api_ingestion": False,
        "credentials_allowed": False,
        "secrets_allowed": False,
        "live_trading": False,
        "live_ready": False,
        "live_order": False,
        "execution_allowed": False,
        "orders_allowed": False,
        "webhooks_allowed": False,
        "scheduler_allowed": False,
        "daemon_allowed": False,
        "reports_written": False,
        "files_written": [],
    }


def _next_safe_action(has_entries: bool) -> str:
    if has_entries:
        return "Build a local evidence bundle from this simulated ledger; keep broker and live trading blocked."
    return "Repair local fixture or strategy intent generation before claiming paper-forward evidence."
