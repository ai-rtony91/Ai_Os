from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any

from automation.forex_engine import schema_contracts as schemas


def simulate_order_intent(
    intent: schemas.OrderIntent | dict[str, Any],
    fixture_or_price: schemas.MarketDataFixture | schemas.Candle | dict[str, Any] | float,
    ledger_state: list[schemas.PaperLedgerEntry | dict[str, Any]] | None = None,
) -> schemas.PaperLedgerEntry:
    active_intent = _coerce_intent(intent)
    schemas.validate_order_intent_schema(active_intent)
    schemas.assert_no_live_permissions(ledger_state or [])
    price, timestamp = _price_and_timestamp(fixture_or_price)
    if active_intent.direction in {"HOLD", "NO_TRADE"}:
        fill_price = None
        pnl_usd = 0.0
    else:
        fill_price = price
        pnl_usd = _simulated_pnl(active_intent, fill_price)

    entry = schemas.PaperLedgerEntry(
        ledger_id=f"paper-ledger-{active_intent.intent_id}",
        timestamp=timestamp,
        intent_id=active_intent.intent_id,
        simulated_fill_price=fill_price,
        simulated_pnl_usd=round(pnl_usd, 4),
    )
    schemas.validate_paper_ledger_entry_schema(entry)
    return entry


def run_paper_forward_simulation(
    intents: list[schemas.OrderIntent | dict[str, Any]],
    fixture: schemas.MarketDataFixture | dict[str, Any],
) -> list[schemas.PaperLedgerEntry]:
    active_fixture = _coerce_fixture(fixture)
    schemas.validate_market_fixture_schema(active_fixture)
    entries: list[schemas.PaperLedgerEntry] = []
    for index, intent in enumerate(intents):
        candle = active_fixture.candles[min(index, len(active_fixture.candles) - 1)]
        entries.append(simulate_order_intent(intent, candle, entries))
    return entries


def paper_forward_summary(entries: list[schemas.PaperLedgerEntry | dict[str, Any]]) -> dict[str, Any]:
    payloads = [_payload(entry) for entry in entries]
    for payload in payloads:
        schemas.validate_paper_ledger_entry_schema(payload)
    total_pnl = round(sum(float(entry.get("simulated_pnl_usd") or 0.0) for entry in payloads), 4)
    return {
        "schema": "AIOS_FOREX_BUILDER_PAPER_FORWARD_SUMMARY.v1",
        "mode": schemas.PAPER_ONLY,
        "status": schemas.SIMULATED_ONLY,
        "classification": "PAPER_FORWARD_READY" if payloads else "WATCHLIST",
        "total_entries": len(payloads),
        "total_simulated_pnl_usd": total_pnl,
        "broker_order_ids": [],
        "live_orders": False,
        "execution_allowed": False,
        "local_simulation_only": True,
        "next_safe_action": "Use local simulated ledger evidence only; no broker paper orders.",
    }


def _payload(value: Any) -> dict[str, Any]:
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, dict):
        return dict(value)
    raise TypeError(f"Expected dataclass or dict, got {type(value).__name__}")


def _coerce_intent(value: schemas.OrderIntent | dict[str, Any]) -> schemas.OrderIntent:
    if isinstance(value, schemas.OrderIntent):
        return value
    payload = _payload(value)
    return schemas.OrderIntent(
        intent_id=str(payload["intent_id"]),
        signal_id=str(payload["signal_id"]),
        symbol=str(payload["symbol"]),
        direction=str(payload["direction"]),
        requested_units=float(payload["requested_units"]),
        entry_reference_price=float(payload["entry_reference_price"]),
        stop_loss_reference_price=payload.get("stop_loss_reference_price"),
        take_profit_reference_price=payload.get("take_profit_reference_price"),
        status=str(payload.get("status", schemas.INTENT_ONLY)),
        broker_order_id=payload.get("broker_order_id"),
        execution_allowed=bool(payload.get("execution_allowed", False)),
    )


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


def _price_and_timestamp(value: schemas.MarketDataFixture | schemas.Candle | dict[str, Any] | float) -> tuple[float, str]:
    if isinstance(value, (int, float)):
        return float(value), "LOCAL_SIMULATION_PRICE"
    if isinstance(value, schemas.Candle):
        return float(value.close), value.timestamp
    payload = _payload(value)
    if "candles" in payload:
        fixture = _coerce_fixture(payload)
        schemas.validate_market_fixture_schema(fixture)
        candle = fixture.candles[0]
        return float(candle.close), candle.timestamp
    if "close" in payload:
        candle = schemas.Candle(**payload)
        schemas.validate_candle_schema(candle)
        return float(candle.close), candle.timestamp
    raise TypeError("fixture_or_price must be a local fixture, candle, candle dict, or numeric price")


def _simulated_pnl(intent: schemas.OrderIntent, fill_price: float) -> float:
    if intent.direction == "BUY":
        return (fill_price - intent.entry_reference_price) * intent.requested_units
    if intent.direction == "SELL":
        return (intent.entry_reference_price - fill_price) * intent.requested_units
    return 0.0
