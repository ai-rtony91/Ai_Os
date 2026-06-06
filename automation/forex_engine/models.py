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


class SetupGrade:
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    F = "F"


class ConfidenceBand:
    HIGH_QUALITY = "HIGH_QUALITY"
    TRADE_CANDIDATE = "TRADE_CANDIDATE"
    WATCHLIST = "WATCHLIST"
    BLOCKED = "BLOCKED"


@dataclass
class ConfidenceComponent:
    name: str
    score_delta: int
    reason: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SetupQualityAssessment:
    mode: str
    symbol: str
    timeframe: str
    direction: str
    score: int
    grade: str
    band: str
    allowed: bool
    reduced_risk: bool
    blocked_reason: Optional[str]
    components: List[ConfidenceComponent] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class StrategyStatus:
    RESEARCH_CANDIDATE = "RESEARCH_CANDIDATE"
    WATCHLIST = "WATCHLIST"
    REJECTED = "REJECTED"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


@dataclass
class OptimizationCandidate:
    name: str
    reason: str
    priority: str
    suggested_direction: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StrategyScoreComponent:
    name: str
    score_delta: int
    reason: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StrategyScorecard:
    mode: str
    strategy_name: str
    symbol: str
    timeframe: str
    score: float
    status: str
    rank: int
    trades: int
    wins: int
    losses: int
    win_rate_pct: float
    profit_factor: Optional[float]
    net_pnl_usd: float
    max_drawdown_usd: float
    max_drawdown_pct: float
    starting_balance_usd: float
    ending_balance_usd: float
    components: List[StrategyScoreComponent] = field(default_factory=list)
    optimization_candidates: List[OptimizationCandidate] = field(default_factory=list)
    summary_note: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StrategyComparisonResult:
    mode: str
    compared_at: str
    strategy_count: int
    scorecards: List[StrategyScorecard] = field(default_factory=list)
    top_strategy: Optional[str] = None
    rejected_count: int = 0
    watchlist_count: int = 0
    research_candidate_count: int = 0
    insufficient_data_count: int = 0
    summary_note: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


class WalkForwardStatus:
    PASSED = "PASSED"
    DEGRADED = "DEGRADED"
    FAILED = "FAILED"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


@dataclass
class WalkForwardSplit:
    mode: str
    symbol: str
    timeframe: str
    train_ratio: float
    test_ratio: float
    train_count: int
    test_count: int
    train_start: str
    train_end: str
    test_start: str
    test_end: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WalkForwardWindowResult:
    mode: str
    symbol: str
    timeframe: str
    window_name: str
    candles_processed: int
    trades: int
    net_pnl_usd: float
    win_rate_pct: float
    profit_factor: Optional[float]
    max_drawdown_usd: float
    max_drawdown_pct: float
    status: str
    summary_note: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WalkForwardResult:
    mode: str
    symbol: str
    timeframe: str
    strategy_name: str
    split: WalkForwardSplit
    train_result: WalkForwardWindowResult
    test_result: WalkForwardWindowResult
    degradation_pct: Optional[float]
    status: str
    recommendations: List[str] = field(default_factory=list)
    summary_note: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


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
