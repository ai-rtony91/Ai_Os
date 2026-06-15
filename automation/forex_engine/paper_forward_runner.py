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
