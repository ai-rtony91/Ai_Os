"""Data models for the AI_OS Forex Engine v1 paper-only scaffold."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class EngineMode:
    PAPER_ONLY = "PAPER_ONLY"


class Direction:
    BUY = "BUY"
    SELL = "SELL"


class TradeStatus:
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    BLOCKED = "BLOCKED"


class TradeOutcome:
    WIN = "WIN"
    LOSS = "LOSS"
    BREAKEVEN = "BREAKEVEN"
    OPEN = "OPEN"


@dataclass
class Candle:
    symbol: str
    timeframe: str
    timestamp: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    source: str


@dataclass
class RegimeAssessment:
    symbol: str
    timeframe: str
    trend_state: str
    volatility_state: str
    candle_count: int
    lookback: int
    reason: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SignalCandidate:
    symbol: str
    timeframe: str
    direction: Optional[str]
    entry_price: float
    stop_loss: float
    take_profit: float
    strategy_name: str
    regime_trend: str
    regime_volatility: str
    confidence_hint: int
    reasons: List[str] = field(default_factory=list)
    blocked_reason: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SignalRuleResult:
    symbol: str
    timeframe: str
    mode: str
    regime: RegimeAssessment
    candidates: List[SignalCandidate] = field(default_factory=list)
    accepted_count: int = 0
    blocked_count: int = 0
    summary_note: str = ""


@dataclass
class BacktestConfig:
    symbol: str
    timeframe: str
    starting_balance_usd: float
    max_candles: Optional[int] = None
    strategy_name: str = "sprint_3_demo_strategy"
    mode: str = EngineMode.PAPER_ONLY
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BacktestTradeResult:
    trade_id: str
    symbol: str
    timeframe: str
    direction: str
    entry_price: float
    stop_loss: float
    take_profit: float
    exit_price: float
    opened_at: str
    closed_at: str
    outcome: str
    pnl_usd: float
    confidence_score: int
    close_reason: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BacktestResult:
    mode: str
    symbol: str
    timeframe: str
    strategy_name: str
    candles_processed: int
    signals_generated: int
    signals_accepted: int
    signals_blocked: int
    trades_opened: int
    trades_closed: int
    starting_balance_usd: float
    ending_balance_usd: float
    net_pnl_usd: float
    win_rate_pct: float
    profit_factor: Optional[float]
    max_drawdown_usd: float
    max_drawdown_pct: float
    results: List[BacktestTradeResult] = field(default_factory=list)
    summary_note: str = ""


@dataclass
class ForexSignal:
    symbol: str
    timeframe: str
    direction: str
    entry_price: float
    stop_loss: float
    take_profit: float
    timestamp: str
    strategy_name: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConfidenceAssessment:
    score: int
    reasons: List[str] = field(default_factory=list)
    allowed: bool = False
    blocked_reason: Optional[str] = None


@dataclass
class RiskDecision:
    allowed: bool
    risk_amount_usd: float
    max_daily_loss_usd: float
    open_trade_count: int
    max_open_trades: int
    consecutive_losses: int
    blocked_reason: Optional[str] = None


@dataclass
class PaperTrade:
    trade_id: str
    mode: str
    symbol: str
    timeframe: str
    direction: str
    entry_price: float
    stop_loss: float
    take_profit: float
    position_size_units: float
    risk_amount_usd: float
    confidence_score: int
    status: str = TradeStatus.OPEN
    opened_at: str = field(default_factory=utc_now_iso)
    closed_at: Optional[str] = None
    exit_price: Optional[float] = None
    outcome: str = TradeOutcome.OPEN
    pnl_usd: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class JournalEvent:
    event_type: str
    timestamp: str
    mode: str
    payload: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceSummary:
    starting_balance_usd: float
    current_balance_usd: float
    total_trades: int
    open_trades: int
    closed_trades: int
    wins: int
    losses: int
    breakeven: int
    win_rate_pct: float
    gross_profit_usd: float
    gross_loss_usd: float
    net_pnl_usd: float
    profit_factor: Optional[float]
    max_drawdown_usd: float
    max_drawdown_pct: float
    consecutive_losses: int
    consistency_note: str
