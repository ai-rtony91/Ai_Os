from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from typing import Any


PAPER_ONLY = "PAPER_ONLY"
LOCAL_ONLY = "LOCAL_ONLY"
INTENT_ONLY = "INTENT_ONLY"
SIMULATED_ONLY = "SIMULATED_ONLY"

VALID_MODES = {PAPER_ONLY, LOCAL_ONLY}
VALID_DIRECTIONS = {"BUY", "SELL", "HOLD", "NO_TRADE"}
VALID_RISK_CLASSIFICATIONS = {"FAIL", "WATCHLIST", "PAPER_FORWARD_READY"}
VALID_REPORT_CLASSIFICATIONS = {"REJECTED", "NEEDS_MORE_DATA", "CANDIDATE", "PAPER_FORWARD_READY"}

PROTECTED_BOUNDARIES = [
    "no broker integration",
    "no OANDA/live exchange integration",
    "no live orders",
    "no paper order execution unless separately approved later",
    "no credentials/secrets/env reads/writes",
    "no webhooks",
    "no scheduler/daemon execution",
    "no real-money trading",
    "no account mutation",
    "no network market automation",
]


@dataclass(frozen=True)
class Candle:
    timestamp: str
    open: float
    high: float
    low: float
    close: float
    volume: float | None = None
    source: str = "local fixture"


@dataclass(frozen=True)
class MarketDataFixture:
    fixture_id: str
    symbol: str
    timeframe: str
    source: str
    candles: list[Candle]
    mode: str = LOCAL_ONLY
    network_allowed: bool = False


@dataclass(frozen=True)
class StrategySignal:
    signal_id: str
    strategy_id: str
    symbol: str
    timeframe: str
    timestamp: str
    direction: str
    confidence: float
    reason: str
    mode: str = PAPER_ONLY


@dataclass(frozen=True)
class OrderIntent:
    intent_id: str
    signal_id: str
    symbol: str
    direction: str
    requested_units: float
    entry_reference_price: float
    stop_loss_reference_price: float | None = None
    take_profit_reference_price: float | None = None
    status: str = INTENT_ONLY
    broker_order_id: str | None = None
    execution_allowed: bool = False


@dataclass(frozen=True)
class BacktestTrade:
    trade_id: str
    symbol: str
    direction: str
    entry_time: str
    exit_time: str
    entry_price: float
    exit_price: float
    units: float
    pnl_usd: float
    r_multiple: float
    mode: str = PAPER_ONLY


@dataclass(frozen=True)
class BacktestResult:
    result_id: str
    strategy_id: str
    fixture_id: str
    total_trades: int
    expectancy_r: float
    profit_factor: float
    max_drawdown_pct: float
    trades: list[BacktestTrade] = field(default_factory=list)
    mode: str = PAPER_ONLY


@dataclass(frozen=True)
class WalkForwardWindow:
    window_id: str
    train_start: str
    train_end: str
    test_start: str
    test_end: str
    result: BacktestResult
    classification: str


@dataclass(frozen=True)
class WalkForwardSummary:
    summary_id: str
    strategy_id: str
    windows: list[WalkForwardWindow]
    consistent_windows_pct: float
    classification: str
    blockers: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class RiskGateResult:
    gate_id: str
    classification: str
    blockers: list[str]
    next_safe_action: str
    live_ready: bool = False


@dataclass(frozen=True)
class PaperLedgerEntry:
    ledger_id: str
    timestamp: str
    intent_id: str
    simulated_fill_price: float | None = None
    simulated_pnl_usd: float | None = None
    status: str = SIMULATED_ONLY
    broker_order_id: str | None = None
    live_order: bool = False


@dataclass(frozen=True)
class DashboardState:
    current_phase: str
    selected_strategy: str
    data_fixture_status: str
    backtest_status: str
    walk_forward_status: str
    risk_gate_status: str
    paper_permission_state: str
    live_permission_state: str
    current_blocker: str
    sos_required: bool
    next_safe_action: str


@dataclass(frozen=True)
class DailyEdgeReport:
    report_id: str
    timestamp: str
    strategy_id: str
    symbols: list[str]
    timeframe: str
    data_source: str
    total_trades: int
    expectancy_r: float
    max_drawdown_pct: float
    profit_factor: float
    classification: str
    blockers: list[str]
    next_safe_action: str
    mode: str = PAPER_ONLY


def _payload(value: Any) -> dict[str, Any]:
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, dict):
        return dict(value)
    raise TypeError(f"Schema payload must be a dataclass or dict, got {type(value).__name__}")


def _require(payload: dict[str, Any], fields: list[str]) -> None:
    missing = [field_name for field_name in fields if field_name not in payload or payload[field_name] in (None, "")]
    if missing:
        raise ValueError(f"Missing required schema fields: {', '.join(missing)}")


def _require_mode(payload: dict[str, Any], *, allowed: set[str] = VALID_MODES) -> None:
    mode = payload.get("mode")
    if mode not in allowed:
        raise ValueError(f"Mode must stay local and non-live: {sorted(allowed)}")


def _require_direction(direction: Any) -> None:
    if direction not in VALID_DIRECTIONS:
        raise ValueError(f"Direction must be one of {sorted(VALID_DIRECTIONS)}")


def _require_classification(classification: Any, allowed: set[str]) -> None:
    if classification not in allowed:
        raise ValueError(f"Classification must be one of {sorted(allowed)}")


def _walk_values(value: Any) -> list[Any]:
    values = [value]
    if is_dataclass(value):
        value = asdict(value)
    if isinstance(value, dict):
        for nested in value.values():
            values.extend(_walk_values(nested))
    elif isinstance(value, list):
        for nested in value:
            values.extend(_walk_values(nested))
    return values


def assert_no_live_permissions(payload: Any) -> bool:
    for value in _walk_values(payload):
        if not isinstance(value, dict):
            continue
        if value.get("live_ready") is True:
            raise ValueError("live_ready must always remain false")
        if value.get("execution_allowed") is True:
            raise ValueError("execution_allowed must remain false")
        if value.get("broker_order_id") not in (None, ""):
            raise ValueError("broker_order_id must remain empty")
        if value.get("live_order") is True:
            raise ValueError("live_order must remain false")
        if value.get("network_allowed") is True:
            raise ValueError("network_allowed must remain false")
    return True


def validate_candle_schema(candle: Candle | dict[str, Any]) -> bool:
    payload = _payload(candle)
    _require(payload, ["timestamp", "open", "high", "low", "close", "source"])
    if payload["high"] < payload["low"]:
        raise ValueError("Candle high must be greater than or equal to low")
    for field_name in ("open", "close"):
        if not payload["low"] <= payload[field_name] <= payload["high"]:
            raise ValueError(f"Candle {field_name} must be contained by high/low")
    assert_no_live_permissions(payload)
    return True


def validate_market_fixture_schema(fixture: MarketDataFixture | dict[str, Any]) -> bool:
    payload = _payload(fixture)
    _require(payload, ["fixture_id", "symbol", "timeframe", "source", "candles", "mode", "network_allowed"])
    _require_mode(payload)
    if payload["network_allowed"] is not False:
        raise ValueError("MarketDataFixture.network_allowed must be false")
    if not payload["candles"]:
        raise ValueError("MarketDataFixture.candles must not be empty")
    for candle in payload["candles"]:
        validate_candle_schema(candle)
    assert_no_live_permissions(payload)
    return True


def validate_strategy_signal_schema(signal: StrategySignal | dict[str, Any]) -> bool:
    payload = _payload(signal)
    _require(
        payload,
        ["signal_id", "strategy_id", "symbol", "timeframe", "timestamp", "direction", "confidence", "reason", "mode"],
    )
    _require_mode(payload, allowed={PAPER_ONLY})
    _require_direction(payload["direction"])
    if not 0 <= payload["confidence"] <= 1:
        raise ValueError("StrategySignal.confidence must be between 0 and 1")
    assert_no_live_permissions(payload)
    return True


def validate_order_intent_schema(intent: OrderIntent | dict[str, Any]) -> bool:
    payload = _payload(intent)
    _require(payload, ["intent_id", "signal_id", "symbol", "direction", "requested_units", "entry_reference_price", "status"])
    _require_direction(payload["direction"])
    if payload["status"] != INTENT_ONLY:
        raise ValueError("OrderIntent.status must be INTENT_ONLY")
    if payload.get("execution_allowed") is not False:
        raise ValueError("OrderIntent.execution_allowed must be false")
    assert_no_live_permissions(payload)
    return True


def validate_backtest_trade_schema(trade: BacktestTrade | dict[str, Any]) -> bool:
    payload = _payload(trade)
    _require(
        payload,
        ["trade_id", "symbol", "direction", "entry_time", "exit_time", "entry_price", "exit_price", "units", "pnl_usd", "r_multiple", "mode"],
    )
    _require_mode(payload, allowed={PAPER_ONLY})
    _require_direction(payload["direction"])
    assert_no_live_permissions(payload)
    return True


def validate_backtest_result_schema(result: BacktestResult | dict[str, Any]) -> bool:
    payload = _payload(result)
    _require(
        payload,
        ["result_id", "strategy_id", "fixture_id", "total_trades", "expectancy_r", "profit_factor", "max_drawdown_pct", "trades", "mode"],
    )
    _require_mode(payload, allowed={PAPER_ONLY})
    if payload["total_trades"] != len(payload["trades"]):
        raise ValueError("BacktestResult.total_trades must match trades length")
    for trade in payload["trades"]:
        validate_backtest_trade_schema(trade)
    assert_no_live_permissions(payload)
    return True


def validate_walk_forward_window_schema(window: WalkForwardWindow | dict[str, Any]) -> bool:
    payload = _payload(window)
    _require(payload, ["window_id", "train_start", "train_end", "test_start", "test_end", "result", "classification"])
    _require_classification(payload["classification"], VALID_RISK_CLASSIFICATIONS)
    validate_backtest_result_schema(payload["result"])
    assert_no_live_permissions(payload)
    return True


def validate_walk_forward_summary_schema(summary: WalkForwardSummary | dict[str, Any]) -> bool:
    payload = _payload(summary)
    _require(payload, ["summary_id", "strategy_id", "windows", "consistent_windows_pct", "classification", "blockers"])
    _require_classification(payload["classification"], VALID_RISK_CLASSIFICATIONS)
    if not 0 <= payload["consistent_windows_pct"] <= 100:
        raise ValueError("WalkForwardSummary.consistent_windows_pct must be between 0 and 100")
    for window in payload["windows"]:
        validate_walk_forward_window_schema(window)
    assert_no_live_permissions(payload)
    return True


def validate_risk_gate_schema(gate: RiskGateResult | dict[str, Any]) -> bool:
    payload = _payload(gate)
    _require(payload, ["gate_id", "classification", "live_ready", "blockers", "next_safe_action"])
    _require_classification(payload["classification"], VALID_RISK_CLASSIFICATIONS)
    if payload["live_ready"] is not False:
        raise ValueError("RiskGateResult.live_ready must always be false")
    assert_no_live_permissions(payload)
    return True


def validate_paper_ledger_entry_schema(entry: PaperLedgerEntry | dict[str, Any]) -> bool:
    payload = _payload(entry)
    _require(payload, ["ledger_id", "timestamp", "intent_id", "status", "live_order"])
    if payload["status"] != SIMULATED_ONLY:
        raise ValueError("PaperLedgerEntry.status must be SIMULATED_ONLY")
    if payload["live_order"] is not False:
        raise ValueError("PaperLedgerEntry.live_order must be false")
    assert_no_live_permissions(payload)
    return True


def validate_dashboard_state_schema(state: DashboardState | dict[str, Any]) -> bool:
    payload = _payload(state)
    _require(
        payload,
        [
            "current_phase",
            "selected_strategy",
            "data_fixture_status",
            "backtest_status",
            "walk_forward_status",
            "risk_gate_status",
            "paper_permission_state",
            "live_permission_state",
            "current_blocker",
            "sos_required",
            "next_safe_action",
        ],
    )
    if str(payload["live_permission_state"]).upper() in {"APPROVED", "LIVE_READY", "ENABLED"}:
        raise ValueError("DashboardState.live_permission_state must not grant live readiness")
    assert_no_live_permissions(payload)
    return True


def validate_daily_edge_report_schema(report: DailyEdgeReport | dict[str, Any]) -> bool:
    payload = _payload(report)
    _require(
        payload,
        [
            "report_id",
            "timestamp",
            "strategy_id",
            "symbols",
            "timeframe",
            "data_source",
            "total_trades",
            "expectancy_r",
            "max_drawdown_pct",
            "profit_factor",
            "classification",
            "blockers",
            "next_safe_action",
            "mode",
        ],
    )
    _require_mode(payload, allowed={PAPER_ONLY})
    _require_classification(payload["classification"], VALID_REPORT_CLASSIFICATIONS)
    assert_no_live_permissions(payload)
    return True


def schema_boundary_summary() -> dict[str, Any]:
    return {
        "schema": "AIOS_FOREX_BUILDER_DATA_SCHEMA_BOUNDARIES.v1",
        "mode": "PAPER_ONLY_OR_LOCAL_ONLY",
        "protected_boundaries": PROTECTED_BOUNDARIES,
        "broker_allowed": False,
        "live_trading_allowed": False,
        "credentials_allowed": False,
        "orders_allowed": False,
        "webhooks_allowed": False,
        "scheduler_allowed": False,
        "daemon_allowed": False,
        "network_market_automation_allowed": False,
    }
