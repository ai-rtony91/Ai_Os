"""JSON-serializable trader event records."""

from __future__ import annotations

from dataclasses import asdict, dataclass


VALID_DIRECTIONS = {"BUY_REVIEW", "SELL_REVIEW", "HOLD", "BLOCKED"}
VALID_PERMISSIONS = {"bullish", "bearish", "neutral", "blocked"}


def _check_direction(direction: str) -> None:
    if direction not in VALID_DIRECTIONS:
        raise ValueError(f"Unsupported direction: {direction}")


def _check_permission(permission: str) -> None:
    if permission not in VALID_PERMISSIONS:
        raise ValueError(f"Unsupported permission: {permission}")


@dataclass
class MarketBar:
    symbol: str
    timeframe: str
    timestamp: str
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass
class SignalEvent:
    symbol: str
    timeframe: str
    timestamp: str
    direction: str
    quantity: int = 1
    reason: str = "strategy_review"

    def __post_init__(self) -> None:
        _check_direction(self.direction)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass
class PermissionEvent:
    symbol: str
    timeframe: str
    timestamp: str
    permission: str
    reason: str = "permission_filter"

    def __post_init__(self) -> None:
        _check_permission(self.permission)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass
class RiskDecisionEvent:
    symbol: str
    timeframe: str
    timestamp: str
    approved: bool
    direction: str
    quantity: int
    reason: str
    paper_only: bool = True

    def __post_init__(self) -> None:
        _check_direction(self.direction)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass
class PaperOrderIntent:
    symbol: str
    timeframe: str
    timestamp: str
    direction: str
    quantity: int
    limit_price: float
    paper_order_id: str
    paper_only: bool = True
    live_execution_status: str = "BLOCKED"
    external_routing_enabled: bool = False

    def __post_init__(self) -> None:
        _check_direction(self.direction)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass
class PaperFillEvent:
    symbol: str
    timeframe: str
    timestamp: str
    direction: str
    quantity: int
    fill_price: float
    paper_order_id: str
    paper_fill_id: str
    paper_only: bool = True

    def __post_init__(self) -> None:
        _check_direction(self.direction)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass
class TraderDecisionEvent:
    symbol: str
    timeframe: str
    timestamp: str
    decision: str
    signal: dict[str, object] | None = None
    permission: dict[str, object] | None = None
    risk: dict[str, object] | None = None
    paper_order: dict[str, object] | None = None
    paper_fill: dict[str, object] | None = None
    paper_outcome: dict[str, object] | None = None
    reason: str = ""
    paper_only: bool = True
    live_execution_status: str = "BLOCKED"

    def __post_init__(self) -> None:
        _check_direction(self.decision)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
