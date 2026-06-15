from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any

from automation.forex_engine import schema_contracts as schemas


DEFAULT_STRATEGY_CONFIG = {
    "strategy_id": "local_close_momentum_v1",
    "units": 10000.0,
    "risk_per_trade_usd": 10.0,
    "minimum_close_move": 0.0,
    "mode": schemas.PAPER_ONLY,
}

FORBIDDEN_CONFIG_FLAGS = (
    "broker_allowed",
    "live_trading_allowed",
    "credentials_allowed",
    "secrets_allowed",
    "orders_allowed",
    "webhooks_allowed",
    "scheduler_allowed",
    "daemon_allowed",
    "network_market_automation_allowed",
    "execution_allowed",
    "live_ready",
)


def build_sample_backtest_fixture() -> schemas.MarketDataFixture:
    candles = [
        schemas.Candle("2026-06-15T09:00:00Z", 1.1000, 1.1020, 1.0990, 1.1010, 1000),
        schemas.Candle("2026-06-15T09:05:00Z", 1.1010, 1.1040, 1.1005, 1.1035, 1001),
        schemas.Candle("2026-06-15T09:10:00Z", 1.1035, 1.1045, 1.1015, 1.1020, 1002),
        schemas.Candle("2026-06-15T09:15:00Z", 1.1020, 1.1050, 1.1010, 1.1042, 1003),
        schemas.Candle("2026-06-15T09:20:00Z", 1.1042, 1.1055, 1.1025, 1.1030, 1004),
        schemas.Candle("2026-06-15T09:25:00Z", 1.1030, 1.1062, 1.1028, 1.1058, 1005),
    ]
    fixture = schemas.MarketDataFixture(
        fixture_id="fixture-local-close-momentum-v1",
        symbol="EURUSD",
        timeframe="5m",
        source="deterministic_local_fixture",
        candles=candles,
    )
    schemas.validate_market_fixture_schema(fixture)
    return fixture


def run_local_backtest_harness(
    fixture: schemas.MarketDataFixture | dict[str, Any] | None = None,
    strategy_config: dict[str, Any] | None = None,
    risk_config: dict[str, Any] | None = None,
) -> schemas.BacktestResult:
    active_fixture = _coerce_fixture(fixture or build_sample_backtest_fixture())
    schemas.validate_market_fixture_schema(active_fixture)

    config = {**DEFAULT_STRATEGY_CONFIG, **(strategy_config or {})}
    _assert_local_config(config)
    _assert_local_config(risk_config or {})
    schemas.assert_no_live_permissions(config)
    schemas.assert_no_live_permissions(risk_config or {})

    strategy_id = str(config.get("strategy_id") or DEFAULT_STRATEGY_CONFIG["strategy_id"])
    units = float(config.get("units", DEFAULT_STRATEGY_CONFIG["units"]))
    risk_per_trade_usd = float(config.get("risk_per_trade_usd", DEFAULT_STRATEGY_CONFIG["risk_per_trade_usd"]))
    minimum_close_move = float(config.get("minimum_close_move", DEFAULT_STRATEGY_CONFIG["minimum_close_move"]))
    if units <= 0:
        raise ValueError("strategy_config.units must be positive")
    if risk_per_trade_usd <= 0:
        raise ValueError("strategy_config.risk_per_trade_usd must be positive")

    candles = active_fixture.candles
    trades: list[schemas.BacktestTrade] = []
    equity = 0.0
    peak_equity = 0.0
    max_drawdown_usd = 0.0

    for index in range(1, len(candles)):
        previous = candles[index - 1]
        current = candles[index]
        direction = _direction(previous.close, current.close, minimum_close_move)
        if direction == "HOLD":
            continue
        pnl_usd = _pnl(direction, previous.close, current.close, units)
        r_multiple = round(pnl_usd / risk_per_trade_usd, 4)
        trades.append(
            schemas.BacktestTrade(
                trade_id=f"{active_fixture.fixture_id}-trade-{len(trades) + 1}",
                symbol=active_fixture.symbol,
                direction=direction,
                entry_time=previous.timestamp,
                exit_time=current.timestamp,
                entry_price=previous.close,
                exit_price=current.close,
                units=units,
                pnl_usd=round(pnl_usd, 4),
                r_multiple=r_multiple,
            )
        )
        equity += pnl_usd
        peak_equity = max(peak_equity, equity)
        max_drawdown_usd = max(max_drawdown_usd, peak_equity - equity)

    expectancy_r = round(sum(trade.r_multiple for trade in trades) / len(trades), 4) if trades else 0.0
    profit_factor = _profit_factor(trades)
    starting_balance_usd = float((risk_config or {}).get("starting_balance_usd", 1000.0))
    max_drawdown_pct = round((max_drawdown_usd / starting_balance_usd) * 100, 4) if starting_balance_usd else 0.0

    result = schemas.BacktestResult(
        result_id=f"backtest-{active_fixture.fixture_id}-{strategy_id}-{len(trades)}",
        strategy_id=strategy_id,
        fixture_id=active_fixture.fixture_id,
        total_trades=len(trades),
        expectancy_r=expectancy_r,
        profit_factor=profit_factor,
        max_drawdown_pct=max_drawdown_pct,
        trades=trades,
    )
    schemas.validate_backtest_result_schema(result)
    return result


def backtest_harness_summary(result: schemas.BacktestResult | dict[str, Any]) -> dict[str, Any]:
    payload = _payload(result)
    schemas.validate_backtest_result_schema(payload)
    return {
        "schema": "AIOS_FOREX_BUILDER_BACKTEST_HARNESS_SUMMARY.v1",
        "mode": schemas.PAPER_ONLY,
        "strategy_id": payload["strategy_id"],
        "fixture_id": payload["fixture_id"],
        "total_trades": payload["total_trades"],
        "expectancy_r": payload["expectancy_r"],
        "profit_factor": payload["profit_factor"],
        "max_drawdown_pct": payload["max_drawdown_pct"],
        "local_fixtures_only": True,
        "network_allowed": False,
        "broker_allowed": False,
        "live_ready": False,
        "next_safe_action": "Use this deterministic backtest as local evidence only; continue risk-gate review.",
    }


def _payload(value: Any) -> dict[str, Any]:
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, dict):
        return dict(value)
    raise TypeError(f"Expected dataclass or dict, got {type(value).__name__}")


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


def _assert_local_config(config: dict[str, Any]) -> None:
    for flag in FORBIDDEN_CONFIG_FLAGS:
        if config.get(flag) is True:
            raise ValueError(f"{flag} must remain false for the local backtest harness")
    if config.get("broker_order_id"):
        raise ValueError("broker_order_id must remain empty for the local backtest harness")


def _direction(previous_close: float, current_close: float, minimum_close_move: float) -> str:
    delta = current_close - previous_close
    if abs(delta) <= minimum_close_move:
        return "HOLD"
    return "BUY" if delta > 0 else "SELL"


def _pnl(direction: str, entry_price: float, exit_price: float, units: float) -> float:
    if direction == "BUY":
        return (exit_price - entry_price) * units
    if direction == "SELL":
        return (entry_price - exit_price) * units
    return 0.0


def _profit_factor(trades: list[schemas.BacktestTrade]) -> float:
    gross_profit = sum(trade.pnl_usd for trade in trades if trade.pnl_usd > 0)
    gross_loss = abs(sum(trade.pnl_usd for trade in trades if trade.pnl_usd < 0))
    if gross_loss == 0:
        return round(gross_profit, 4) if gross_profit else 0.0
    return round(gross_profit / gross_loss, 4)
